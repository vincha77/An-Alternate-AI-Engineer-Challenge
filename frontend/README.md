# Frontend - Business Chat UI (Next.js)

A clean, business-like chat interface built with Next.js that connects to the FastAPI backend in `api/app.py`.

## Quick Start

Prereqs: Node 18+ recommended.

1. Install deps:

```
cd frontend
npm install
```

2. Run the frontend (port 3000):

```
npm run dev
```

3. Run the backend in another terminal from repo root (port 8000):

```
uv run uvicorn api.app:app --reload
```

4. During local development, add a proxy (optional). If serving from different ports, the frontend calls relative `/api/*`. If you open the frontend at `http://localhost:3000`, ensure the backend is reachable at the same origin via a reverse proxy or run in an environment that routes `/api/*` to the FastAPI app. In deployment (Vercel), the provided root `vercel.json` already routes `/api/*` to the backend.

## Features
- Streaming responses rendered live
- Editable system/developer message
- Model picker (defaults to `gpt-4.1-mini`)
- Business-like dark UI with subtle accents

## Where to Customize
- UI: `app/page.tsx`
- HTML wrapper/meta: `app/layout.tsx`

## Notes
- The backend expects `OPENAI_API_KEY` to be set where it runs.
- CORS is already permissive in the backend for development convenience.