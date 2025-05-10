from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.utils.logger import get_logger

# Get logger for this module
logger = get_logger(__name__)

try:
    # Create connection URL
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    
    # Log connection attempt (masking password)
    masked_url = f"mysql+pymysql://{settings.DB_USER}:***@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    logger.info(f"Connecting to database: {masked_url}")
    
    # Create engine
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    logger.info("Database engine and session maker created successfully")
except Exception as e:
    logger.critical(f"Failed to connect to database: {str(e)}", exc_info=True)
    raise

Base = declarative_base()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    logger.debug("Database session opened")
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()
        logger.debug("Database session closed")