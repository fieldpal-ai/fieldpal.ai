from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.templates import render_template
from app.services.analytics import AnalyticsService
from app.services.azure_storage import AzureStorageService
import uuid

router = APIRouter()

def get_storage_service():
    """Get storage service instance"""
    return AzureStorageService()

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    subject: Optional[str] = None
    message: str

@router.get("/contact")
async def contact(request: Request):
    """Contact page"""
    # Try to load content from Azure Storage
    content = {}
    try:
        storage_service = get_storage_service()
        content = await storage_service.get_content("contact")
    except Exception:
        # Use default content if storage is not available or content doesn't exist
        pass
    
    return render_template("contact.html", request=request, content=content)

@router.post("/contact/submit")
async def submit_contact(form_data: ContactForm, request: Request):
    """Handle contact form submission"""
    # Get analytics ID from cookie or generate one
    distinct_id = request.cookies.get("analytics_id", str(uuid.uuid4()))
    
    # Track contact form submission
    AnalyticsService.capture(
        distinct_id=distinct_id,
        event="contact_form_submitted",
        properties={
            "email": form_data.email,
            "has_subject": bool(form_data.subject),
            "message_length": len(form_data.message)
        }
    )
    
    # TODO: Implement email sending or storage to Azure
    # For now, just return success
    return JSONResponse(
        content={"status": "success", "message": "Thank you for your message. We'll get back to you soon!"}
    )

