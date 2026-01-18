import asyncio
import os
import json
import re
import uuid
from dotenv import load_dotenv
from mcp_agent import MCPLangGraphAgent
from util import search_products

load_dotenv()

async def debug_response():
    print("Initializing agent...")
    agent = MCPLangGraphAgent("servers_config.json")
    await agent.initialize()
    
    query = "running shoes"
    print(f"\nSending query: '{query}'...")
    
    # Use the same logic as server.py
    try:
        # We need to simulate the util.py call which is what server.py calls
        # server.py calls: res = await search_products(agent, req.query, user_id)
        # util.py uses the injected prompt string.
        
        res = await search_products(agent, query, user_id="debug_user")
        print("\n" + "="*20 + " RAW RESPONSE " + "="*20)
        print(res)
        print("="*56 + "\n")
        
        # Test the regex logic
        print("Testing Regex Extraction...")
        data = None
        try:
            data = json.loads(res.strip())
            print("✅ Direct JSON parse successful")
        except json.JSONDecodeError:
            print("⚠️ Direct parse failed. Trying Regex...")
            match = re.search(r'\[.*\]', res, re.DOTALL)
            if match:
                json_str = match.group(0)
                print(f"Regex match found: {json_str[:50]}...")
                try:
                    data = json.loads(json_str)
                    print("✅ Regex JSON parse successful")
                except json.JSONDecodeError as e:
                    print(f"❌ Regex JSON parse failed: {e}")
                    # Try cleaning markdown
                    clean_str = json_str.replace("`", "").strip()
                    try:
                        data = json.loads(clean_str)
                        print("✅ Cleaned JSON parse successful")
                    except:
                        pass
            else:
                print("❌ No regex match for [...] found.")
                
        if data:
            print(f"Final Info: Found {len(data)} items.")
        else:
            print("FAILED TO EXTRACT DATA.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(debug_response())
