# app/main.py
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import time
import traceback
import os

from app.database import get_db, engine, Base
from app.utils.security import get_current_user
from app.utils.logger import get_logger
from app.config import settings
from app.api import auth, trending  # Import both routers correctly

# Get logger for this module
logger = get_logger(__name__)

# Create database tables
try:
    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.critical(f"Failed to create database tables: {str(e)}", exc_info=True)
    raise

# Create FastAPI application
app = FastAPI(
    title="Content Creator App",
    description="A web application for content creators",
    version="1.0.0",
    debug=settings.DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.debug(f"Request processed in {process_time:.4f} seconds: {request.method} {request.url.path}")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Request failed in {process_time:.4f} seconds: {request.method} {request.url.path}")
        logger.error(f"Error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request received: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response sent: {response.status_code}")
    return response

# Mount static files - FIXED VERSION
try:
    # Create the directory if it doesn't exist
    os.makedirs("app/static/js", exist_ok=True)
    os.makedirs("app/static/css", exist_ok=True)
    
    # Mount static files directly to root paths
    app.mount("/js", StaticFiles(directory="app/static/js"), name="js")
    app.mount("/css", StaticFiles(directory="app/static/css"), name="css")
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    logger.info("Static files mounted successfully")
except Exception as e:
    logger.error(f"Failed to mount static files: {str(e)}", exc_info=True)
    # Continue anyway, app should work but static files won't be available

# Include routers - Include both routers properly
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(trending.router, prefix="/api/trending", tags=["trending"])
logger.info("Auth and Trending routers included")

# Templates
templates = Jinja2Templates(directory="templates")
logger.info("Template engine initialized")

# Root route - redirect to login if not authenticated
@app.get("/")
async def root(request: Request, db: Session = Depends(get_db)):
    try:
        logger.debug("Serving index page")
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"Error serving index page: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )

# Dashboard route - requires authentication
@app.get("/dashboard")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        current_user = await get_current_user(request, db)
        logger.info(f"User {current_user.username} accessed dashboard")
        return templates.TemplateResponse("dashboard.html", {"request": request, "user": current_user})
    except HTTPException:
        logger.warning("Unauthorized access attempt to dashboard")
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logger.error(f"Error serving dashboard page: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )
    
# Trending page route
@app.get("/trending")
async def trending_page(request: Request, db: Session = Depends(get_db)):
    try:
        # Check if user is logged in, but make this optional
        try:
            current_user = await get_current_user(request, db)
            logger.info(f"User {current_user.username} accessed trending page")
            return templates.TemplateResponse("trending.html", {"request": request, "user": current_user})
        except HTTPException:
            # Allow access even if not logged in
            logger.info("Anonymous user accessed trending page")
            return templates.TemplateResponse("trending.html", {"request": request, "user": None})
    except Exception as e:
        logger.error(f"Error serving trending page: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )

# Error handler for 401 Unauthorized
@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def unauthorized_exception_handler(request, exc):
    logger.warning(f"Unauthorized access: {request.method} {request.url.path}")
    return RedirectResponse(url="/auth/login")

# Error handler for 500 Internal Server Error
@app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
async def internal_exception_handler(request, exc):
    logger.error(f"Internal server error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred"}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up")
    # You can add initialization code here, like connecting to external services

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")
    # You can add cleanup code here, like closing connections

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting application server")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)