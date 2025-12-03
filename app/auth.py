from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from jose.utils import base64url_decode
from typing import Optional, Dict
import httpx
import json
from functools import lru_cache
from app.core.config import Config

security = HTTPBearer(auto_error=False)

# Auth0 configuration
AUTH0_ALGORITHMS = ["RS256"]

# Cache for JWKS
_jwks_cache = None

async def get_jwks():
    """Fetch JWKS from Auth0 and cache it"""
    global _jwks_cache
    
    if _jwks_cache is None:
        auth0_domain = Config.get_auth0_domain()
        # Ensure domain doesn't have protocol
        if auth0_domain.startswith("http://") or auth0_domain.startswith("https://"):
            auth0_domain = auth0_domain.replace("https://", "").replace("http://", "").strip("/")
        jwks_url = f"https://{auth0_domain}/.well-known/jwks.json"
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url)
            response.raise_for_status()
            _jwks_cache = response.json()
    
    return _jwks_cache

def get_rsa_key(token: str, jwks: dict):
    """Get RSA key from JWKS for token verification"""
    from jose import jwk
    from jose.constants import ALGORITHMS
    
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = None
    
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = key
            break
    
    if not rsa_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to find appropriate key"
        )
    
    # Convert JWK to RSA public key using jose
    public_key = jwk.construct(rsa_key, algorithm=ALGORITHMS.RS256)
    
    return public_key

def get_token_from_request(
    credentials: Optional[HTTPAuthorizationCredentials] = None,
    auth_token: Optional[str] = None
) -> Optional[str]:
    """Get token from either Authorization header or cookie"""
    # Try Bearer token first
    if credentials:
        return credentials.credentials
    # Try cookie
    if auth_token:
        return auth_token
    return None

def get_token_from_request_depends(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_token: Optional[str] = Cookie(None)
) -> Optional[str]:
    """Get token from request using FastAPI dependencies"""
    return get_token_from_request(credentials, auth_token)

async def verify_token(token: str) -> Dict:
    """Verify Auth0 JWT token"""
    auth0_domain = Config.get_auth0_domain()
    auth0_audience = Config.get_auth0_audience()
    
    if not auth0_domain or not auth0_audience:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth0 configuration missing"
        )
    
    try:
        # Get JWKS
        jwks = await get_jwks()
        
        # Get RSA key
        public_key = get_rsa_key(token, jwks)
        
        # Ensure domain doesn't have protocol
        if auth0_domain.startswith("http://") or auth0_domain.startswith("https://"):
            auth0_domain = auth0_domain.replace("https://", "").replace("http://", "").strip("/")
        
        # Decode and verify token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=AUTH0_ALGORITHMS,
            audience=auth0_audience,
            issuer=f"https://{auth0_domain}/"
        )
        
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )

async def get_current_user_optional_from_request(request: Request) -> Optional[Dict]:
    """Get current authenticated user from request, returns None if not authenticated"""
    # Try to get token from cookie
    auth_token = request.cookies.get("auth_token")
    
    # Try to get token from Authorization header
    auth_header = request.headers.get("Authorization")
    credentials = None
    if auth_header and auth_header.startswith("Bearer "):
        from fastapi.security import HTTPAuthorizationCredentials
        token_value = auth_header.replace("Bearer ", "")
        # Create a simple object to mimic HTTPAuthorizationCredentials
        class SimpleCredentials:
            def __init__(self, token):
                self.credentials = token
        credentials = SimpleCredentials(token_value)
    
    token = get_token_from_request(credentials, auth_token)
    
    if not token:
        return None
    
    try:
        return await verify_token(token)
    except Exception:
        return None

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_token: Optional[str] = Cookie(None)
) -> Dict:
    """Get current authenticated user from token (header or cookie) - for use as dependency"""
    token = get_token_from_request(credentials, auth_token)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    return await verify_token(token)

def require_auth(user: Dict = Depends(get_current_user)) -> Dict:
    """Dependency to require authentication"""
    return user

