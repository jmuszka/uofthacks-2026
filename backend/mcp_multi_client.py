"""
MCP Multi-Client Host Architecture

This module implements a "Host Pattern" for connecting to multiple MCP (Model Context Protocol)
servers simultaneously. It manages a registry of client connections, aggregates tools from all
servers, and routes tool calls to the appropriate server.

Supports:
- stdio transport (local servers via npx/command)
- SSE transport (remote HTTP servers)
- streamable_http transport (modern HTTP servers like Shopify)

Prerequisites: pip install mcp httpx-sse
"""

import asyncio
import json
import os
from contextlib import AsyncExitStack
from typing import Dict, Any, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client


class MCPMultiClient:
    """
    A host manager that connects to multiple MCP servers and provides
    a unified interface for tool discovery and execution.
    """

    def __init__(self, config_path: str):
        """
        Initialize the multi-client manager.

        Args:
            config_path: Path to the JSON configuration file containing server definitions.
        """
        self.config_path = config_path
        self.sessions: Dict[str, ClientSession] = {}
        self.exit_stack = AsyncExitStack()
        self.tool_registry: Dict[str, str] = {}  # Maps tool_name -> server_name
        self.original_tool_names: Dict[str, str] = {}  # Maps namespaced_name -> original_name

    async def connect(self) -> None:
        """
        Connects to all servers defined in the configuration file.
        
        Each server gets its own ClientSession, and all tools are registered
        in the tool_registry for routing. Handles namespace collisions by
        prefixing tool names with the server name when duplicates are detected.
        """
        # Load Config
        with open(self.config_path, 'r') as f:
            config = json.load(f)

        for server_name, server_conf in config.get('mcpServers', {}).items():
            try:
                await self._connect_to_server(server_name, server_conf)
            except Exception as e:
                print(f"Failed to connect to {server_name}: {e}")

    def _resolve_env_vars(self, value: Any) -> Any:
        """
        Recursively resolve environment variable placeholders in config values.
        Supports ${VAR_NAME} syntax.
        """
        import re
        
        if isinstance(value, str):
            # Replace ${VAR_NAME} with environment variable value
            pattern = r'\$\{([^}]+)\}'
            def replacer(match):
                var_name = match.group(1)
                return os.environ.get(var_name, match.group(0))
            return re.sub(pattern, replacer, value)
        elif isinstance(value, dict):
            return {k: self._resolve_env_vars(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._resolve_env_vars(item) for item in value]
        return value

    async def _connect_to_server(self, server_name: str, server_conf: Dict[str, Any]) -> None:
        """
        Connect to a single MCP server.

        Args:
            server_name: The name/identifier of the server.
            server_conf: Configuration dictionary for the server.
                        For stdio: requires 'command', optional 'args' and 'env'
                        For SSE: requires 'type': 'sse', 'url', optional 'headers'
                        For streamable_http: requires 'type': 'streamable_http', 'url', optional 'headers'
        """
        transport_type = server_conf.get('type', 'stdio')

        if transport_type == 'streamable_http':
            # Streamable HTTP Transport (modern HTTP servers like Shopify)
            url = server_conf['url']
            headers = self._resolve_env_vars(server_conf.get('headers', {}))
            
            streams = await self.exit_stack.enter_async_context(
                streamablehttp_client(url, headers=headers)
            )
            read_stream, write_stream, _ = streams
            
        elif transport_type == 'sse':
            # SSE Transport (for remote HTTP-based servers)
            url = server_conf['url']
            headers = self._resolve_env_vars(server_conf.get('headers', {}))
            
            transport = await self.exit_stack.enter_async_context(
                sse_client(url, headers=headers)
            )
            read_stream, write_stream = transport[0], transport[1]
            
        else:
            # Stdio Transport (for local command-based servers)
            server_params = StdioServerParameters(
                command=server_conf['command'],
                args=server_conf.get('args', []),
                env={**os.environ, **server_conf.get('env', {})}
            )
            transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read_stream, write_stream = transport[0], transport[1]

        # Create session from transport
        session = await self.exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )

        # Initialize
        await session.initialize()
        self.sessions[server_name] = session

        # Register Tools with namespace collision handling
        tools = await session.list_tools()
        for tool in tools.tools:
            self._register_tool(tool.name, server_name)

    def _register_tool(self, tool_name: str, server_name: str) -> None:
        """
        Register a tool with namespace collision handling.
        
        If a tool name already exists from another server, prefix it with the server name.

        Args:
            tool_name: The original name of the tool.
            server_name: The server this tool belongs to.
        """
        if tool_name in self.tool_registry:
            # Collision detected - need to namespace both tools
            existing_server = self.tool_registry[tool_name]
            
            # Rename the existing tool if it hasn't been renamed yet
            if tool_name not in self.original_tool_names:
                namespaced_existing = f"{existing_server}_{tool_name}"
                self.tool_registry[namespaced_existing] = existing_server
                self.original_tool_names[namespaced_existing] = tool_name
                del self.tool_registry[tool_name]
                print(f"Renamed existing tool: {tool_name} -> {namespaced_existing}")

            # Add the new tool with namespace prefix
            namespaced_name = f"{server_name}_{tool_name}"
            self.tool_registry[namespaced_name] = server_name
            self.original_tool_names[namespaced_name] = tool_name
            print(f"Loaded tool: {namespaced_name} from {server_name} (namespaced due to collision)")
        else:
            self.tool_registry[tool_name] = server_name
            print(f"Loaded tool: {tool_name} from {server_name}")

    async def get_all_tools(self) -> List[Dict[str, Any]]:
        """
        Aggregates tools from all connected servers into a format suitable for LLMs.

        Returns:
            A list of tool definitions with name, description, and input_schema.
        """
        all_tools = []
        processed_tools = set()

        for server_name, session in self.sessions.items():
            result = await session.list_tools()
            for tool in result.tools:
                # Determine the exposed name (may be namespaced)
                exposed_name = self._get_exposed_tool_name(tool.name, server_name)
                
                if exposed_name not in processed_tools:
                    # Convert MCP tool format to OpenAI/Anthropic tool format
                    all_tools.append({
                        "name": exposed_name,
                        "description": tool.description or "",
                        "input_schema": tool.inputSchema
                    })
                    processed_tools.add(exposed_name)

        return all_tools

    def _get_exposed_tool_name(self, original_name: str, server_name: str) -> str:
        """
        Get the exposed tool name, accounting for any namespacing.

        Args:
            original_name: The original tool name from the server.
            server_name: The server the tool belongs to.

        Returns:
            The name that should be exposed to the LLM.
        """
        namespaced = f"{server_name}_{original_name}"
        if namespaced in self.tool_registry:
            return namespaced
        return original_name

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Routes and executes a tool call to the correct server.

        Args:
            tool_name: The name of the tool to call (may be namespaced).
            arguments: The arguments to pass to the tool.

        Returns:
            The result from the tool execution.

        Raises:
            ValueError: If the tool is not found in any connected server.
        """
        server_name = self.tool_registry.get(tool_name)
        if not server_name:
            raise ValueError(f"Tool '{tool_name}' not found in any connected server.")

        session = self.sessions[server_name]
        
        # Get the original tool name if it was namespaced
        original_name = self.original_tool_names.get(tool_name, tool_name)
        
        result = await session.call_tool(original_name, arguments)
        return result

    async def get_resources(self, server_name: Optional[str] = None) -> Dict[str, List[Any]]:
        """
        Get resources from connected servers.

        Args:
            server_name: Optional specific server to query. If None, queries all servers.

        Returns:
            A dictionary mapping server names to their available resources.
        """
        resources = {}
        
        servers_to_query = (
            {server_name: self.sessions[server_name]} 
            if server_name and server_name in self.sessions 
            else self.sessions
        )

        for name, session in servers_to_query.items():
            try:
                result = await session.list_resources()
                resources[name] = result.resources
            except Exception as e:
                print(f"Failed to get resources from {name}: {e}")
                resources[name] = []

        return resources

    async def cleanup(self) -> None:
        """
        Gracefully close all server connections.
        """
        await self.exit_stack.aclose()
        self.sessions.clear()
        self.tool_registry.clear()
        self.original_tool_names.clear()
        print("All MCP connections closed.")

    def list_connected_servers(self) -> List[str]:
        """
        Get a list of all currently connected server names.

        Returns:
            List of server names.
        """
        return list(self.sessions.keys())

    def list_tools_by_server(self) -> Dict[str, List[str]]:
        """
        Get tools grouped by their source server.

        Returns:
            Dictionary mapping server names to lists of tool names.
        """
        tools_by_server: Dict[str, List[str]] = {}
        
        for tool_name, server_name in self.tool_registry.items():
            if server_name not in tools_by_server:
                tools_by_server[server_name] = []
            tools_by_server[server_name].append(tool_name)

        return tools_by_server


EXAMPLE_CONFIG = """
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/directory"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here"
      }
    },
    "shopify": {
      "type": "sse",
      "url": "https://discover.shopifyapps.com/global/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_ACCESS_TOKEN"
      }
    }
  }
}
"""


async def main():
    """
    Example usage of the MCPMultiClient.
    """
    config_path = "servers_config.json"
    
    # Check if config exists, if not create an example
    if not os.path.exists(config_path):
        print(f"Config file '{config_path}' not found.")
        print("Creating example configuration...")
        with open(config_path, 'w') as f:
            f.write(EXAMPLE_CONFIG.strip())
        print(f"Please edit '{config_path}' with your server configurations and run again.")
        return

    client = MCPMultiClient(config_path)
    
    try:
        print("Connecting to MCP servers...")
        await client.connect()
        
        # List connected servers
        servers = client.list_connected_servers()
        print(f"\nConnected to {len(servers)} server(s): {servers}")
        
        # Get all tools for the LLM
        tools = await client.get_all_tools()
        print(f"\nAgent has access to {len(tools)} tool(s):")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description'][:50]}...")

        # Show tools grouped by server
        print("\nTools by server:")
        tools_by_server = client.list_tools_by_server()
        for server, tool_list in tools_by_server.items():
            print(f"  {server}: {tool_list}")

        # Example tool call (commented out - uncomment and modify for your use case)
        # result = await client.call_tool("list_directory", {"path": "."})
        # print(f"\nTool result: {result}")

    except FileNotFoundError as e:
        print(f"Configuration file error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
