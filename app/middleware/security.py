from flask import request, jsonify, current_app
from functools import wraps
import re
import html
import os
import hashlib
import secrets
from urllib.parse import urlparse

class SecurityMiddleware:
    def __init__(self, app):
        self.app = app
        self.setup_security_headers()
        self.setup_input_validation()
        self.setup_csrf_protection()
    
    def setup_security_headers(self):
        """Setup security headers for all responses"""
        
        @self.app.after_request
        def add_security_headers(response):
            # Security headers
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https:; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none';"
            )
            response.headers['Permissions-Policy'] = (
                'geolocation=(), microphone=(), camera=(), '
                'payment=(), usb=(), magnetometer=(), '
                'gyroscope=(), fullscreen=(self)'
            )
            
            # Remove server information
            response.headers['Server'] = 'ProjectManagementSystem'
            
            return response
    
    def setup_input_validation(self):
        """Setup input validation middleware"""
        
        @self.app.before_request
        def validate_input():
            # Skip validation for certain endpoints
            skip_validation = [
                '/api/auth/login',
                '/api/auth/register',
                '/api/health'
            ]
            
            if request.path in skip_validation:
                return None
            
            # Validate JSON input
            if request.is_json and request.get_json():
                self.validate_json_input(request.get_json())
            
            # Validate form input
            if request.form:
                self.validate_form_input(request.form)
            
            # Validate query parameters
            if request.args:
                self.validate_query_params(request.args)
            
            return None
    
    def setup_csrf_protection(self):
        """Setup CSRF protection"""
        
        @self.app.before_request
        def csrf_protection():
            # Skip CSRF for GET, HEAD, OPTIONS requests
            if request.method in ['GET', 'HEAD', 'OPTIONS']:
                return None
            
            # Skip CSRF for API endpoints that use JWT
            if request.path.startswith('/api/'):
                return None
            
            # Check CSRF token for state-changing requests
            if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                csrf_token = request.headers.get('X-CSRF-Token')
                session_token = session.get('csrf_token')
                
                if not csrf_token or not session_token or csrf_token != session_token:
                    return jsonify({
                        'error': 'CSRF token missing or invalid',
                        'message': 'Please provide a valid CSRF token'
                    }), 403
            
            return None
    
    def validate_json_input(self, data):
        """Validate JSON input for security threats"""
        if not isinstance(data, dict):
            return
        
        # Check for potential XSS in string values
        for key, value in data.items():
            if isinstance(value, str):
                # Check for script tags
                if '<script' in value.lower():
                    raise ValueError(f"Potential XSS attack detected in field: {key}")
                
                # Check for SQL injection patterns
                sql_patterns = [
                    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
                    r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
                    r"(--|#|/\*|\*/)",
                    r"(\b(UNION|JOIN)\s+SELECT\b)"
                ]
                
                for pattern in sql_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        raise ValueError(f"Potential SQL injection detected in field: {key}")
                
                # Check for path traversal
                if '../' in value or '..\\' in value:
                    raise ValueError(f"Potential path traversal attack detected in field: {key}")
    
    def validate_form_input(self, form_data):
        """Validate form input for security threats"""
        for key, value in form_data.items():
            if isinstance(value, str):
                # HTML encode to prevent XSS
                form_data[key] = html.escape(value)
                
                # Check for dangerous patterns
                dangerous_patterns = [
                    r'<script[^>]*>.*?</script>',
                    r'javascript:',
                    r'on\w+\s*=',
                    r'<iframe[^>]*>',
                    r'<object[^>]*>',
                    r'<embed[^>]*>'
                ]
                
                for pattern in dangerous_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        raise ValueError(f"Potential XSS attack detected in field: {key}")
    
    def validate_query_params(self, query_params):
        """Validate query parameters"""
        for key, value in query_params.items():
            if isinstance(value, str):
                # URL encode to prevent injection
                query_params[key] = html.escape(value)
                
                # Check for dangerous patterns
                if '<' in value or '>' in value:
                    raise ValueError(f"Invalid characters in query parameter: {key}")
                
                # Check for path traversal
                if '../' in value or '..\\' in value:
                    raise ValueError(f"Potential path traversal in query parameter: {key}")
    
    def sanitize_filename(self, filename):
        """Sanitize filename to prevent directory traversal"""
        # Remove directory traversal characters
        filename = re.sub(r'[\\/]', '_', filename)
        
        # Remove dangerous characters
        filename = re.sub(r'[<>:"|?*]', '', filename)
        
        # Limit filename length
        filename = filename[:255]
        
        return filename
    
    def generate_csrf_token(self):
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    def validate_file_upload(self, file):
        """Validate uploaded file for security"""
        if not file:
            return False, "No file provided"
        
        # Check file size
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
        if file.content_length > max_size:
            return False, "File too large"
        
        # Check file extension
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', ['pdf'])
        if file.filename:
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                return False, f"File type {file_ext} not allowed"
        
        # Check file content type
        if file.content_type:
            allowed_mime_types = ['application/pdf']
            if file.content_type not in allowed_mime_types:
                return False, f"MIME type {file.content_type} not allowed"
        
        return True, "File is valid"
    
    def hash_password(self, password):
        """Hash password using secure method"""
        import bcrypt
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password, hashed):
        """Verify password against hash"""
        import bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_secure_token(self, length=32):
        """Generate secure random token"""
        return secrets.token_urlsafe(length)
    
    def encrypt_sensitive_data(self, data, key=None):
        """Encrypt sensitive data"""
        from cryptography.fernet import Fernet
        import base64
        
        if key is None:
            key = current_app.config.get('ENCRYPTION_KEY')
        
        if not key:
            raise ValueError("Encryption key not configured")
        
        f = Fernet(key.encode())
        encrypted_data = f.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt_sensitive_data(self, encrypted_data, key=None):
        """Decrypt sensitive data"""
        from cryptography.fernet import Fernet
        import base64
        
        if key is None:
            key = current_app.config.get('ENCRYPTION_KEY')
        
        if not key:
            raise ValueError("Encryption key not configured")
        
        f = Fernet(key.encode())
        decoded_data = base64.b64decode(encrypted_data.encode('utf-8'))
        decrypted_data = f.decrypt(decoded_data)
        return decrypted_data.decode('utf-8')
    
    def validate_url(self, url):
        """Validate URL for security"""
        try:
            parsed = urlparse(url)
            
            # Check for dangerous protocols
            dangerous_protocols = ['javascript:', 'data:', 'vbscript:', 'file:']
            if parsed.scheme in dangerous_protocols:
                return False, "Dangerous protocol not allowed"
            
            # Check for XSS in URL
            if '<' in url or '>' in url:
                return False, "Invalid characters in URL"
            
            return True, "URL is valid"
            
        except Exception:
            return False, "Invalid URL format"
    
    def sanitize_html(self, html_content):
        """Sanitize HTML content to prevent XSS"""
        import bleach
        
        # Define allowed HTML tags and attributes
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a']
        allowed_attributes = {
            'a': ['href', 'title'],
            '*': ['class']
        }
        
        return bleach.clean(html_content, tags=allowed_tags, attributes=allowed_attributes)
    
    def check_rate_limit(self, identifier, limit=100, window=3600):
        """Check rate limit for identifier"""
        # This is a simplified implementation
        # In production, you'd use Redis or a proper rate limiting library
        
        import time
        
        current_time = int(time.time())
        window_start = current_time - window
        
        # Store rate limit data in session (simplified)
        if 'rate_limits' not in session:
            session['rate_limits'] = {}
        
        if identifier not in session['rate_limits']:
            session['rate_limits'][identifier] = []
        
        # Clean old entries
        session['rate_limits'][identifier] = [
            timestamp for timestamp in session['rate_limits'][identifier]
            if timestamp > window_start
        ]
        
        # Check current count
        if len(session['rate_limits'][identifier]) >= limit:
            return False, f"Rate limit exceeded. Max {limit} requests per {window} seconds."
        
        # Add current request
        session['rate_limits'][identifier].append(current_time)
        
        return True, "Rate limit check passed"
    
    def log_security_event(self, event_type, details, severity='medium'):
        """Log security events"""
        log_data = {
            'timestamp': time.time(),
            'event_type': event_type,
            'severity': severity,
            'details': details,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'path': request.path,
            'method': request.method
        }
        
        current_app.logger.warning(f"Security Event: {event_type} - {details}")
        
        # In production, you might send this to a security monitoring service
        return log_data

# Create security middleware instance
def security_middleware(app):
    """Apply security middleware to Flask app"""
    return SecurityMiddleware(app)

# Decorators for security
def require_https(f):
    """Decorator to require HTTPS"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_secure:
            return jsonify({
                'error': 'HTTPS required',
                'message': 'Please use HTTPS for this request'
            }), 403
        return f(*args, **kwargs)
    return decorated_function

def validate_csrf(f):
    """Decorator to validate CSRF token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            csrf_token = request.headers.get('X-CSRF-Token')
            session_token = session.get('csrf_token')
            
            if not csrf_token or not session_token or csrf_token != session_token:
                return jsonify({
                    'error': 'CSRF token missing or invalid',
                    'message': 'Please provide a valid CSRF token'
                }), 403
        
        return f(*args, **kwargs)
    return decorated_function

def sanitize_input(f):
    """Decorator to sanitize input"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Sanitize request data
        if request.is_json and request.get_json():
            try:
                SecurityMiddleware(current_app).validate_json_input(request.get_json())
            except ValueError as e:
                return jsonify({
                    'error': 'Invalid input',
                    'message': str(e)
                }), 400
        
        return f(*args, **kwargs)
    return decorated_function
