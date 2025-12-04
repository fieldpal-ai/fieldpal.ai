from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.templates import render_template
from app.services.analytics import AnalyticsService
from app.services.azure_storage import AzureStorageService
from app.services.email import get_email_service
import uuid
from urllib.parse import quote

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
    
    # Save to Azure Table Storage
    try:
        storage_service = get_storage_service()
        await storage_service.save_contact_submission(
            name=form_data.name,
            email=form_data.email,
            message=form_data.message,
            subject=form_data.subject
        )
    except Exception as e:
        # Log error but don't fail the request - still return success to user
        print(f"Error saving contact submission to Azure Storage: {e}")
        # In production, you might want to log this to a monitoring service
    
    # Send email notification
    try:
        email_service = get_email_service()
        result = email_service.send_contact_notification(
            to_email="info@fieldpal.ai",
            name=form_data.name,
            email=form_data.email,
            message=form_data.message,
            subject=form_data.subject
        )
        if not result:
            print("Email notification failed - check logs above for details")
    except Exception as e:
        # Log error but don't fail the request - still return success to user
        print(f"Error sending email notification: {e}")
        import traceback
        traceback.print_exc()
        # In production, you might want to log this to a monitoring service
    
    # Redirect to home page with success message
    message = "Thank you for your message. We'll get back to you soon!"
    return RedirectResponse(url=f"/?contact_success={quote(message)}", status_code=303)

