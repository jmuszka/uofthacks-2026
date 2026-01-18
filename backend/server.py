import os
import requests
import re
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from dotenv import load_dotenv
from enums.sort import SortBy 
from dto.search import SearchRequest 
from dto.purchase import PurchaseRequest, PurchaseResponse
from util import search_products
import json
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

# Define which origins (frontends) are allowed
origins = [
    "http://localhost:3000", # Your React/Vue/Svelte dev server
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Allow these specific ports
    allow_credentials=True,
    allow_methods=["*"],         # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],         # Allow all headers
)

class CheckoutRequest(BaseModel):
    variant_id: str
    quantity: int = 1
    store_domain: str
    access_token: str | None = None

# Search for items via the Shopify Catalog MCP Server
@app.post("/search")
async def search(
    req: SearchRequest,
    limit: int = Query(default=10, ge=1, le=100),
    sort_order: str = Query(default=SortBy.RELEVANCE)
):
    
    res = await search_products(req.query)

    print(f"DEBUG: Result type is {type(res)}")

    return {
            "items": json.dumps(json.loads(res), separators=(',', ':'))
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

@app.post("/checkout")
async def create_checkout(request: CheckoutRequest):
    store_domain = request.store_domain
    access_token = request.access_token
    
    # Auto-discovery if token not provided
    if not access_token:
        access_token = find_storefront_token(store_domain)

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
                    'lines': [{'quantity': request.quantity, 'merchandiseId': request.variant_id}]
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
    uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=True)
