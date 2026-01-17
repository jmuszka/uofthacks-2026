import os
import requests
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class CheckoutRequest(BaseModel):
    variant_id: str
    quantity: int = 1
    store_domain: str
    access_token: str | None = None

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
    uvicorn.run(app, host="0.0.0.0", port=8000)
