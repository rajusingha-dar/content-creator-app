from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.utils.logger import get_logger

# Get logger for this module
logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Verify a password against a hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}", exc_info=True)
        return False

def get_password_hash(password):
    """Generate a password hash"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing error: {str(e)}", exc_info=True)
        raise

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate a user with username and password"""
    try:
        logger.info(f"Authentication attempt for user: {username}")
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            logger.warning(f"Authentication failed: User {username} not found")
            return False
            
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: Invalid password for user {username}")
            return False
            
        logger.info(f"Authentication successful for user: {username}")
        return user
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}", exc_info=True)
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a new JWT access token"""
    try:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        logger.debug(f"Access token created for user: {data.get('sub', 'unknown')}")
        
        return encoded_jwt
    except Exception as e:
        logger.error(f"Token creation error: {str(e)}", exc_info=True)
        raise

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Get the current user from the JWT token in the cookie"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Get token from cookie
        token = request.cookies.get("access_token")
        if not token:
            logger.warning("Authentication failed: No access token in cookies")
            raise credentials_exception
        
        # Remove "Bearer " prefix if present
        if token.startswith("Bearer "):
            token = token[7:]
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                logger.warning("Authentication failed: No username in token payload")
                raise credentials_exception
        except JWTError as e:
            logger.warning(f"JWT verification failed: {str(e)}")
            raise credentials_exception
            
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            logger.warning(f"Authentication failed: User {username} from token not found in database")
            raise credentials_exception
            
        logger.debug(f"User {username} authenticated successfully via token")
        return user
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}", exc_info=True)
        raise credentials_exception