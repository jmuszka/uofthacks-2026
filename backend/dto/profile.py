"""
DTOs for profile API endpoints.
These are the request/response models for the REST API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class SizesInput(BaseModel):
    """Body size input from frontend"""
    clothing: str = Field(default="M")
    waist: str = Field(default="32")
    shoe: str = Field(default="10")
    fit: str = Field(default="Regular")


class ProfileCreateRequest(BaseModel):
    """Request body for creating/updating a user profile"""
    user_id: str = Field(..., description="Supabase auth user ID")
    name: str = Field(default="", description="User's display name")
    email: str = Field(default="", description="User's email address")
    photo: Optional[str] = Field(default=None, description="Profile photo as base64 data URL")
    sizes: SizesInput = Field(default_factory=SizesInput)
    style: List[str] = Field(default_factory=list, description="Style preferences")
    customStyle: str = Field(default="", max_length=20)
    values: List[str] = Field(default_factory=list, description="Shopping values")
    customValue: str = Field(default="", max_length=20)
    budget: int = Field(default=50, ge=0, le=100)
    zipCode: str = Field(default="")


class ProfileResponse(BaseModel):
    """Response model for profile endpoints"""
    success: bool
    message: str
    profile: Optional[dict] = None
