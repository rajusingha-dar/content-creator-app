from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from app.database import get_db
from app.models.user import User
from app.utils.security import get_password_hash, authenticate_user, create_access_token
from app.config import settings

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
    return templates.TemplateResponse("auth/login.html", {"request": request})

# Render signup page
@router.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse("auth/signup.html", {"request": request})


# Process login form
@router.post("/login")
async def login(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse(
            "auth/login.html", 
            {"request": {"headers": {}}, "error": "Invalid username or password"}
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    
    return response

# Process login form
# @router.post("/login")
# async def login(
#     response: Response,
#     username: str = Form(...),
#     password: str = Form(...),
#     db: Session = Depends(get_db)
# ):
#     user = authenticate_user(db, username, password)
#     if not user:
#         return templates.TemplateResponse(
#             "auth/login.html", 
#             {"request": {"headers": {}}, "error": "Invalid username or password"}
#         )
    
#     access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
    
#     response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
#     response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    
#     return response


@router.post("/signup")
async def create_user(
    username: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if passwords match
    if password != confirm_password:
        return templates.TemplateResponse(
            "auth/signup.html", 
            {"request": {"headers": {}}, "error": "Passwords do not match"}
        )
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return templates.TemplateResponse(
            "auth/signup.html", 
            {"request": {"headers": {}}, "error": "Username already registered"}
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        return templates.TemplateResponse(
            "auth/signup.html", 
            {"request": {"headers": {}}, "error": "Email already registered"}
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
    
    # Redirect to login page
    return RedirectResponse(url="/auth/login?registered=true", status_code=status.HTTP_303_SEE_OTHER)

# Process signup form
# @router.post("/signup")
# async def create_user(
#     username: str = Form(...),
#     email: str = Form(...),
#     full_name: str = Form(...),
#     password: str = Form(...),
#     db: Session = Depends(get_db)
# ):
#     # Check if username already exists
#     existing_user = db.query(User).filter(User.username == username).first()
#     if existing_user:
#         return templates.TemplateResponse(
#             "auth/signup.html", 
#             {"request": {"headers": {}}, "error": "Username already registered"}
#         )
    
#     # Check if email already exists
#     existing_email = db.query(User).filter(User.email == email).first()
#     if existing_email:
#         return templates.TemplateResponse(
#             "auth/signup.html", 
#             {"request": {"headers": {}}, "error": "Email already registered"}
#         )
    
#     # Create new user
#     hashed_password = get_password_hash(password)
#     db_user = User(
#         username=username,
#         email=email,
#         full_name=full_name,
#         hashed_password=hashed_password
#     )
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
    
#     # Redirect to login page
#     return RedirectResponse(url="/auth/login?registered=true", status_code=status.HTTP_303_SEE_OTHER)

# Logout
@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response


# OAuth2 token endpoint (for API access)
@router.post("/token")
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# OAuth2 token endpoint (for API access)
# @router.post("/token")
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     user = authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}