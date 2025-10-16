"""
Configuration settings for Kiwiberry Cart application.
Loads environment variables with sensible defaults.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Application configuration class."""

    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Admin configuration - used for initial admin validation
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@kiwiberry.co')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

    # Data file paths
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
    USERS_FILE = os.path.join(DATA_DIR, 'users.json')

# Create a config instance for easy importing
config = Config()
