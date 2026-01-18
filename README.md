# Trovato - Speak it. Cart it. Own it.

**By Josh, Hadi, Daniel, Henrique**

> UofTHacks 2026 - Shopify Track

An AI-powered conversational shopping assistant using the Universal Commerce Protocol (UCP) to find and purchase products through natural language. Trovato bridges the gap between discovery and purchase by allowing users to simply say what they want.

## Problem
Finding the right products takes too much effort. Users face endless scrolling through disconnected store pages, complex comparisons of shipping options and prices, decision fatigue from sorting through countless options, and fragmentation between discovery (search) and action (checkout).

**Our Solution**
Trovato is an agentic shopping assistant that interconnects with Shopify merchants via the **Universal Commerce Protocol (UCP)**. It understands complex natural language queries, finds the best matching products across multiple stores, and builds a single checkout session for you. Just tell us what you want, and we'll find it for you.

## Tech Stack

### Frontend (frontend3/)
- **Framework**: Next.js 16 (React 19)
- **Styling**: Tailwind CSS v4 & Framer Motion
- **UI Components**: Radix UI / Shadcn

### Backend (backend/)
- **API**: FastAPI (server.py)
- **Agent Orchestration**: LangGraph (mcp_agent.py)
- **Protocol**: Model Context Protocol (MCP) (mcp_multi_client.py)
- **Database**: MongoDB (Search History)

### Integrations
- **Shopify Storefront API**: Dynamic product resolution and checkout creation.
- **Groq**: High-speed LLM inference for agentic reasoning.

## Project Structure

This project is organized into a clear separation of concerns between the frontend user interface and the backend agentic logic.

```bash
tavardo/
├── backend/                  # Python FastAPI Backend
│   ├── server.py             # The core API entry point. Handles HTTP requests, manages the lifecycle of the AI agent, and exposes endpoints for search and checkout.
│   ├── mcp_agent.py          # Contains the LangGraph definition for the AI Agent. This defines the cognitive architecture and decision-making flow of the assistant.
│   ├── mcp_multi_client.py   # Implements the Model Context Protocol (MCP) client. This allows the backend to communicate with standardized external tools and standardized commerce protocols.
│   ├── database.py           # Manages connections to the MongoDB instance. Used primarily for persisting user search history to personalize future results.
│   └── util.py               # A collection of helper functions and utilities used across the backend for tasks like data formatting and minor logic abstraction.
├── frontend3/                # Next.js Frontend
│   ├── src/app/page.tsx      # The main application page. Features the chat interface where users interact with the agent.
│   └── package.json          # Defines the Node.js dependencies and scripts for building and running the frontend application.
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB instance
- Shopify API Keys (in .env)

### 1. Backend Setup
Navigate to the backend directory and start the server:

```bash
cd backend
# Install dependencies (using uv or pip)
pip install -r ../requirements.txt  # or install from pyproject.toml
python server.py
```
*Server runs on http://localhost:8080*

### 2. Frontend Setup
Navigate to the frontend directory and start the dev server:

```bash
cd frontend3
npm install
npm run dev
```
*Frontend runs on http://localhost:3000*

## Architecture

1.  **User Query**: User types "Find me red running shoes" in the **Frontend**.
2.  **Agent Processing**: Request sent to the backend API. The **Backend** delegates the intent analysis to the **Agent**.
3.  **Discovery**: The Agent queries MCP servers (specifically the Shopify Catalog) to intelligently find products that match the semantic meaning of the user's request.
4.  **Response**: The Agent structures the found results into a standardized format and returns them to the UI for display.
5.  **Checkout**: When a user selects items, the system performs a smart resolution of Variant IDs and generates a direct Shopify Checkout URL.
