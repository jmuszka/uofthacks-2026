from fastapi import FastAPI, Query
from dto.search import SearchRequest
from dto.purchase import PurchaseRequest, PurchaseResponse
from enums.sort import SortBy
from time import sleep
from random import random
from util import search_products
import json

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI running with uv!"}


# Search for items via the Shopify Catalog MCP Server
@app.get("/search")
async def search(
    req: SearchRequest,
    limit: int = Query(default=10, ge=1, le=100),
    sort_order: str = Query(default=SortBy.RELEVANCE)
):
    
    res = await search_products(req.query)

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=True)
