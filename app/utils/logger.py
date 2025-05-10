import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

def setup_logger(name, log_file, level=logging.INFO):
    """Function to set up a logger with file and console handlers"""
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # Prevent duplicate logs
    
    # Only add handlers if not already added to avoid duplicates
    if not logger.handlers:
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        
        # Create file handler (rotating to avoid huge log files)
        file_handler = RotatingFileHandler(
            os.path.join("logs", log_file),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger

# Main application logger
app_logger = setup_logger('app', 'app.log')

# Create specialized loggers for different modules
auth_logger = setup_logger('auth', 'auth.log')
db_logger = setup_logger('db', 'db.log')
security_logger = setup_logger('security', 'security.log')

# Function to get an appropriate logger based on module name
def get_logger(module_name):
    if 'auth' in module_name.lower():
        return auth_logger
    elif 'database' in module_name.lower():
        return db_logger
    elif 'security' in module_name.lower():
        return security_logger
    else:
        return app_logger