# Flask Web Application Configuration
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Flask application configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Shopify configuration
    SHOPIFY_SHOP_DOMAIN = os.environ.get('SHOPIFY_SHOP_DOMAIN')
    SHOPIFY_ACCESS_TOKEN = os.environ.get('SHOPIFY_ACCESS_TOKEN')
    STORE_CREATION_MODE = os.environ.get('STORE_CREATION_MODE', 'demo')  # 'demo' or 'real'
    
    # Application settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    JSONIFY_PRETTYPRINT_REGULAR = True
    
    # CORS settings
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5000']

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
