import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Install required packages if not already installed
try:
    from pydantic_settings import BaseSettings
except ImportError:
    print("Installing missing dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pydantic-settings"])

from app.database import engine, Base
from app.models.user import User
from app.utils.security import get_password_hash
from sqlalchemy.orm import sessionmaker

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

# Create an admin user
def create_admin():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # Check if admin already exists
    admin = db.query(User).filter(User.username == "admin").first()
    
    if admin:
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
    db.close()
    
    print("✅ Admin user created successfully")
    print("   Username: admin")
    print("   Password: admin123")
    print("   ⚠️ Please change the password after first login!")

if __name__ == "__main__":
    print("Initializing database...")
    create_tables()
    create_admin()
    print("✅ Database initialization complete")