import pytest
import os
import sys
import tempfile
from datetime import datetime, timedelta
import json

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__file__)))

# Test configuration
os.environ['PYTHONPATH'] = r'C:\Users\HomePC\Desktop\project-management-system\backend;' + os.environ.get('PYTHONPATH', '')
os.environ['FLASK_ENV'] = 'testing'
os.environ['TESTING'] = 'True'
os.environ['SECRET_KEY'] = 'test-secret-key'
os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['UPLOAD_FOLDER'] = tempfile.mkdtemp()
os.environ['MAX_CONTENT_LENGTH'] = 16777216

# Test database configuration
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
os.environ['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'

# Test email configuration
os.environ['MAIL_SERVER'] = 'localhost'
os.environ['MAIL_PORT'] = '1025'
os.environ['MAIL_USE_TLS'] = 'False'
os.environ['MAIL_USERNAME'] = 'test@example.com'
os.environ['MAIL_PASSWORD'] = 'test-password'
os.environ['MAIL_DEFAULT_SENDER'] = 'test@example.com'

# Test Redis configuration
os.environ['REDIS_URL'] = 'redis://localhost:6379/0'

# Test security configuration
os.environ['JWT_ACCESS_TOKEN_EXPIRES'] = '3600'
os.environ['JWT_REFRESH_TOKEN_EXPIRES'] = '2592000'
os.environ['BCRYPT_LOG_ROUNDS'] = '12'

# Application configuration
os.environ['DEBUG'] = 'True'
os.environ['TESTING'] = 'True'

# Create temporary upload directory for tests
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__file__)), 'test_uploads'), exist_ok=True)
