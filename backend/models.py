"""
Pydantic models for MongoDB collections.
Matches the schema defined in database.md
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SizesModel(BaseModel):
    """User body size preferences"""
    clothing: str = Field(default="M", description="Clothing size: XS, S, M, L, XL, XXL")
    waist: str = Field(default="32", description="Waist measurement")
    shoe: str = Field(default="10", description="Shoe size")
    fit: str = Field(default="Regular", description="Fit preference: Slim, Regular, Oversized")


class UserProfileModel(BaseModel):
    """
    User profile stored in MongoDB.
    Contains preferences collected during signup for personalized search.
    """
    user_id: str = Field(..., description="Supabase auth user ID (primary key)")
    name: str = Field(default="", description="User's display name")
    email: str = Field(default="", description="User's email address")
    photo: Optional[str] = Field(default=None, description="Profile photo as base64 data URL")
    sizes: SizesModel = Field(default_factory=SizesModel, description="Body size preferences")
    style: List[str] = Field(default_factory=list, description="Style preferences (multi-select)")
    customStyle: str = Field(default="", max_length=20, description="User-entered custom style")
    values: List[str] = Field(default_factory=list, description="Shopping values (multi-select)")
    customValue: str = Field(default="", max_length=20, description="User-entered custom value")
    budget: int = Field(default=50, ge=0, le=100, description="Budget slider 0-100")
    zipCode: str = Field(default="", description="Zip code for shipping estimates")
    created_at: Optional[datetime] = Field(default=None, description="Profile creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")

    class Config:
        # Allow extra fields from MongoDB (like _id)
        extra = "ignore"


class SearchHistoryModel(BaseModel):
    """Search history entry stored in MongoDB"""
    user_id: str = Field(..., description="Supabase user ID")
    query: str = Field(..., description="Search query text")
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow(), description="When search was made")


def get_budget_tier(budget: int) -> str:
    """Convert budget number (0-100) to tier label"""
    if budget <= 33:
        return "budget"
    elif budget <= 66:
        return "mid-range"
    else:
        return "luxury"


def build_profile_context(profile: UserProfileModel) -> str:
    """
    Build a context string from user profile for search personalization.
    This is injected into the agent query.
    """
    budget_tier = get_budget_tier(profile.budget)
    
    # Combine selected styles with custom style
    all_styles = profile.style.copy()
    if profile.customStyle:
        all_styles.append(profile.customStyle)
    
    # Combine selected values with custom value
    all_values = profile.values.copy()
    if profile.customValue:
        all_values.append(profile.customValue)
    
    parts = []
    
    if all_styles:
        parts.append(f"Style preferences: {', '.join(all_styles)}")
    
    if all_values:
        parts.append(f"Values: {', '.join(all_values)}")
    
    parts.append(f"Budget tier: {budget_tier}")
    
    if profile.sizes:
        parts.append(f"Clothing size: {profile.sizes.clothing}, Shoe size: {profile.sizes.shoe}")
    
    if profile.zipCode:
        parts.append(f"Location: {profile.zipCode}")
    
    return "\n".join(parts)
