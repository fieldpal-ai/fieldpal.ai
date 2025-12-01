#!/usr/bin/env python3
"""
Simple HTTP server for local development of Fieldpal website.
Serves the static site and handles URL rewriting for local development.
"""

import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse, unquote

PORT = 8000

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers if needed
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()
    
    def do_GET(self):
        # Handle root path
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
        
        # Serve the file
        return super().do_GET()

def main():
    # Change to the directory where this script is located
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    Handler = CustomHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🚀 Server running at http://localhost:{PORT}/")
        print(f"📁 Serving from: {os.getcwd()}")
        print(f"🌐 Open http://localhost:{PORT} in your browser")
        print("\nPress Ctrl+C to stop the server\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped.")
            sys.exit(0)

if __name__ == "__main__":
    main()



