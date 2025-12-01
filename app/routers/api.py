from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from app.auth import require_auth
from app.services.azure_storage import AzureStorageService
from app.services.analytics import AnalyticsService
from typing import List

router = APIRouter()

# Lazy-load storage service to avoid errors on import
_storage_service = None

def get_storage_service():
    """Get or create storage service instance"""
    global _storage_service
    # Always recreate to ensure we get latest config from Pulumi
    # This is safe because the service is lightweight to create
    _storage_service = AzureStorageService()
    return _storage_service

@router.get("/content/{page}")
async def get_content(page: str):
    """Get content for a specific page from Azure Storage"""
    try:
        storage_service = get_storage_service()
        content = await storage_service.get_content(page)
        return JSONResponse(content=content)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/content/{page}")
async def update_content(page: str, content: dict, user: dict = Depends(require_auth)):
    """Update content for a specific page"""
    try:
        storage_service = get_storage_service()
        await storage_service.save_content(page, content)
        
        # Track content update
        AnalyticsService.capture(
            distinct_id=user.get("sub", "unknown"),
            event="content_updated",
            properties={
                "page": page,
                "email": user.get("email", "unknown")
            }
        )
        
        return JSONResponse(content={"status": "success"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/images/upload")
async def upload_image(file: UploadFile = File(...), user: dict = Depends(require_auth)):
    """Upload an image to Azure Blob Storage"""
    try:
        storage_service = get_storage_service()
        file_content = await file.read()
        url = await storage_service.upload_image(file.filename, file_content, file.content_type)
        
        # Track image upload
        AnalyticsService.capture(
            distinct_id=user.get("sub", "unknown"),
            event="image_uploaded",
            properties={
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(file_content),
                "email": user.get("email", "unknown")
            }
        )
        
        return JSONResponse(content={"status": "success", "url": url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/images")
async def list_images(user: dict = Depends(require_auth)):
    """List all images in Azure Blob Storage"""
    try:
        storage_service = get_storage_service()
        images = await storage_service.list_images()
        return JSONResponse(content={"images": images})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/images/{image_name}")
async def delete_image(image_name: str, user: dict = Depends(require_auth)):
    """Delete an image from Azure Blob Storage"""
    try:
        storage_service = get_storage_service()
        await storage_service.delete_image(image_name)
        
        # Track image deletion
        AnalyticsService.capture(
            distinct_id=user.get("sub", "unknown"),
            event="image_deleted",
            properties={
                "image_name": image_name,
                "email": user.get("email", "unknown")
            }
        )
        
        return JSONResponse(content={"status": "success"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

