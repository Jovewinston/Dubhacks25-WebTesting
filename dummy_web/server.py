#!/usr/bin/env python3
"""
Simple HTTP Server for Calculator App

This server serves the calculator app with StatSig integration
for testing purposes.
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

def start_server(port=5000):
    """Start the HTTP server."""
    
    # Change to the dummy_web directory
    web_dir = Path(__file__).parent
    os.chdir(web_dir)
    
    # Create server
    handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🚀 Calculator App Server Started")
        print(f"📱 URL: http://localhost:{port}")
        print(f"📁 Serving from: {web_dir}")
        print(f"🧮 Calculator with StatSig integration ready!")
        print(f"⏹️  Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Open browser automatically
        webbrowser.open(f'http://localhost:{port}')
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🛑 Server stopped")
            httpd.shutdown()

if __name__ == "__main__":
    start_server()
