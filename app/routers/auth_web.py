from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from app.core.templates import render_template
from app.core.config import Config
from app.services.analytics import AnalyticsService
import httpx
from urllib.parse import urlencode

router = APIRouter()

@router.get("/login")
async def login(request: Request):
    """Redirect to Auth0 login"""
    auth0_domain = Config.get_auth0_domain()
    auth0_client_id = Config.get_auth0_client_id()
    
    if not auth0_domain or not auth0_client_id:
        return render_template(
            "admin/login_error.html",
            request=request,
            error="Auth0 is not configured. Please configure Auth0 in Pulumi stack outputs or set AUTH0_DOMAIN and AUTH0_CLIENT_ID as environment variables."
        )
    
    auth0_audience = Config.get_auth0_audience()
    auth0_callback_url = Config.get_auth0_callback_url()
    
    # Ensure domain doesn't have protocol
    if auth0_domain.startswith("http://") or auth0_domain.startswith("https://"):
        auth0_domain = auth0_domain.replace("https://", "").replace("http://", "").strip("/")
    
    auth0_base_url = f"https://{auth0_domain}"
    
    # Build Auth0 authorization URL
    params = {
        "response_type": "code",
        "client_id": auth0_client_id,
        "redirect_uri": auth0_callback_url,
        "scope": "openid profile email",
        "audience": auth0_audience,
    }
    
    auth_url = f"{auth0_base_url}/authorize?{urlencode(params)}"
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def callback(request: Request, code: str = None, error: str = None):
    """Handle Auth0 callback"""
    if error:
        return render_template(
            "admin/login_error.html",
            request=request,
            error=f"Authentication error: {error}"
        )
    
    if not code:
        return render_template(
            "admin/login_error.html",
            request=request,
            error="No authorization code received"
        )
    
    # Exchange code for token
    try:
        auth0_domain = Config.get_auth0_domain()
        auth0_client_id = Config.get_auth0_client_id()
        auth0_client_secret = Config.get_auth0_client_secret()
        auth0_callback_url = Config.get_auth0_callback_url()
        
        # Ensure domain doesn't have protocol
        if auth0_domain.startswith("http://") or auth0_domain.startswith("https://"):
            auth0_domain = auth0_domain.replace("https://", "").replace("http://", "").strip("/")
        
        auth0_base_url = f"https://{auth0_domain}"
        
        token_url = f"{auth0_base_url}/oauth/token"
        token_data = {
            "grant_type": "authorization_code",
            "client_id": auth0_client_id,
            "client_secret": auth0_client_secret,
            "code": code,
            "redirect_uri": auth0_callback_url,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=token_data)
            response.raise_for_status()
            tokens = response.json()
        
        # Decode token to get user info for analytics
        from jose import jwt
        try:
            # Decode without verification to get user info (we already verified it)
            token_payload = jwt.decode(
                tokens.get("access_token"),
                options={"verify_signature": False}
            )
            user_id = token_payload.get("sub", "unknown")
            user_email = token_payload.get("email", "unknown")
            
            # Identify user in PostHog
            AnalyticsService.identify(
                distinct_id=user_id,
                properties={
                    "email": user_email
                }
            )
            
            # Track login
            AnalyticsService.capture(
                distinct_id=user_id,
                event="user_logged_in",
                properties={
                    "email": user_email
                }
            )
        except Exception:
            pass  # Don't fail if analytics fails
        
        # Store token in session (for simplicity, we'll use a cookie)
        # In production, use proper session management
        redirect = RedirectResponse(url="/admin", status_code=302)
        redirect.set_cookie(
            key="auth_token",
            value=tokens.get("access_token"),
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        return redirect
        
    except Exception as e:
        return render_template(
            "admin/login_error.html",
            request=request,
            error=f"Failed to exchange code for token: {str(e)}"
        )

@router.get("/logout")
async def logout(request: Request):
    """Logout and redirect to Auth0"""
    redirect = RedirectResponse(url="/", status_code=302)
    redirect.delete_cookie("auth_token")
    
    # Optionally redirect to Auth0 logout
    auth0_domain = Config.get_auth0_domain()
    if auth0_domain:
        # Ensure domain doesn't have protocol
        if auth0_domain.startswith("http://") or auth0_domain.startswith("https://"):
            auth0_domain = auth0_domain.replace("https://", "").replace("http://", "").strip("/")
        auth0_base_url = f"https://{auth0_domain}"
        logout_url = f"{auth0_base_url}/v2/logout"
        return RedirectResponse(url=logout_url)
    
    return redirect

