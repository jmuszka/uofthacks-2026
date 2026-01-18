import sys
import os

print("Testing imports...")
try:
    from enums.sort import SortBy
    print("Imported SortBy")
    from dto.search import SearchRequest
    print("Imported SearchRequest")
    from util import search_products
    print("Imported search_products")
    from mcp_agent import MCPLangGraphAgent
    print("Imported MCPLangGraphAgent")
    
    import server
    print("Imported server module successfully")
except Exception as e:
    print(f"Import Error: {e}")
    import traceback
    traceback.print_exc()
