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
            
            # For POST requests, read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Create request to backend
            req = urllib.request.Request(backend_url, data=body)
            
            # Copy headers (except Host)
            for header, value in self.headers.items():
                if header.lower() != 'host':
                    req.add_header(header, value)
            
            # Make request to backend
            with urllib.request.urlopen(req) as response:
                # Send response headers
                self.send_response(response.status)
                for header, value in response.headers.items():
                    if header.lower() not in ['content-encoding', 'transfer-encoding', 'content-length']:
                        self.send_header(header, value)
                self.end_headers()
                
                # Stream response body
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    
        except URLError as e:
            self.send_error(502, f"Backend connection error: {e}")
        except Exception as e:
            self.send_error(500, f"Proxy error: {e}")

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
