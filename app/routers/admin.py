from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from app.auth import get_current_user_optional_from_request
from app.core.templates import render_template
from app.core.config import Config
from app.services.analytics import AnalyticsService

router = APIRouter()

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
    
    return render_template("admin/content.html", request=request, user=user)

@router.get("/images")
async def admin_images(request: Request):
    """Image management page"""
    if not Config.is_auth0_configured():
        return RedirectResponse(url="/auth/login", status_code=302)
    
    user = await get_current_user_optional_from_request(request)
    
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    return render_template("admin/images.html", request=request, user=user)

