import sys
import os
import traceback

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Install required packages if not already installed
try:
    from pydantic_settings import BaseSettings
except ImportError:
    print("Installing missing dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pydantic-settings"])

# Import after ensuring dependencies are installed
try:
    from app.database import engine, Base, SessionLocal
    from app.models.user import User
    from app.utils.security import get_password_hash
    from app.utils.logger import setup_logger
    from sqlalchemy.orm import sessionmaker
except ImportError as e:
    print(f"Error importing modules: {str(e)}")
    print("Make sure you're running this script from the project root directory")
    sys.exit(1)

# Setup logger for this script
logger = setup_logger("init_db", "init_db.log")

# Create tables
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        print("✅ Database tables created successfully")
    except Exception as e:
        error_msg = f"❌ Failed to create database tables: {str(e)}"
        logger.error(error_msg, exc_info=True)
        print(error_msg)
        print(traceback.format_exc())
        sys.exit(1)

# Create an admin user
def create_admin():
    try:
        db = SessionLocal()
        
        # Check if admin already exists
        admin = db.query(User).filter(User.username == "admin").first()
        
        if admin:
            logger.info("⚠️ Admin user already exists")
            print("⚠️ Admin user already exists")
            return
        
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@example.com",
            full_name="Administrator",
            hashed_password=get_password_hash("admin123"),
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        logger.info("✅ Admin user created successfully")
        print("✅ Admin user created successfully")
        print("   Username: admin")
        print("   Password: admin123")
        print("   ⚠️ Please change the password after first login!")
    except Exception as e:
        error_msg = f"❌ Failed to create admin user: {str(e)}"
        logger.error(error_msg, exc_info=True)
        print(error_msg)
        print(traceback.format_exc())
    finally:
        db.close()

if __name__ == "__main__":
    try:
        logger.info("Initializing database...")
        print("Initializing database...")
        create_tables()
        create_admin()
        logger.info("✅ Database initialization complete")
        print("✅ Database initialization complete")
    except Exception as e:
        error_msg = f"❌ Unhandled error during database initialization: {str(e)}"
        logger.critical(error_msg, exc_info=True)
        print(error_msg)
        print(traceback.format_exc())
        sys.exit(1)