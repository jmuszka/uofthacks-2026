"""
LangGraph Agent with MCP Multi-Client Integration

This agent uses Google's Gemini model and has access to tools from all connected MCP servers.
It implements a ReAct-style agent loop using LangGraph.

Prerequisites:
    pip install langgraph langchain-google-genai python-dotenv mcp httpx-sse
"""

import asyncio
import os, sys
from typing import Annotated, TypedDict, Literal, Optional
from dotenv import load_dotenv


from langchain_groq import ChatGroq


from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage, BaseMessage
from langchain_core.tools import tool, StructuredTool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from mcp_multi_client import MCPMultiClient

# Load environment variables
load_dotenv()


class AgentState(TypedDict):
    """State for the agent graph."""
    messages: Annotated[list[BaseMessage], add_messages]


class MCPLangGraphAgent:
    """
    A LangGraph agent that integrates with MCP servers via the MCPMultiClient.
    """

    def __init__(self, config_path: str = "servers_config.json"):
        """
        Initialize the agent.

        Args:
            config_path: Path to the MCP servers configuration file.
        """
        self.config_path = config_path
        self.mcp_client: MCPMultiClient | None = None
        self.tools: list[StructuredTool] = []
        self.model = None
        self.graph = None

    async def initialize(self) -> None:
        """Initialize the MCP client and build the agent graph."""
        # Initialize MCP client
        self.mcp_client = MCPMultiClient(self.config_path)
        await self.mcp_client.connect()

        # Convert MCP tools to LangChain tools
        # 2. Convert MCP tools to LangChain tools
        await self._create_langchain_tools()

        # Initialize Groq (Llama 3.1 8B for speed and TPM limits)
        self.model = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0,
            max_tokens=1024,
        )
        # Bind tools to the model
        if self.tools:
            self.model = self.model.bind_tools(self.tools)

        # Build the graph
        self._build_graph()

        print(f"Agent initialized with {len(self.tools)} tools from MCP servers")



    async def _create_langchain_tools(self) -> None:
        """Convert MCP tools to LangChain StructuredTools with corrected Pydantic schemas."""
        from langchain_core.tools import StructuredTool
        import json
        
        mcp_tools = await self.mcp_client.get_all_tools()

        for mcp_tool in mcp_tools:
            tool_name = mcp_tool["name"]
            raw_description = mcp_tool["description"] or f"Tool: {tool_name}"
            input_schema = mcp_tool.get("input_schema", {})
            
            # 1. Create a Pydantic model to enforce strict types (Fixes the "missing items" error)
            args_schema, field_mapping = self._create_pydantic_model(tool_name, input_schema)

            # 2. Create the execution closure
            def create_tool_func(name: str, mapping: dict):
                async def tool_func(**kwargs) -> str:
                    """Execute the MCP tool with structured arguments."""
                    try:
                        # Re-map sanitized names back to original names (e.g. gsid -> _gsid)
                        final_args = {}
                        for k, v in kwargs.items():
                            original_key = mapping.get(k, k)
                            final_args[original_key] = v
                            
                        # Auto-inject defaults for robustness (Shopify server is strict)
                        if "context" not in final_args and "context" in input_schema.get("properties", {}):
                            final_args["context"] = "User search request"
                        
                        if "shop_ids" not in final_args and "shop_ids" in input_schema.get("properties", {}):
                            final_args["shop_ids"] = []

                        if "product_ids" not in final_args and "product_ids" in input_schema.get("properties", {}):
                            final_args["product_ids"] = []
                            
                        # Remove None values (clean up optional args)
                        final_args = {k: v for k, v in final_args.items() if v is not None}
                        
                        # Execute tool
                        result = await self.mcp_client.call_tool(name, final_args)
                        print(result)
                        
                        if result.content[0].text == "You are not authorized to use this tool":
                            print("Shopify hates you (get new token)")
                            sys.exit(1)
                        
                        # Handle result content
                        if hasattr(result, 'content') and result.content:
                            contents = []
                            for item in result.content:
                                if hasattr(item, 'text'):
                                    contents.append(item.text)
                                else:
                                    contents.append(str(item))
                            return "\n".join(contents)
                        return str(result)
                    except Exception as e:
                        return f"Error calling tool {name}: {str(e)}"
                return tool_func

            # 3. Create a StructuredTool (Gemini prefers this over simple Tools)
            langchain_tool = StructuredTool.from_function(
                func=lambda **x: None,  # Dummy sync function
                coroutine=create_tool_func(tool_name, field_mapping),
                name=tool_name,
                description=raw_description,
                args_schema=args_schema  # This applies the fix
            )
            
            self.tools.append(langchain_tool)

    def _create_pydantic_model(self, name: str, schema: dict) -> tuple:
        """
        Create a Pydantic model from JSON schema for tool arguments.
        
        Returns:
            tuple: (pydantic_model, field_mapping) where field_mapping maps
                   sanitized names back to original names.
        """
        from pydantic import BaseModel, Field, create_model
        from typing import Optional, Any, List, Dict
        import re

        properties = schema.get("properties", {})
        required = set(schema.get("required", []))

        fields = {}
        field_mapping = {}  # Maps sanitized_name -> original_name

        for prop_name, prop_schema in properties.items():
            prop_type = prop_schema.get("type", "string")
            prop_desc = prop_schema.get("description", "")

            # Sanitize field name: remove leading underscores (Pydantic doesn't allow them)
            sanitized_name = prop_name.lstrip('_')
            if sanitized_name != prop_name:
                field_mapping[sanitized_name] = prop_name
                prop_desc = f"{prop_desc} (parameter: {prop_name})"

            # Determine the Python type
            python_type = self._get_python_type(prop_schema)

            if prop_name in required:
                fields[sanitized_name] = (python_type, Field(description=prop_desc))
            else:
                fields[sanitized_name] = (Optional[python_type], Field(default=None, description=prop_desc))

        # Create and return the model
        model_name = f"{name.replace('-', '_').replace(' ', '_').title()}Args"
        model = create_model(model_name, **fields)
        return model, field_mapping

    def _get_python_type(self, prop_schema: dict):
        """
        Convert JSON schema type to Python type, properly handling arrays and objects.
        For Gemini API compatibility, we need properly typed Lists.
        """
        from typing import Any, List, Dict, Annotated
        from pydantic import Field
        
        prop_type = prop_schema.get("type", "string")
        
        if prop_type == "array":
            # Get the items type for arrays
            items_schema = prop_schema.get("items", {})
            items_type = items_schema.get("type", "string")
            
            # For arrays of objects, use List[dict] with proper annotation
            if items_type == "object":
                return List[Dict[str, Any]]
            
            # Map the items type for simple arrays
            items_type_mapping = {
                "string": str,
                "integer": int,
                "number": float,
                "boolean": bool,
            }
            item_python_type = items_type_mapping.get(items_type, str)
            return List[item_python_type]
        
        elif prop_type == "object":
            # For objects, use Dict[str, Any]
            return Dict[str, Any]
        
        else:
            # Simple types
            type_mapping = {
                "string": str,
                "integer": int,
                "number": float,
                "boolean": bool,
            }
            return type_mapping.get(prop_type, Any)

    def _build_graph(self) -> None:
        """Build the LangGraph agent graph."""
        print("Build the LangGraph agent graph.")

        # Define the agent node
        async def agent_node(state: AgentState) -> dict:
            """The agent decides what to do based on the current state."""
            import json
            import uuid
    
            print("graph.ainvoke")
            messages = state["messages"]
            response = await self.model.ainvoke(messages)
            


            return {"messages": [response]}

        # Define the should_continue function
        def should_continue(state: AgentState) -> Literal["tools", "end"]:
            """Determine if we should continue to tools or end."""
            messages = state["messages"]
            last_message = messages[-1]
            
            print()
            print()
            print()
            # print(messages[-1])
            print()
            print()
            print()

            # If the LLM made a tool call, route to tools
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "tools"
            # Otherwise, end
            return "end"

        # Create the graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("agent", agent_node)
        
        if self.tools:
            tool_node = ToolNode(self.tools)
            workflow.add_node("tools", tool_node)

            # Add edges
            workflow.add_conditional_edges(
                "agent",
                should_continue,
                {
                    "tools": "tools",
                    "end": END,
                }
            )
            workflow.add_edge("tools", "agent")
        else:
            workflow.add_edge("agent", END)

        # Set entry point
        workflow.set_entry_point("agent")

        # Compile with memory checkpointer
        memory = MemorySaver()
        self.graph = workflow.compile(checkpointer=memory)

    async def chat(self, message: str, thread_id: str = "default") -> str:
        """
        Send a message to the agent and get a response.

        Args:
            message: The user's message.
            thread_id: Thread ID for conversation memory.

        Returns:
            The agent's response.
        """
        config = {"configurable": {"thread_id": thread_id}}
        
        system_prompt = (
            "You are a helpful shopping assistant with access to Shopify's global product catalog. "
            "\n\n"
            "PROTOCOL:\n"
            "1. If the user asks for a product, usage `search_global_products`.\n"
            "2. Once you get the search results, DO NOT SEARCH AGAIN. Format the REAL results into a JSON list.\n"
            "3. DO NOT HALLUCINATE. Use ONLY the data returned by the tool. If no results, return an empty list [].\n"
            "4. The JSON list must contain objects with keys: 'title', 'price', 'description', 'url', 'id', 'image_url'.\n"
            "   - 'id' should be the product's global ID (e.g. gid://shopify/Product/...) or the ID of its first variant.\n"
            "5. Output ONLY the JSON. Do not add conversational text."
            "Use the following schema:"
            "{items: {title, price, description, url, id,}[]}"
        )
       
        print("INVOKING")
        result = await self.graph.ainvoke(
            {"messages": [SystemMessage(content=system_prompt), HumanMessage(content=message)]},
            config=config
        )
        print(result)

        # Get the last AI message
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage) and msg.content:
                return msg.content

        return "No response generated."

    async def cleanup(self) -> None:
        """Clean up resources."""
        if self.mcp_client:
            await self.mcp_client.cleanup()


async def main():
    """Main function to run the agent interactively."""
    agent = MCPLangGraphAgent("servers_config.json")

    try:
        print("Initializing agent...")
        await agent.initialize()

        print("\n" + "=" * 50)
        print("MCP LangGraph Agent Ready!")
        print("Type 'quit' or 'exit' to stop.")
        print("=" * 50 + "\n")

        thread_id = "main_conversation"

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit"]:
                    print("Goodbye!")
                    break

                print("Agent: Thinking...")
                response = await agent.chat(user_input, thread_id)
                print(f"Agent: {response}\n")

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
