# API Endpoints
API_BASE_URL = 'http://localhost:5000/api'
API_VERSION = 'v1'

# Authentication endpoints
AUTH_LOGIN = '/auth/login'
AUTH_REGISTER = '/auth/register'
AUTH_LOGOUT = '/auth/logout'
AUTH_REFRESH = '/auth/refresh'
AUTH_CHANGE_PASSWORD = '/auth/change-password'
AUTH_FORGOT_PASSWORD = '/auth/forgot-password'
AUTH_RESET_PASSWORD = '/auth/reset-password'
AUTH_VERIFY_EMAIL = '/auth/verify-email'

# User endpoints
USER_PROFILE = '/user/profile'
USER_PROJECTS = '/user/projects'
USER_NOTIFICATIONS = '/user/notifications'
USER_SETTINGS = '/user/settings'
USER_STATS = '/user/stats'

# Project endpoints
PROJECTS = '/projects'
PROJECT_UPLOAD = '/projects/upload'
PROJECT_DESCRIBE = '/projects/describe'
PROJECT_PREVIEW = '/projects/preview'
PROJECT_DOWNLOAD = '/projects/download'

# Staff endpoints
STAFF_PROFILE = '/staff/profile'
STAFF_PROJECTS = '/staff/projects'
STAFF_DASHBOARD = '/staff/dashboard'
STAFF_PERFORMANCE = '/staff/performance'

# Admin endpoints
ADMIN_DASHBOARD = '/admin/dashboard'
ADMIN_CLIENTS = '/admin/clients'
ADMIN_STAFF = '/admin/staff'
ADMIN_PROJECTS = '/admin/projects'
ADMIN_PAYMENTS = '/admin/payments'

# Payment endpoints
PAYMENTS_PROCESS = '/payments/process'
PAYMENTS_VERIFY = '/payments/verify'
PAYMENTS_HISTORY = '/payments/history'
PAYMENTS_STATUS = '/payments/status'

# File endpoints
FILES_UPLOAD = '/files/upload'
FILES_DOWNLOAD = '/files/download'
FILES_PREVIEW = '/files/preview'

# User roles
ROLE_USER = 'user'
ROLE_STAFF = 'staff'
ROLE_ADMIN = 'admin'

# Project statuses
STATUS_PENDING = 'pending'
STATUS_IN_PROGRESS = 'in_progress'
STATUS_COMPLETED = 'completed'
STATUS_PAYMENT_REQUIRED = 'payment_required'
STATUS_CANCELLED = 'cancelled'
STATUS_ARCHIVED = 'archived'

# Project priorities
PRIORITY_LOW = 'low'
PRIORITY_MEDIUM = 'medium'
PRIORITY_HIGH = 'high'

# Payment statuses
PAYMENT_PENDING = 'pending'
PAYMENT_PROCESSING = 'processing'
PAYMENT_COMPLETED = 'completed'
PAYMENT_FAILED = 'failed'
PAYMENT_REFUNDED = 'refunded'

# Research fields
FIELD_COMPUTER_SCIENCE = 'computer-science'
FIELD_ENGINEERING = 'engineering'
FIELD_MEDICINE = 'medicine'
FIELD_BUSINESS = 'business'
FIELD_EDUCATION = 'education'
FIELD_SOCIAL_SCIENCES = 'social-sciences'
FIELD_NATURAL_SCIENCES = 'natural-sciences'
FIELD_OTHER = 'other'

# File types
FILE_TYPE_PDF = 'application/pdf'
FILE_TYPE_IMAGE = 'image/jpeg'
FILE_TYPE_DOC = 'application/msword'
FILE_TYPE_DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

# File sizes
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5MB
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB

# Date formats
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
ISO_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

# Pagination
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
DEFAULT_PAGE = 1

# Sorting options
SORT_ASC = 'asc'
SORT_DESC = 'desc'

# Filter operators
FILTER_EQ = 'eq'
FILTER_NE = 'ne'
FILTER_GT = 'gt'
FILTER_GTE = 'gte'
FILTER_LT = 'lt'
FILTER_LTE = 'lte'
FILTER_LIKE = 'like'
FILTER_IN = 'in'
FILTER_NOT_IN = 'not_in'

# Validation rules
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 100
MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 200
MIN_DESCRIPTION_LENGTH = 10
MAX_DESCRIPTION_LENGTH = 10000

# JWT settings
JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days
JWT_ALGORITHM = 'HS256'

# Rate limiting
RATE_LIMIT_DEFAULT = 100  # requests per hour
RATE_LIMIT_AUTH = 10     # requests per 15 minutes
RATE_LIMIT_UPLOAD = 5     # requests per hour
RATE_LIMIT_PASSWORD_RESET = 3  # requests per hour

# Security
BCRYPT_ROUNDS = 12
SESSION_TIMEOUT = 3600  # 1 hour
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 900     # 15 minutes

# Email settings
EMAIL_FROM = 'noreply@projectmanagement.com'
EMAIL_SUBJECT_PREFIX = '[Project Management]'

# File upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'doc', 'docx']
ALLOWED_MIME_TYPES = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/gif',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]

# Database settings
DATABASE_POOL_SIZE = 10
DATABASE_POOL_TIMEOUT = 30
DATABASE_POOL_RECYCLE = 3600

# Cache settings
CACHE_TYPE = 'simple'
CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes

# Logging settings
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'logs/app.log'
LOG_MAX_BYTES = 10485760  # 10MB
LOG_BACKUP_COUNT = 5

# CORS settings
CORS_ORIGINS = ['http://localhost:5000', 'http://127.0.0.1:5000']
CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
CORS_HEADERS = ['Content-Type', 'Authorization', 'X-Requested-With']

# Notification types
NOTIFICATION_PROJECT_ASSIGNED = 'project_assigned'
NOTIFICATION_PROJECT_COMPLETED = 'project_completed'
NOTIFICATION_PAYMENT_RECEIVED = 'payment_received'
NOTIFICATION_SYSTEM_UPDATE = 'system_update'
NOTIFICATION_MESSAGE = 'message'
NOTIFICATION_REMINDER = 'reminder'

# Error codes
ERROR_VALIDATION = 'VALIDATION_ERROR'
ERROR_AUTHENTICATION = 'AUTHENTICATION_ERROR'
ERROR_AUTHORIZATION = 'AUTHORIZATION_ERROR'
ERROR_NOT_FOUND = 'NOT_FOUND'
ERROR_CONFLICT = 'CONFLICT'
ERROR_RATE_LIMIT = 'RATE_LIMIT_ERROR'
ERROR_SERVER_ERROR = 'SERVER_ERROR'

# HTTP status codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_CONFLICT = 409
HTTP_UNPROCESSABLE_ENTITY = 422
HTTP_TOO_MANY_REQUESTS = 429
HTTP_INTERNAL_SERVER_ERROR = 500

# Local storage keys
LS_ACCESS_TOKEN = 'access_token'
LS_REFRESH_TOKEN = 'refresh_token'
LS_USER_INFO = 'user_info'
LS_THEME = 'theme'
LS_LANGUAGE = 'language'

# Session storage keys
SS_AUTH_STATE = 'auth_state'
SS_REDIRECT_URL = 'redirect_url'

# Theme options
THEME_LIGHT = 'light'
THEME_DARK = 'dark'

# Language options
LANG_ENGLISH = 'en'
LANG_SPANISH = 'es'
LANG_FRENCH = 'fr'
LANG_GERMAN = 'de'

# Animation durations
ANIMATION_FAST = 200
ANIMATION_NORMAL = 300
ANIMATION_SLOW = 500

# Breakpoints
BREAKPOINT_SM = 640
BREAKPOINT_MD = 768
BREAKPOINT_LG = 1024
BREAKPOINT_XL = 1280

# Colors
COLOR_PRIMARY = '#3b82f6'
COLOR_SECONDARY = '#10b981'
COLOR_SUCCESS = '#22c55e'
COLOR_WARNING = '#f59e0b'
COLOR_ERROR = '#ef4444'
COLOR_INFO = '#6366f1'

# Status colors
COLOR_STATUS_PENDING = '#f59e0b'
COLOR_STATUS_IN_PROGRESS = '#3b82f6'
COLOR_STATUS_COMPLETED = '#22c55e'
COLOR_STATUS_CANCELLED = '#6b7280'
COLOR_STATUS_ARCHIVED = '#9ca3af'

# Payment methods
PAYMENT_CREDIT_CARD = 'credit_card'
PAYMENT_DEBIT_CARD = 'debit_card'
PAYMENT_PAYPAL = 'paypal'
PAYMENT_STRIPE = 'stripe'
PAYMENT_BANK_TRANSFER = 'bank_transfer'

# Export formats
EXPORT_PDF = 'pdf'
EXPORT_EXCEL = 'excel'
EXPORT_CSV = 'csv'
EXPORT_JSON = 'json'

# Time ranges
TIME_RANGE_TODAY = 'today'
TIME_RANGE_WEEK = 'week'
TIME_RANGE_MONTH = 'month'
TIME_RANGE_QUARTER = 'quarter'
TIME_RANGE_YEAR = 'year'

# Chart types
CHART_LINE = 'line'
CHART_BAR = 'bar'
CHART_PIE = 'pie'
CHART_AREA = 'area'
CHART_SCATTER = 'scatter'

# Default values
DEFAULT_CURRENCY = 'USD'
DEFAULT_LANGUAGE = 'en'
DEFAULT_THEME = 'light'
DEFAULT_PAGE_SIZE = 10
DEFAULT_SORT_ORDER = 'desc'

# Feature flags
FEATURE_EMAIL_NOTIFICATIONS = True
FEATURE_PUSH_NOTIFICATIONS = False
FEATURE_ANALYTICS = True
FEATURE_REPORTING = True
FEATURE_API_DOCS = True

# Integration settings
STRIPE_PUBLISHABLE_KEY = 'pk_test_placeholder'
STRIPE_SECRET_KEY = 'sk_test_placeholder'
PAYPAL_CLIENT_ID = 'paypal_test_placeholder'
PAYPAL_CLIENT_SECRET = 'paypal_test_placeholder'

# Development settings
DEBUG = True
TESTING = False
DEVELOPMENT = True
PRODUCTION = False

# Security headers
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Referrer-Policy': 'strict-origin-when-cross-origin'
}

# Database table names
TABLE_USERS = 'users'
TABLE_STAFF = 'staff'
TABLE_PROJECTS = 'projects'
TABLE_PAYMENTS = 'payments'
TABLE_NOTIFICATIONS = 'notifications'
TABLE_AUDIT_LOGS = 'audit_logs'

# Regex patterns
REGEX_EMAIL = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
REGEX_PHONE = r'^\+?1?\d{9,15}$'
REGEX_URL = r'^https?://(?:[-\w.]+(?:\.[a-z0-9.-]+\.[a-z]{2,})(?:/[-\w./?%&=]*)?$'
REGEX_PASSWORD = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]'
REGEX_SLUG = r'^[a-z0-9-]+$'

# Environment variables
ENV_FLASK_ENV = 'FLASK_ENV'
ENV_SECRET_KEY = 'SECRET_KEY'
ENV_DATABASE_URL = 'DATABASE_URL'
ENV_JWT_SECRET_KEY = 'JWT_SECRET_KEY'
ENV_MAIL_SERVER = 'MAIL_SERVER'
ENV_MAIL_PORT = 'MAIL_PORT'
ENV_MAIL_USERNAME = 'MAIL_USERNAME'
ENV_MAIL_PASSWORD = 'MAIL_PASSWORD'
ENV_MAIL_USE_TLS = 'MAIL_USE_TLS'
ENV_REDIS_URL = 'REDIS_URL'
ENV_CORS_ORIGINS = 'CORS_ORIGINS'

# Default configurations
DEFAULT_CONFIG = {
    'debug': False,
    'testing': False,
    'secret_key': 'dev-secret-key-change-in-production',
    'database_url': 'sqlite:///project_management.db',
    'jwt_secret_key': 'jwt-secret-key-change-in-production',
    'mail_server': 'localhost',
    'mail_port': 587,
    'mail_username': '',
    'mail_password': '',
    'mail_use_tls': True,
    'cors_origins': ['http://localhost:5000'],
    'upload_folder': 'uploads',
    'max_file_size': 16 * 1024 * 1024,
    'allowed_extensions': ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'doc', 'docx']
}

# Validation messages
VALIDATION_MESSAGES = {
    'required': 'This field is required',
    'email_invalid': 'Please enter a valid email address',
    'password_weak': 'Password must be at least 8 characters long',
    'name_invalid': 'Please enter a valid name',
    'phone_invalid': 'Please enter a valid phone number',
    'url_invalid': 'Please enter a valid URL',
    'file_too_large': 'File size must be less than 16MB',
    'file_type_invalid': 'File type not allowed',
    'date_invalid': 'Please enter a valid date',
    'time_invalid': 'Please enter a valid time'
}

# Success messages
SUCCESS_MESSAGES = {
    'login': 'Login successful',
    'logout': 'Logout successful',
    'register': 'Registration successful',
    'profile_updated': 'Profile updated successfully',
    'password_changed': 'Password changed successfully',
    'project_created': 'Project created successfully',
    'project_updated': 'Project updated successfully',
    'project_deleted': 'Project deleted successfully',
    'payment_processed': 'Payment processed successfully',
    'file_uploaded': 'File uploaded successfully'
}

# Error messages
ERROR_MESSAGES = {
    'login_failed': 'Login failed. Please check your credentials',
    'invalid_token': 'Invalid authentication token',
    'access_denied': 'Access denied',
    'not_found': 'Resource not found',
    'server_error': 'Internal server error',
    'validation_failed': 'Validation failed',
    'file_upload_failed': 'File upload failed',
    'payment_failed': 'Payment processing failed'
}
