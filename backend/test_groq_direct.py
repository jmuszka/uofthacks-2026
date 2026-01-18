import asyncio
import os
import uuid
from dotenv import load_dotenv
from mcp_agent import MCPLangGraphAgent

load_dotenv()

async def test_direct():
    print("Initializing agent...")
    agent = MCPLangGraphAgent("servers_config.json")
    await agent.initialize()
    
    print("\nSending simple 'hi' message...")
    try:
        # Use a fresh thread ID
        tid = f"test:{str(uuid.uuid4())}"
        res = await agent.chat("hi", thread_id=tid)
        print(f"Response: {res}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(test_direct())
