from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class PurchaseRequest(BaseModel):
    items: list[str] = Field(..., min_length=1, description="List of products to purchase via UCP")

class PurchaseResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    purchases: list[dict[str, bool]] = Field(..., description="Purchase-boolean pairs indicating success or failure purchasing")

    def add(self, item: str, success: bool):
        self.purchases.append({item: success})
