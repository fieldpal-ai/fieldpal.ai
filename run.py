#!/usr/bin/env python3
"""
Run script for FieldPal.ai application
This file exports the app object for Azure App Service deployment
"""
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the app from app.main
from app.main import app

# Export app for gunicorn/azure
__all__ = ['app']

if __name__ == "__main__":
    import uvicorn
    import os
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8003))
    reload = os.getenv("DEBUG", "False").lower() == "true"
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload
    )

