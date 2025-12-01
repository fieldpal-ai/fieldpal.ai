from fastapi import APIRouter, Request
from app.core.templates import render_template
from app.services.azure_storage import AzureStorageService

router = APIRouter()

def get_storage_service():
    """Get storage service instance"""
    return AzureStorageService()

@router.get("/about")
async def about(request: Request):
    """About page"""
    # Try to load content from Azure Storage
    content = {}
    try:
        storage_service = get_storage_service()
        content = await storage_service.get_content("about")
    except Exception:
        # Use default content if storage is not available or content doesn't exist
        pass
    
    return render_template("about.html", request=request, content=content)

