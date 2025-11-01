# Import required FastAPI components for building the API
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
# Import Pydantic for data validation and settings management
from pydantic import BaseModel
# Import OpenAI client for interacting with OpenAI's API
from openai import OpenAI
import os
from typing import Optional

# Initialize FastAPI application with a title
app = FastAPI(title="OpenAI Chat API")

# Configure CORS (Cross-Origin Resource Sharing) middleware
# This allows the API to be accessed from different domains/origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin
    allow_credentials=True,  # Allows cookies to be included in requests
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers in requests
)

# Define the data model for chat requests using Pydantic
# This ensures incoming request data is properly validated
class ChatRequest(BaseModel):
    developer_message: str  # Message from the developer/system
    user_message: str      # Message from the user
    model: Optional[str] = "gpt-4.1-mini"  # Optional model selection with default
    # api_key: str          # OpenAI API key for authentication

# Helper function for chat logic (to avoid duplication)
async def _handle_chat(request: ChatRequest):
    """Internal chat handler logic"""
    # Get the OpenAI API key from the environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured on server")

    # Initialize OpenAI client with the provided API key
    client = OpenAI(api_key=api_key)
    
    # Create an async generator function for streaming responses
    async def generate():
        # Create a streaming chat completion request
        # Note: OpenAI API uses "system" role, not "developer"
        stream = client.chat.completions.create(
            model=request.model,
            messages=[
                {"role": "system", "content": request.developer_message},
                {"role": "user", "content": request.user_message}
            ],
            stream=True  # Enable streaming response
        )
        
        # Yield each chunk of the response as it becomes available
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    # Return a streaming response to the client
    return StreamingResponse(generate(), media_type="text/plain")

# Define the main chat endpoint that handles POST requests
# Support both /api/chat and /chat paths for Vercel routing compatibility
@app.post("/api/chat")
async def chat_with_prefix(request: ChatRequest):
    try:
        return await _handle_chat(request)
    except HTTPException:
        raise
    except Exception as e:
        # Handle any errors that occur during processing
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    """Alternative endpoint path if Vercel strips /api prefix"""
    try:
        return await _handle_chat(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Define a health check endpoint to verify API status
# Support both /api/health and /health paths for Vercel routing compatibility
@app.get("/api/health")
async def health_check_with_prefix():
    return {"status": "ok", "message": "API is running"}

@app.get("/health")
async def health_check():
    """Alternative endpoint path if Vercel strips /api prefix"""
    return {"status": "ok", "message": "API is running"}

# Debug endpoints to check routing and test connectivity
@app.get("/")
async def root():
    return {"message": "FastAPI is running", "endpoints": ["/api/chat", "/chat", "/api/health", "/health"]}

@app.get("/api")
async def api_root():
    """Debug endpoint to verify /api routing works"""
    return {"message": "API root endpoint", "status": "ok", "available_endpoints": ["/api/chat", "/api/health"]}

# Also add /api/ route without trailing path for Vercel routing
@app.api_route("/api", methods=["GET"])
async def api_root_alt():
    """Alternative API root endpoint"""
    return {"message": "API root endpoint", "status": "ok", "available_endpoints": ["/api/chat", "/api/health"]}

# Diagnostic endpoint to check environment variable configuration
@app.get("/api/env-check")
async def env_check():
    """Diagnostic endpoint to verify environment variable is accessible"""
    api_key_present = os.getenv("OPENAI_API_KEY") is not None
    api_key_length = len(os.getenv("OPENAI_API_KEY", ""))
    return {
        "OPENAI_API_KEY_present": api_key_present,
        "OPENAI_API_KEY_length": api_key_length if api_key_present else 0,
        "status": "configured" if api_key_present else "missing",
        "note": "If missing, add OPENAI_API_KEY in Vercel project settings -> Environment Variables"
    }

# Entry point for running the application directly
if __name__ == "__main__":
    import uvicorn
    # Start the server on all network interfaces (0.0.0.0) on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
