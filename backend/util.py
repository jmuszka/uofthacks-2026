#!/usr/bin/env python3
"""
Shopify Product Search CLI

A fully agentic CLI app that uses Gemini + MCP to search for products
across Shopify's global catalog.

Usage:
    python main.py
    python main.py "wireless headphones"
"""

import asyncio
import sys
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from mcp_agent import MCPLangGraphAgent


SYSTEM_PROMPT = """You are a helpful shopping assistant with access to Shopify's global product catalog.

When a user asks about a product:
1. Use the search_global_products tool to find relevant products
2. Present the results in a clear, readable format with:
   - Product name
   - Price (if available)
   - Brief description
   - Any notable features

If you need more details about a specific product, use get_global_product_details.

Be concise but helpful. Keep your response in the JSON format for easy parsing. No backticks, just raw JSON text."""


async def search_products(agent: MCPLangGraphAgent, query: str) -> str:
    """Run a single product search query through the agent."""
    print(f"[*] Searching for: {query}\n")

    return await agent.chat(query, thread_id=f"product_search:{hash(query)}")



async def interactive_mode():
    """Run in interactive mode for multiple queries."""
    agent = MCPLangGraphAgent("servers_config.json")
    
    try:
        print("[*] Initializing agent...")
        await agent.initialize()
        
        print("\n" + "=" * 60)
        print("    Shopify Product Search")
        print("=" * 60)
        print("Ask me to find any product! Type 'quit' to exit.\n")
        
        thread_id = "interactive_session"
        first_query = True
        
        while True:
            try:
                query = input("You: ").strip()
                
                if not query:
                    continue
                    
                if query.lower() in ["quit", "exit", "q"]:
                    print("\nGoodbye!")
                    break
                
                print("\n[*] Searching...\n")
                
                # Add system context on first query
                if first_query:
                    prompt = f"{SYSTEM_PROMPT}\n\nUser query: {query}"
                    first_query = False
                else:
                    prompt = query
                
                response = (await agent.chat(prompt, thread_id)).strip('`')
                print(f"Agent:\n{response}\n")
                print("-" * 40 + "\n")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
                
    finally:
        await agent.cleanup()


async def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Single query mode: python util.py "search term"
        agent = MCPLangGraphAgent("servers_config.json")
        try:
            await agent.initialize()
            query = " ".join(sys.argv[1:])
            result = await search_products(agent, query)
            print(f"\n{result}")
        finally:
            await agent.cleanup()
    else:
        # Interactive mode
        await interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())

