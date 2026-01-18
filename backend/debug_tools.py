import asyncio
import json
import os
from dotenv import load_dotenv
from mcp_agent import MCPLangGraphAgent

load_dotenv()

async def debug_tools():
    print("Initializing agent to inspect tools...")
    agent = MCPLangGraphAgent("servers_config.json")
    await agent.initialize()
    
    print(f"\nTotal Tools: {len(agent.tools)}")
    
    total_len = 0
    for t in agent.tools:
        # Approximate size of the tool definition passed to LLM
        schema = t.args_schema.model_json_schema()
        schema_str = json.dumps(schema)
        # Add description and name
        tool_def_str = f"{t.name}: {t.description} {schema_str}"
        t_len = len(tool_def_str)
        total_len += t_len
        
        print(f"\n--- TOOL: {t.name} ---")
        print(f"Description Length: {len(t.description)}")
        print(f"Schema Length: {len(schema_str)}")
        print(f"Approx Total Chars: {t_len}")
        
        if t_len > 1000:
            print(f"⚠️ SUPER LARGE TOOL DETECTED!")
            # Print a snippet of schema
            print(f"Schema snippet: {schema_str[:500]} ...")

    print(f"\nTotal Approx Characters: {total_len}")
    await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(debug_tools())
