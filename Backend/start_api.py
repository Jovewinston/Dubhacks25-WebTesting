#!/usr/bin/env python3
"""
Startup script for the Web Testing Pipeline API
"""

import uvicorn
import sys
import os

# Add the Backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Starting Web Testing Pipeline API...")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/api/v1/health")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
