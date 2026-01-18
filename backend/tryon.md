# Virtual Try-On Feature

## Overview

When a user with a profile photo searches for a product, generate an AI image showing the user wearing/using that product using Gemini's image generation API.

## Flow

```
┌─────────────┐     Search "red hat"    ┌─────────────┐
│   Frontend  │ ──────────────────────► │   Backend   │
│             │                         │             │
└─────────────┘                         └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │  MongoDB    │
                                        │  Get user   │
                                        │  profile    │
                                        └──────┬──────┘
                                               │
                              photo !== null?  │
                                               ▼
                                        ┌─────────────┐
                                        │  Gemini API │
                                        │  Generate   │
                                        │  try-on     │
                                        └──────┬──────┘
                                               │
                                               ▼
┌─────────────┐    Products + try-on    ┌─────────────┐
│   Frontend  │ ◄────────────────────── │   Response  │
│   Display   │       image             │             │
└─────────────┘                         └─────────────┘
```

## Implementation

### 1. Backend Endpoint

Create `POST /tryon` or enhance existing `/search` response:

```python
@router.post("/tryon")
async def generate_tryon(user_id: str, product_image_url: str, product_name: str):
    """
    Generate a try-on image of the user wearing the product.
    
    Args:
        user_id: Supabase user ID (to fetch profile photo)
        product_image_url: URL of the product image from search results
        product_name: Name of the product (for prompt context)
    
    Returns:
        { "tryon_image": "base64 encoded image" }
    """
    # 1. Get user profile from MongoDB
    profile = get_user_profile(user_id)
    
    if not profile or not profile.get("photo"):
        return {"error": "No profile photo available"}
    
    user_photo_base64 = profile["photo"]  # Already stored as base64
    
    # 2. Call Gemini API to generate try-on image
    tryon_image = await generate_tryon_image(
        user_photo=user_photo_base64,
        product_image_url=product_image_url,
        product_name=product_name
    )
    
    return {"tryon_image": tryon_image}
```

### 2. Gemini Image Generation

```python
import google.generativeai as genai
import base64
import requests

async def generate_tryon_image(user_photo: str, product_image_url: str, product_name: str) -> str:
    """
    Use Gemini to generate an image of the user wearing the product.
    """
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    
    # Fetch product image
    product_image_data = requests.get(product_image_url).content
    product_image_base64 = base64.b64encode(product_image_data).decode()
    
    # Use Gemini's image generation model
    model = genai.GenerativeModel("gemini-2.0-flash-exp")  # or imagen-3
    
    prompt = f"""
    Create a realistic photo of the person in the first image wearing/using the {product_name} 
    shown in the second image. Keep the person's face and body proportions accurate.
    The result should look like a natural photo of them trying on the product.
    """
    
    response = model.generate_content([
        prompt,
        {"mime_type": "image/jpeg", "data": user_photo},
        {"mime_type": "image/jpeg", "data": product_image_base64}
    ])
    
    # Return generated image as base64
    return response.candidates[0].content.parts[0].inline_data.data
```

### 3. Frontend Integration

```tsx
// After search results load, if user has profile photo
const handleTryOn = async (product) => {
  const response = await fetch('/tryon', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: session.user.id,
      product_image_url: product.image,
      product_name: product.title
    })
  });
  
  const { tryon_image } = await response.json();
  
  // Display in modal or overlay
  setTryOnImage(`data:image/jpeg;base64,${tryon_image}`);
  setShowTryOnModal(true);
};
```

## UI/UX

1. **Try-On Button**: Add a "Try it on" button on each product card (only visible if user has profile photo)

2. **Loading State**: Show spinner while Gemini generates (can take 5-15 seconds)

3. **Modal Display**: Show generated image in a modal with:
   - Side-by-side comparison (original product vs try-on)
   - "Add to Cart" button
   - "Save Image" option

## Prerequisites

- [ ] User profile with `photo` field (base64 image) - ✅ Already implemented
- [ ] Google API key with Gemini access - ✅ Already in `.env`
- [ ] Product images from search results - ✅ Available from Shopify

## Limitations

- **Gemini image generation** may not be available in all regions
- **Quality depends on** user photo quality and product type
- **Works best for**: Hats, glasses, jewelry, accessories
- **May struggle with**: Full outfits, shoes (body positioning)

## Alternative: Use Imagen 3

If Gemini's native image gen isn't available, use **Imagen 3** via Vertex AI:

```python
from google.cloud import aiplatform

def generate_with_imagen(prompt, reference_images):
    model = aiplatform.ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
    response = model.generate_images(prompt=prompt, reference_images=reference_images)
    return response.images[0]._image_bytes
```
