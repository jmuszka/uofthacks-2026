"""
Profile API Router for FastAPI.
Handles user profile CRUD operations.

To use: Include this router in your main FastAPI app:
    from profile_router import router as profile_router
    app.include_router(profile_router)
"""

from fastapi import APIRouter, HTTPException, Path
from dto.profile import ProfileCreateRequest, ProfileResponse
from database import (
    upsert_user_profile,
    get_user_profile,
    delete_user_profile,
    get_all_profiles
)
from models import UserProfileModel, build_profile_context

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.post("", response_model=ProfileResponse)
async def create_or_update_profile(request: ProfileCreateRequest):
    """
    Create or update a user profile.
    Uses user_id as the unique identifier - if profile exists, it will be updated.
    """
    try:
        # Convert Pydantic model to dict
        profile_data = request.model_dump()
        
        # Convert nested sizes model to dict
        if hasattr(request.sizes, 'model_dump'):
            profile_data['sizes'] = request.sizes.model_dump()
        
        success = upsert_user_profile(profile_data)
        
        if success:
            # Retrieve the saved profile to return
            saved_profile = get_user_profile(request.user_id)
            return ProfileResponse(
                success=True,
                message="Profile saved successfully",
                profile=saved_profile
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to save profile")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=ProfileResponse)
async def get_profile(user_id: str = Path(..., description="Supabase user ID")):
    """
    Retrieve a user profile by user_id.
    """
    profile = get_user_profile(user_id)
    
    if profile:
        return ProfileResponse(
            success=True,
            message="Profile found",
            profile=profile
        )
    else:
        return ProfileResponse(
            success=False,
            message="Profile not found",
            profile=None
        )


@router.delete("/{user_id}", response_model=ProfileResponse)
async def remove_profile(user_id: str = Path(..., description="Supabase user ID")):
    """
    Delete a user profile by user_id.
    """
    success = delete_user_profile(user_id)
    
    if success:
        return ProfileResponse(
            success=True,
            message="Profile deleted successfully",
            profile=None
        )
    else:
        return ProfileResponse(
            success=False,
            message="Profile not found or could not be deleted",
            profile=None
        )


@router.get("", response_model=dict)
async def list_profiles():
    """
    List all user profiles (for admin/debugging).
    """
    profiles = get_all_profiles(limit=100)
    return {
        "success": True,
        "count": len(profiles),
        "profiles": profiles
    }


@router.get("/{user_id}/context")
async def get_profile_context(user_id: str = Path(..., description="Supabase user ID")):
    """
    Get the personalization context string for a user.
    This is what gets injected into search queries for personalization.
    """
    profile_data = get_user_profile(user_id)
    
    if not profile_data:
        return {
            "success": False,
            "message": "Profile not found",
            "context": ""
        }
    
    try:
        # Convert dict to Pydantic model for context building
        profile = UserProfileModel(**profile_data)
        context = build_profile_context(profile)
        
        return {
            "success": True,
            "message": "Context generated",
            "context": context
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "context": ""
        }
