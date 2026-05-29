#!/usr/bin/env python3
"""Simple test to verify frontend build is accessible."""
import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 8000
FRONTEND_DIST = Path(__file__).parent / "frontend" / "dist"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIST), **kwargs)

if __name__ == "__main__":
    if not FRONTEND_DIST.exists():
        print(f"Error: Frontend dist not found at {FRONTEND_DIST}")
        exit(1)

    print(f"Serving frontend from {FRONTEND_DIST}")
    print(f"Open http://localhost:{PORT} in your browser")

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")
