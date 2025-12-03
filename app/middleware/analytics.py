"""
Analytics middleware to track page views
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.services.analytics import AnalyticsService
import uuid

class AnalyticsMiddleware(BaseHTTPMiddleware):
    """Middleware to track page views and requests"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip tracking for static files, API endpoints, and admin endpoints
        path = request.url.path
        if (
            path.startswith("/static") or
            path.startswith("/api") or
            path.startswith("/admin") or
            path.startswith("/auth") or
            path == "/health"
        ):
            return await call_next(request)
        
        # Get or create distinct_id from cookie
        distinct_id = request.cookies.get("analytics_id")
        if not distinct_id:
            distinct_id = str(uuid.uuid4())
        
        # Track page view
        AnalyticsService.capture(
            distinct_id=distinct_id,
            event="page_viewed",
            properties={
                "path": path,
                "method": request.method,
                "user_agent": request.headers.get("user-agent", ""),
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Set analytics ID cookie if not present
        if not request.cookies.get("analytics_id"):
            response.set_cookie(
                key="analytics_id",
                value=distinct_id,
                max_age=365 * 24 * 60 * 60,  # 1 year
                httponly=False,
                secure=False,  # Set to True in production with HTTPS
                samesite="lax"
            )
        
        return response



