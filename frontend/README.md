# Frontend - Business Chat UI (Pure HTML/CSS/JS)

A clean, business-like chat interface built with pure HTML, CSS, and JavaScript using Bootstrap that connects to the FastAPI backend in `api/app.py`.

## Quick Start

### Option 1: Using Python HTTP Server (Recommended)

1. Run the backend in one terminal from repo root (port 8000):

```
uv run uvicorn api.app:app --reload
```

2. Run the frontend server in another terminal (port 3000):

```
cd frontend
python3 server.py
```

The frontend server will automatically proxy API requests to the backend.

3. Open your browser to `http://localhost:3000`

### Option 2: Using Python's Built-in HTTP Server

1. Run the backend as described above.

2. Start a simple HTTP server from the frontend directory:

```
cd frontend
python3 -m http.server 3000
```

**Note:** With this method, API requests will need to be configured to point to `http://localhost:8000` (you may need to modify the fetch URL in `index.html` or use a browser extension to handle CORS).

### Option 3: Direct File Access

You can also open `index.html` directly in your browser, but you'll need to:
- Configure CORS in your browser
- Or modify the API endpoint URL to point to `http://localhost:8000/api/chat`

## Features
- Streaming responses rendered live
- Editable system/developer message
- Model picker (defaults to `gpt-4.1-mini`)
- Business-like dark UI with subtle accents
- Responsive design using Bootstrap 5
- Pure JavaScript (no frameworks)

## Technology Stack
- **HTML5** - Structure
- **CSS3** - Styling with custom variables
- **JavaScript (ES6+)** - Interactivity and API communication
- **Bootstrap 5.3.2** - UI components and responsive grid
- **Bootstrap Icons** - Icon library

## Files
- `index.html` - Main HTML file with embedded CSS and JavaScript
- `server.py` - Development server with API proxying

## Where to Customize
- UI: `index.html` (contains all HTML, CSS, and JavaScript)
- Styling: CSS is in the `<style>` section of `index.html`
- Behavior: JavaScript is in the `<script>` section of `index.html`

## Notes
- The backend expects `OPENAI_API_KEY` to be set where it runs.
- CORS is already permissive in the backend for development convenience.
- For Vercel deployment, the `vercel.json` configuration routes `/api/*` to the backend and serves static files from `frontend/`.