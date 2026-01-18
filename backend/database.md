# Database Documentation

## Overview

Trovato uses **MongoDB Atlas** to store user data. The database is named `Travado` and connects via the connection string in `.env`.

## Architecture

```
┌─────────────┐     POST /profile      ┌─────────────┐     upsert       ┌─────────────┐
│  Frontend   │ ──────────────────────▶│   Backend   │ ────────────────▶│  MongoDB    │
│  (Next.js)  │                        │  (FastAPI)  │                  │   Atlas     │
└─────────────┘                        └─────────────┘                  └─────────────┘
       │                                                                      │
       │  Login Page collects (multi-step wizard):                            │
       │  1. Account info (name, email, password) → Supabase Auth             │
       │  2. Photo (optional selfie/upload)                                   │
       │  3. Body sizes (clothing, waist, shoe, fit)                          │
       │  4. Style preferences + custom style                  Collections:   │
       │  5. Shopping values + custom value                  - user_profiles  │
       │  6. Budget slider (0-100) + Zip code                - search_history │
       └──────────────────────────────────────────────────────────────────────┘
```

## Collections

### `user_profiles`

Stores user preferences collected during signup for personalized search.

**Document Schema:**
```json
{
  "user_id": "supabase-uuid-abc123",
  "name": "John Doe",
  "email": "john@example.com",
  "photo": "data:image/jpeg;base64,... or null",
  "sizes": {
    "clothing": "M",
    "waist": "32",
    "shoe": "10.5",
    "fit": "Regular"
  },
  "style": ["streetwear", "minimalist"],
  "customStyle": "techwear",
  "values": ["eco-friendly", "local"],
  "customValue": "small business",
  "budget": 50,
  "zipCode": "90210",
  "created_at": "2026-01-18T04:00:00Z",
  "updated_at": "2026-01-18T04:00:00Z"
}
```

**Field Details:**

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | string | Supabase auth user ID (primary key) |
| `name` | string | User's display name |
| `email` | string | User's email address |
| `photo` | string \| null | Profile photo as base64 data URL |
| `sizes.clothing` | string | Clothing size: `"XS"`, `"S"`, `"M"`, `"L"`, `"XL"`, `"XXL"` |
| `sizes.waist` | string | Waist measurement (e.g., `"32"`) |
| `sizes.shoe` | string | Shoe size (e.g., `"10.5"`) |
| `sizes.fit` | string | Fit preference: `"Slim"`, `"Regular"`, `"Oversized"` |
| `style` | array | Style preferences (multi-select from options) |
| `customStyle` | string | User-entered custom style (max 20 chars) |
| `values` | array | Shopping values (multi-select from options) |
| `customValue` | string | User-entered custom value (max 20 chars) |
| `budget` | number | Budget slider 0-100 (0-33=budget, 34-66=mid, 67-100=luxury) |
| `zipCode` | string | Zip code for shipping estimates |

**Style Options (frontend):**
- `"streetwear"` 🔥
- `"minimalist"` ⚪

**Value Options (frontend):**
- `"eco-friendly"` - Eco-Friendly
- `"local"` - Made Locally

**Budget Interpretation:**
| Range | Tier | Description |
|-------|------|-------------|
| 0-33 | 💵 Budget | Budget-Friendly (best value) |
| 34-66 | 💳 Mid | Mid-Range (quality meets price) |
| 67-100 | 💎 Luxury | Luxury (premium products) |

---

### `search_history`

Stores user search queries for context and analytics.

```json
{
  "user_id": "supabase-uuid-abc123",
  "query": "black leather jacket",
  "timestamp": "2026-01-18T04:00:00Z"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | string | Supabase user ID |
| `query` | string | Search query text |
| `timestamp` | datetime | When search was made |

## Environment Setup

Add to `backend/.env`:
```
MONGODB_URI=mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/?appName=Travado
```

## Usage: Personalizing Search

When user is logged in, fetch their profile and enhance the agent query:

```python
profile = get_user_profile(user_id)

# Convert budget number to tier
budget_tier = "budget" if profile['budget'] <= 33 else "mid" if profile['budget'] <= 66 else "luxury"

# Include custom preferences
all_styles = profile['style'] + ([profile['customStyle']] if profile['customStyle'] else [])
all_values = profile['values'] + ([profile['customValue']] if profile['customValue'] else [])

# Build personalized context
context = f"""
User prefers: {', '.join(all_styles)} style
Values: {', '.join(all_values)}
Budget: {budget_tier}
Size: {profile['sizes']['clothing']}
"""

enhanced_query = f"{user_query}\n\nUser Profile:\n{context}"
```

---

## API Integration

The backend exposes REST endpoints for profile management via `profile_router.py`.

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/profile` | Create or update user profile (upsert) |
| `GET` | `/profile/{user_id}` | Retrieve user profile |
| `DELETE` | `/profile/{user_id}` | Delete user profile |
| `GET` | `/profile` | List all profiles (admin/debug) |
| `GET` | `/profile/{user_id}/context` | Get personalization context string |

### Create/Update Profile

```bash
curl -X POST http://localhost:8080/profile \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "supabase-uuid-abc123",
    "name": "John Doe",
    "email": "john@example.com",
    "photo": null,
    "sizes": {
      "clothing": "M",
      "waist": "32",
      "shoe": "10.5",
      "fit": "Regular"
    },
    "style": ["streetwear", "minimalist"],
    "customStyle": "techwear",
    "values": ["eco-friendly"],
    "customValue": "small business",
    "budget": 50,
    "zipCode": "90210"
  }'
```

### Get Profile

```bash
curl http://localhost:8080/profile/supabase-uuid-abc123
```

### Get Personalization Context

Returns the context string injected into search queries:

```bash
curl http://localhost:8080/profile/supabase-uuid-abc123/context
```

Response:
```json
{
  "success": true,
  "context": "Style preferences: streetwear, minimalist, techwear\nValues: eco-friendly, small business\nBudget tier: mid-range\nClothing size: M, Shoe size: 10.5\nLocation: 90210"
}
```

---

## File Structure

```
backend/
├── database.py        # MongoDB connection & CRUD operations
├── models.py          # Pydantic schemas for UserProfile, SearchHistory
├── profile_router.py  # FastAPI router with /profile endpoints
├── init_db.py         # Run once to create collections & indexes
└── dto/
    └── profile.py     # Request/response DTOs for API
```

---

## Database Initialization

Run once to set up MongoDB collections and indexes:

```bash
cd backend
python init_db.py
```

This creates:
- `user_profiles` collection with unique index on `user_id`
- `search_history` collection with compound index on `user_id` + `timestamp`
