import os
import requests
import re
from fastapi import FastAPI, HTTPException, Query, Depends
from enums.sort import SortBy
from dto.search import SearchRequest
from pydantic import BaseModel
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import asyncio
import json
from random import random
from time import sleep
from enums.sort import SortBy
from dto.search import SearchRequest
from dto.purchase import PurchaseRequest, PurchaseResponse
from util import search_products
from mcp_agent import MCPLangGraphAgent

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Agent is now initialized lazily on first request to avoid startup timeouts/crashes
    yield
    # Cleanup if initialized
    if hasattr(app.state, "agent") and app.state.agent:
        await app.state.agent.cleanup()

app = FastAPI(lifespan=lifespan)

class CheckoutRequest(BaseModel):
    variant_id: str | int
    quantity: int = 1
    store_domain: str
    access_token: str | None = None

async def get_or_initialize_agent():
    if not hasattr(app.state, "agent"):
        app.state.agent_lock = asyncio.Lock()
        app.state.agent = None

    async with app.state.agent_lock:
        if app.state.agent is None:
            print("Initializing agent (lazy)...")
            agent = MCPLangGraphAgent("servers_config.json")
            await agent.initialize()
            app.state.agent = agent
    
    return app.state.agent

# Search for items via the Shopify Catalog MCP Server
@app.post("/search")
async def search(
    req: SearchRequest,
    limit: int = Query(default=10, ge=1, le=100),
    sort_order: SortBy = Query(default=SortBy.RELEVANCE),
):
    agent = await get_or_initialize_agent()
    print(f"Searching for: {req.query}")

    try:
        res = await search_products(agent, req.query)
        print(f"Agent Response: {res}")
        
        # Clean response (sometimes LLMs add markdown)
        cleaned_res = res.strip().strip('`').replace('json\n', '')
        
        return {
            "items": json.dumps(json.loads(cleaned_res), separators=(",", ":"))
        }
    except json.JSONDecodeError:
        print(f"JSON Decode Error. Raw response: {res}")
        # Fallback: return the raw text if json fails
        return {"items": [], "raw_response": res, "error": "Failed to parse JSON"}
    except Exception as e:
        print(f"Search Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# Purchase specified items
@app.post("/purchase", response_model=PurchaseResponse)
def purchase(req: PurchaseRequest):
    res = PurchaseResponse(purchases = [])
    
    for item in req.items:
        # Mock purchasing 
        # TODO: use UCP to genuinely purchase items using a credit provider
        sleep(random())
        res.add(item, True)

    return res

def validate_token(store_domain: str, token: str) -> bool:
    """Checks if a token is valid by making a lightweight query."""
    try:
        if not store_domain.startswith("http"):
             api_url = f"https://{store_domain}/api/2025-01/graphql.json"
        else:
             api_url = f"{store_domain.rstrip('/')}/api/2025-01/graphql.json"

        query = "{ shop { name } }"
        response = requests.post(
            api_url,
            json={'query': query},
            headers={'X-Shopify-Storefront-Access-Token': token, 'Content-Type': 'application/json'},
            timeout=5
        )
        return response.status_code == 200 and 'errors' not in response.json()
    except:
        return False

def find_storefront_token(store_domain: str) -> str:
    """Attempts to scrape the storefront access token from the store's homepage."""
    print(f"🕵️ Searching for token on {store_domain}...")
    try:
        if not store_domain.startswith("http"):
            url = f"https://{store_domain}"
        else:
            url = store_domain
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        html = requests.get(url, headers=headers, timeout=10).text
        
        # Look for 32-char hex strings
        candidates = set(re.findall(r'["\']([a-f0-9]{32})["\']', html))
        
        print(f"🔎 Found {len(candidates)} candidate tokens.")
        
        for token in candidates:
            if validate_token(store_domain, token):
                print(f"✅ Found valid token: {token}")
                return token
        
        raise Exception("No valid token found in HTML candidates.")
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not auto-discover token for {store_domain}. Please provide it manually. Error: {str(e)}")

def resolve_variant_id(store_domain: str, access_token: str, input_id: str | int) -> str:
    """
    Resolves a numeric or GID input to a valid ProductVariant GID.
    If the input is a Product ID, it fetches the first available Variant ID.
    If the input is already a Variant ID (or unknown), it formats it as a Variant GID.
    """
    numeric_id = "".join(filter(str.isdigit, str(input_id)))
    if not numeric_id:
        return str(input_id) # Fallback for completely non-numeric garbage

    # 1. Try treating it as a Product ID first to get the default variant
    product_gid = f"gid://shopify/Product/{numeric_id}"
    
    query = """
    query($id: ID!) {
      product(id: $id) {
        variants(first: 1) {
          nodes { id }
        }
      }
    }
    """
    
    try:
        if not store_domain.startswith("http"):
             api_url = f"https://{store_domain}/api/2025-01/graphql.json"
        else:
             api_url = f"{store_domain.rstrip('/')}/api/2025-01/graphql.json"

        response = requests.post(
            api_url,
            json={'query': query, 'variables': {'id': product_gid}},
            headers={
                'X-Shopify-Storefront-Access-Token': access_token,
                'Content-Type': 'application/json'
            },
            timeout=5
        )
        
        data = response.json()
        # If product found and has variants, return the first variant's ID
        if data.get('data') and data['data'].get('product') and data['data']['product'].get('variants'):
            nodes = data['data']['product']['variants']['nodes']
            if nodes:
                print(f"✅ Resolved Product {numeric_id} -> Variant {nodes[0]['id']}")
                return nodes[0]['id']
                
    except Exception as e:
        print(f"⚠️ Failed to resolve Product ID: {e}")

    # 2. Fallback: Assume it's a Variant ID if product lookup failed/returned null
    return f"gid://shopify/ProductVariant/{numeric_id}"


@app.post("/checkout")
async def create_checkout(request: CheckoutRequest):
    store_domain = request.store_domain
    access_token = request.access_token
    
    # Auto-discovery if token not provided (needed early for resolution)
    if not access_token:
        access_token = find_storefront_token(store_domain)

    # Resolve all items to valid Variant IDs
    line_items = []
    # Handle single item request structure (backwards compatibility shim if needed, 
    # but based on previous step we returned to single item structure in CheckoutRequest)
    # Wait, the prompt reverted to single item.
    
    # Resolving the single variant_id from request
    final_variant_id = resolve_variant_id(store_domain, access_token, request.variant_id)
    
    line_items = [{'quantity': request.quantity, 'merchandiseId': final_variant_id}]

    query = """
    mutation($lines: [CartLineInput!]!) {
      cartCreate(input: { lines: $lines }) {
        cart { checkoutUrl }
        userErrors { field message }
      }
    }
    """
    
    try:
        if not store_domain.startswith("http"):
             api_url = f"https://{store_domain}/api/2025-01/graphql.json"
        else:
             api_url = f"{store_domain.rstrip('/')}/api/2025-01/graphql.json"

        response = requests.post(
            api_url,
            json={
                'query': query, 
                'variables': {
                    'lines': line_items
                }
            },
            headers={
                'X-Shopify-Storefront-Access-Token': access_token,
                'Content-Type': 'application/json'
            }
        )
        
        data = response.json()
        
        if 'errors' in data:
            raise HTTPException(status_code=500, detail=f"GraphQL Error: {data['errors']}")
            
        cart_data = data['data']['cartCreate']
        if cart_data['userErrors']:
            raise HTTPException(status_code=400, detail=f"User Error: {cart_data['userErrors'][0]['message']}")
            
        return {"checkout_url": cart_data['cart']['checkoutUrl'], "used_token": access_token}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
