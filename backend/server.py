import os
import requests
import re
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from enums.sort import SortBy
from dto.search import SearchRequest
from dto.purchase import PurchaseRequest, PurchaseResponse
from util import search_products
from database import add_search_history
from time import sleep
from random import random
import json
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import asyncio
from mcp_agent import MCPLangGraphAgent

load_dotenv()

# Fetch fresh Shopify token on startup
def fetch_shopify_token():
    client_id = os.getenv("SHOPIFY_CLIENT_ID")
    client_secret = os.getenv("SHOPIFY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("⚠️  SHOPIFY_CLIENT_ID or SHOPIFY_CLIENT_SECRET missing. Skipping auto-fetch.")
        return

    try:
        print("🔄 Fetching new Shopify Access Token...")
        resp = requests.post(
            "https://api.shopify.com/auth/access_token",
            json={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials"
            },
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("access_token")
            if token:
                os.environ["SHOPIFY_ACCESS_TOKEN"] = token
                print("✅ Successfully refreshed SHOPIFY_ACCESS_TOKEN")
            else:
                print("❌ Failed to parse access_token from response")
        else:
            print(f"❌ Failed to fetch token: {resp.status_code} {resp.text}")
            
    except Exception as e:
        print(f"❌ Error fetching Shopify token: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Try to fetch a fresh token first
    fetch_shopify_token()

    # 2. Initialize Agent immediately on startup
    print("🚀 Pre-warming Agent Connection...")
    # The agent will read os.environ["SHOPIFY_ACCESS_TOKEN"] which we just updated
    app.state.agent = MCPLangGraphAgent("servers_config.json")
    await app.state.agent.initialize()
    print("✅ Agent Ready")
    
    yield
    
    print("🛑 Cleaning up...")
    if hasattr(app.state, "agent") and app.state.agent:
        await app.state.agent.cleanup()

app = FastAPI(lifespan=lifespan)

# Define which origins (frontends) are allowed
origins = [
    "http://localhost:3000", # Your React/Vue/Svelte dev server
    "http://127.0.0.1:3000",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Allow these specific ports
    allow_credentials=True,
    allow_methods=["*"],         # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],         # Allow all headers
)


class CheckoutItem(BaseModel):
    variant_id: str | int
    quantity: int = 1
    store_domain: str
    access_token: str | None = None

class CheckoutRequest(BaseModel):
    items: list[CheckoutItem]

# Accessor for the eagerly initialized agent
async def get_agent():
    if not hasattr(app.state, "agent") or not app.state.agent:
        raise HTTPException(503, "Agent not initialized (Startup failed?)")
    return app.state.agent

# Search for items via the Shopify Catalog MCP Server
@app.post("/search")
async def search(
    req: SearchRequest,
    limit: int = Query(default=10, ge=1, le=100),
    sort_order: SortBy = Query(default=SortBy.RELEVANCE),
    user_id: str = Query(default="")
):
    agent = await get_agent()
    print(f"Searching for: {req.query}")

    # Pass user_id for history tracking if needed (though history is handled in util.py now?)
    # Let's clean up util.py's history implementation vs server.py's
    # For now, just call search_products
    try:
        res = await search_products(agent, req.query, user_id)
        print(f"Agent Response: {res}")
        
        # Robust JSON extraction
        try:
            # Try parsing directly first
            data = json.loads(res.strip())
        except json.JSONDecodeError:
            # Fallback: Extract JSON array from text using regex
            import re
            match = re.search(r'\[.*\]', res, re.DOTALL)
            if match:
                json_str = match.group(0)
                try:
                    data = json.loads(json_str)
                except json.JSONDecodeError:
                     # Attempt to fix common trailing comma issues or markdown
                     clean_str = json_str.replace("`", "").strip()
                     data = json.loads(clean_str)
            else:
                 # Last resort: try to find just the JSON array start
                 if "[" in res:
                     start = res.find("[")
                     end = res.rfind("]") + 1
                     clean_str = res[start:end]
                     data = json.loads(clean_str)
                 else:
                    raise ValueError("No JSON array found in response")

        if user_id:
            # Note: add_search_history might be redundant if util.py does it, 
            # but util.py only READS history currently. 
            # server.py ADDS history after successful response.
            add_search_history(user_id, req.query)
            
        return {
            "items": json.dumps(data, separators=(",", ":"))
        }

    except Exception as e:
        print(f"Search failed/parse error: {e}")
        # Return empty list on failure, but log it
        return {
            "items": "[]", 
            "error": "Failed to parse JSON response from AI"
        }


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
    # Group items by store_domain
    items_by_store = {}
    for item in request.items:
        if item.store_domain not in items_by_store:
            items_by_store[item.store_domain] = []
        items_by_store[item.store_domain].append(item)
    
    checkouts = []

    for store_domain, items in items_by_store.items():
        try:
            # 1. Get Access Token (use the first one found or discover it)
            access_token = next((i.access_token for i in items if i.access_token), None)
            
            if not access_token:
                access_token = find_storefront_token(store_domain)
            
            # 2. Resolve all variant IDs for this store
            line_items = []
            for item in items:
                final_variant_id = resolve_variant_id(store_domain, access_token, item.variant_id)
                if final_variant_id:
                     line_items.append({'quantity': item.quantity, 'merchandiseId': final_variant_id})
            
            if not line_items:
                print(f"⚠️ No valid items for store {store_domain}, skipping.")
                continue

            # 3. Create Cart
            query = """
            mutation($lines: [CartLineInput!]!) {
              cartCreate(input: { lines: $lines }) {
                cart { checkoutUrl }
                userErrors { field message }
              }
            }
            """
            
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
                print(f"❌ GraphQL Error for {store_domain}: {data['errors']}")
                checkouts.append({"store": store_domain, "error": str(data['errors'])})
                continue
                
            cart_data = data['data']['cartCreate']
            if cart_data['userErrors']:
                 msg = cart_data['userErrors'][0]['message']
                 print(f"❌ User Error for {store_domain}: {msg}")
                 checkouts.append({"store": store_domain, "error": msg})
                 continue
                
            checkouts.append({
                "store": store_domain,
                "checkout_url": cart_data['cart']['checkoutUrl'],
                "item_count": len(line_items)
            })

        except Exception as e:
            print(f"❌ Error processing checkout for {store_domain}: {e}")
            checkouts.append({"store": store_domain, "error": str(e)})

    return {"checkouts": checkouts}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=True)
