from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from pathlib import Path
from dotenv import load_dotenv
from app.core.templates import render_template
from app.services.analytics import AnalyticsService
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle app startup and shutdown"""
    # Startup
    yield
    # Shutdown
    AnalyticsService.shutdown()

# Create FastAPI app
app = FastAPI(title="FieldPal.ai", version="1.0.0", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add analytics middleware
from app.middleware.analytics import AnalyticsMiddleware
app.add_middleware(AnalyticsMiddleware)

# Mount static files
BASE_DIR = Path(__file__).resolve().parent.parent
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Import routers
from app.routers import home, about, contact, admin, api, auth_web

# Include routers
app.include_router(home.router)
app.include_router(about.router)
app.include_router(contact.router)
app.include_router(auth_web.router, prefix="/auth")
app.include_router(admin.router, prefix="/admin")
app.include_router(api.router, prefix="/api")

# Custom 404 handler
@app.exception_handler(StarletteHTTPException)
async def not_found_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return render_template("404.html", request=request)
    # Re-raise other HTTP exceptions
    raise exc

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

