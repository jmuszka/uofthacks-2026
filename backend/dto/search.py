from pydantic import BaseModel, Field
from typing import Optional

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="The natural language catalog query.")
    # category: Optional[str] = Field(..., min_length=1, description="Product category.")
    # profile: Optional[str] = Field(..., min_length=1, description="Background information about the user.")
