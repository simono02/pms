# backend/config.py
import os
from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    """Base configuration"""

    # App settings
    DEBUG   = os.getenv('DEBUG', 'False').lower() in ['true', 'on', '1']
    TESTING = os.getenv('TESTING', 'False').lower() in ['true', 'on', '1']

    # App info
    APP_NAME     = os.getenv('APP_NAME', 'ResearchPro')
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5000')

    # Security
    SECRET_KEY        = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY    = os.getenv('JWT_SECRET_KEY')
    BCRYPT_LOG_ROUNDS = int(os.getenv('BCRYPT_LOG_ROUNDS', 12))

    # Database
    SQLALCHEMY_DATABASE_URI    = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO            = DEBUG

    # JWT Token Expiration
    JWT_ACCESS_TOKEN_EXPIRES  = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000)))

    # File storage
    UPLOAD_FOLDER       = os.getenv('UPLOAD_FOLDER', 'uploads')
    EXTRACT_DIR         = os.getenv('EXTRACT_DIR', 'storage/extracted')
    REPORT_DIR          = os.getenv('REPORT_DIR', 'storage/reports')
    MAX_CONTENT_LENGTH  = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))
    ALLOWED_EXTENSIONS  = {'pdf', 'doc', 'docx', 'txt'}

    # Email
    MAIL_SERVER         = os.getenv('MAIL_SERVER')
    MAIL_PORT           = int(os.getenv('MAIL_PORT', 465))
    MAIL_USERNAME       = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD       = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS        = os.getenv('MAIL_USE_TLS', 'false').lower() in ['true', 'on', '1']
    MAIL_USE_SSL        = os.getenv('MAIL_USE_SSL', 'true').lower() in ['true', 'on', '1']
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5000').split(',')

    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # Payment Gateway
    PAYMENT_GATEWAY_URL = os.getenv('PAYMENT_GATEWAY_URL')
    PAYMENT_PUBLIC_KEY  = os.getenv('PAYMENT_PUBLIC_KEY')
    PAYMENT_PRIVATE_KEY = os.getenv('PAYMENT_PRIVATE_KEY')

    @staticmethod
    def init_app(app):
        Path(Config.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
        Path(Config.EXTRACT_DIR).mkdir(parents=True, exist_ok=True)
        Path(Config.REPORT_DIR).mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        assert os.getenv('SECRET_KEY'),                 'SECRET_KEY must be set in production'
        assert os.getenv('JWT_SECRET_KEY'),             'JWT_SECRET_KEY must be set in production'
        assert os.getenv('SQLALCHEMY_DATABASE_URI'),    'SQLALCHEMY_DATABASE_URI must be set in production'
        assert os.getenv('MAIL_SERVER'),                'MAIL_SERVER must be set in production'
        assert os.getenv('MAIL_USERNAME'),              'MAIL_USERNAME must be set in production'
        assert os.getenv('MAIL_PASSWORD'),              'MAIL_PASSWORD must be set in production'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URI',
        'postgresql://postgres:root@localhost:5432/research_db_test'
    )
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'testing':     TestingConfig,
    'default':     DevelopmentConfig,
}