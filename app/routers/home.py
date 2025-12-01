from fastapi import APIRouter, Request
from app.core.templates import render_template
from app.services.azure_storage import AzureStorageService

router = APIRouter()

def get_storage_service():
    """Get storage service instance"""
    return AzureStorageService()

@router.get("/")
async def home(request: Request):
    """Home page"""
    # Try to load content from Azure Storage
    content = {}
    try:
        storage_service = get_storage_service()
        content = await storage_service.get_content("home")
    except Exception:
        # Use default content if storage is not available or content doesn't exist
        pass
    
    return render_template("home.html", request=request, content=content)

