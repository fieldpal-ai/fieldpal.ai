from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from app.auth import get_current_user_optional_from_request
from app.core.templates import render_template
from app.core.config import Config
from app.services.analytics import AnalyticsService
from app.services.azure_storage import AzureStorageService
from typing import Dict, Optional

router = APIRouter()

# List of authorized admin user IDs
AUTHORIZED_ADMIN_USERS = [
    "google-oauth2|113092643924672726107",
    "google-oauth2|102070775897269563284"
]

def is_authorized_admin(user: Optional[Dict]) -> bool:
    """Check if user is an authorized admin"""
    if not user:
        return False
    user_id = user.get("sub") or user.get("user_id")
    return user_id in AUTHORIZED_ADMIN_USERS

def get_storage_service():
    """Get storage service instance"""
    return AzureStorageService()

@router.get("/")
async def admin_dashboard(request: Request):
    """Admin dashboard - redirects to login if not authenticated"""
    # Check Auth0 config first
    if not Config.is_auth0_configured():
        return RedirectResponse(url="/auth/login", status_code=302)
    
    # Try to get user (returns None if not authenticated)
    user = await get_current_user_optional_from_request(request)
    
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    # Check if user is authorized
    if not is_authorized_admin(user):
        response = render_template("admin/unauthorized.html", request=request, user=user)
        response.status_code = status.HTTP_403_FORBIDDEN
        return response
    
    # Track admin dashboard view
    AnalyticsService.capture(
        distinct_id=user.get("sub", "unknown"),
        event="admin_dashboard_viewed",
        properties={
            "email": user.get("email", "unknown")
        }
    )
    
    return render_template("admin/dashboard.html", request=request, user=user)

@router.get("/content")
async def admin_content(request: Request):
    """Content management page"""
    if not Config.is_auth0_configured():
        return RedirectResponse(url="/auth/login", status_code=302)
    
    user = await get_current_user_optional_from_request(request)
    
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    # Check if user is authorized
    if not is_authorized_admin(user):
        response = render_template("admin/unauthorized.html", request=request, user=user)
        response.status_code = status.HTTP_403_FORBIDDEN
        return response
    
    return render_template("admin/content.html", request=request, user=user)

@router.get("/images")
async def admin_images(request: Request):
    """Image management page"""
    if not Config.is_auth0_configured():
        return RedirectResponse(url="/auth/login", status_code=302)
    
    user = await get_current_user_optional_from_request(request)
    
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    # Check if user is authorized
    if not is_authorized_admin(user):
        response = render_template("admin/unauthorized.html", request=request, user=user)
        response.status_code = status.HTTP_403_FORBIDDEN
        return response
    
    return render_template("admin/images.html", request=request, user=user)

@router.get("/contacts")
async def admin_contacts(request: Request):
    """Contact submissions management page"""
    if not Config.is_auth0_configured():
        return RedirectResponse(url="/auth/login", status_code=302)
    
    user = await get_current_user_optional_from_request(request)
    
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    # Check if user is authorized
    if not is_authorized_admin(user):
        response = render_template("admin/unauthorized.html", request=request, user=user)
        response.status_code = status.HTTP_403_FORBIDDEN
        return response
    
    # Get contact submissions
    submissions = []
    try:
        storage_service = get_storage_service()
        submissions = await storage_service.get_contact_submissions(limit=100)
    except Exception as e:
        # Log error but continue - show empty list
        print(f"Error loading contact submissions: {e}")
    
    return render_template("admin/contacts.html", request=request, user=user, submissions=submissions)

