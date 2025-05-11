from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field, ValidationError
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.utils.security import get_password_hash, authenticate_user, create_access_token
from app.config import settings
from app.utils.logger import get_logger

# Get logger for this module
logger = get_logger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8)

# Render login page
@router.get("/login")
async def login_page(request: Request):
    logger.debug("Serving login page")
    return templates.TemplateResponse("auth/login.html", {"request": request})

# Render signup page
@router.get("/signup")
async def signup_page(request: Request):
    logger.debug("Serving signup page")
    return templates.TemplateResponse("auth/signup.html", {"request": request})

# Process login form
@router.post("/login")
async def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    remember: Optional[bool] = Form(False),
    db: Session = Depends(get_db)
):
    """
    Process login form submission
    """
    logger.info(f"Login attempt for user: {username}")
    
    try:
        user = authenticate_user(db, username, password)
        
        if not user:
            logger.warning(f"Failed login attempt for user: {username}")
            # Return to login page with error
            return templates.TemplateResponse(
                "auth/login.html", 
                {"request": request, "error": "Invalid username or password"}
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        logger.info(f"User {username} logged in successfully")
        
        # Create redirect response
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        
        # Set cookie with token
        response.set_cookie(
            key="access_token", 
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60 if remember else None,
            expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60 if remember else None,
            samesite="lax",
            secure=not settings.DEBUG
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Login error for user {username}: {str(e)}", exc_info=True)
        # Return to login page with error
        return templates.TemplateResponse(
            "auth/login.html", 
            {"request": request, "error": "An error occurred during login. Please try again."}
        )

@router.post("/signup")
async def create_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    logger.info(f"Signup attempt for username: {username}, email: {email}")
    try:
        # Check if passwords match
        if password != confirm_password:
            logger.warning(f"Signup failed: Passwords do not match for {username}")
            return templates.TemplateResponse(
                "auth/signup.html", 
                {"request": request, "error": "Passwords do not match"}
            )
        
        # Validate input data using Pydantic model
        try:
            user_data = UserCreate(
                username=username,
                email=email,
                full_name=full_name,
                password=password
            )
        except ValidationError as e:
            logger.warning(f"Signup validation error for {username}: {str(e)}")
            return templates.TemplateResponse(
                "auth/signup.html", 
                {"request": request, "error": f"Validation error: {str(e)}"}
            )
        
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            logger.warning(f"Signup failed: Username {username} already exists")
            return templates.TemplateResponse(
                "auth/signup.html", 
                {"request": request, "error": "Username already registered"}
            )
        
        # Check if email already exists
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            logger.warning(f"Signup failed: Email {email} already exists")
            return templates.TemplateResponse(
                "auth/signup.html", 
                {"request": request, "error": "Email already registered"}
            )
        
        # Create new user
        hashed_password = get_password_hash(password)
        db_user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"User created successfully: {username}")
        
        # Redirect to login page
        return RedirectResponse(url="/auth/login?registered=true", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logger.error(f"User creation error for {username}: {str(e)}", exc_info=True)
        return templates.TemplateResponse(
            "auth/signup.html", 
            {"request": request, "error": "An error occurred during registration. Please try again."}
        )

# Logout
@router.get("/logout")
async def logout():
    try:
        logger.info("User logged out")
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        response.delete_cookie("access_token")
        return response
    except Exception as e:
        logger.error(f"Logout error: {str(e)}", exc_info=True)
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

# OAuth2 token endpoint (for API access)
@router.post("/token")
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"API token request for user: {form_data.username}")
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            logger.warning(f"API token request failed for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        logger.info(f"API token created for user: {form_data.username}")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API token error for {form_data.username}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating the token",
        )