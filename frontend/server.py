#!/usr/bin/env python3
"""
Simple HTTP server for local development of the frontend.
This serves the static HTML file and proxies API requests to the FastAPI backend.
"""

import http.server
import socketserver
import urllib.request
import urllib.parse
import json
from urllib.error import URLError

PORT = 3000
BACKEND_URL = "http://localhost:8000"


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler that serves static files and proxies API requests."""

    def do_GET(self):
        """Handle GET requests."""
        if self.path.startswith('/api/'):
            # Proxy API requests to backend
            self.proxy_request()
        else:
            # Serve static files
            if self.path == '/':
                self.path = '/index.html'
            super().do_GET()

    def do_POST(self):
        """Handle POST requests - proxy to backend."""
        if self.path.startswith('/api/'):
            self.proxy_request()
        else:
            self.send_error(404, "Not found")

    def proxy_request(self):
        """Proxy request to FastAPI backend."""
        try:
            backend_url = BACKEND_URL + self.path
            print(f"[PROXY] Proxying {self.command} {self.path} -> {backend_url}")
            
            # For POST requests, read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Create request to backend
            req = urllib.request.Request(backend_url, data=body)
            
            # Set content type if body exists
            if body:
                req.add_header('Content-Type', 'application/json')
            
            # Copy headers (except Host and Content-Length which urllib handles)
            for header, value in self.headers.items():
                header_lower = header.lower()
                if header_lower not in ['host', 'content-length', 'connection']:
                    req.add_header(header, value)
            
            # Make request to backend with timeout
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    # Send response headers
                    self.send_response(response.status)
                    for header, value in response.headers.items():
                        header_lower = header.lower()
                        if header_lower not in ['content-encoding', 'transfer-encoding', 'content-length', 'connection']:
                            self.send_header(header, value)
                    self.end_headers()
                    
                    # Stream response body
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
            except urllib.error.HTTPError as e:
                # Handle HTTP errors (like 500 from backend)
                print(f"[PROXY] Backend returned error: {e.code} {e.reason}")
                error_body = e.read().decode('utf-8', errors='ignore')
                print(f"[PROXY] Error body: {error_body[:500]}")
                
                # Forward the error response to client
                self.send_response(e.code)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = {
                    "error": f"Backend error: {e.code} {e.reason}",
                    "message": "The backend API returned an error. Please check if the backend is running and OPENAI_API_KEY is set.",
                    "details": error_body[:200] if error_body else "No error details available"
                }
                self.wfile.write(json.dumps(error_response).encode())
                    
        except urllib.error.URLError as e:
            error_msg = str(e)
            print(f"[PROXY] Connection error: {error_msg}")
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {
                "error": "Backend connection failed",
                "message": f"Cannot connect to backend at {BACKEND_URL}. Please ensure the backend is running on port 8000.",
                "details": error_msg
            }
            self.wfile.write(json.dumps(error_response).encode())
        except Exception as e:
            print(f"[PROXY] Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {
                "error": "Proxy error",
                "message": "An unexpected error occurred in the proxy server",
                "details": str(e)
            }
            self.wfile.write(json.dumps(error_response).encode())

    def end_headers(self):
        """Add CORS headers for local development."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def log_message(self, format, *args):
        """Override to provide cleaner log output."""
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    """Run the development server."""
    import os
    
    # Change to frontend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
        print(f"Frontend server running at http://localhost:{PORT}")
        print(f"API requests will be proxied to {BACKEND_URL}")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
