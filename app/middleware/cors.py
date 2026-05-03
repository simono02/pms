from flask import request, jsonify, current_app
from functools import wraps
import re

class CORSMiddleware:
    def __init__(self, app):
        self.app = app
        self.setup_cors()
    
    def setup_cors(self):
        """Setup CORS middleware"""
        
        @self.app.after_request
        def add_cors_headers(response):
            # Get origin from request
            origin = request.headers.get('Origin')
            
            # Check if origin is allowed
            if self.is_origin_allowed(origin):
                response.headers['Access-Control-Allow-Origin'] = origin
            else:
                # Allow credentials for same-origin requests
                if request.headers.get('Host') == self.extract_host_from_origin(origin):
                    response.headers['Access-Control-Allow-Origin'] = origin
            
            # Allow credentials
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            
            # Allow common headers
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = (
                'Content-Type, Authorization, X-Requested-With, '
                'X-CSRF-Token, X-API-Key, Accept, Origin, '
                'Cache-Control, Pragma, Expires'
            )
            
            # Expose headers for client
            response.headers['Access-Control-Expose-Headers'] = (
                'X-Total-Count, X-Page-Count, X-Per-Page, '
                'X-Request-ID, X-Response-Time'
            )
            
            # Cache control for preflight requests
            if request.method == 'OPTIONS':
                response.headers['Access-Control-Max-Age'] = '86400'  # 24 hours
                response.status_code = 200
            
            return response
    
    def is_origin_allowed(self, origin):
        """Check if origin is allowed"""
        if not origin:
            return True  # Allow same-origin requests
        
        # Get allowed origins from config
        allowed_origins = current_app.config.get('CORS_ORIGINS', [])
        
        if not allowed_origins:
            # Default to allowing same origin
            return self.is_same_origin(origin)
        
        # Check against allowed origins
        for allowed_origin in allowed_origins:
            if self.match_origin(origin, allowed_origin):
                return True
        
        return False
    
    def is_same_origin(self, origin):
        """Check if origin is same as request host"""
        try:
            origin_host = self.extract_host_from_origin(origin)
            request_host = request.headers.get('Host', '')
            return origin_host == request_host
        except:
            return False
    
    def extract_host_from_origin(self, origin):
        """Extract host from origin URL"""
        try:
            # Remove protocol
            origin = re.sub(r'^https?://', '', origin)
            # Remove port if present
            origin = re.sub(r':\d+$', '', origin)
            # Remove path
            return origin.split('/')[0]
        except:
            return origin
    
    def match_origin(self, origin, pattern):
        """Match origin against pattern"""
        if not pattern:
            return False
        
        # Exact match
        if pattern == origin:
            return True
        
        # Wildcard matching
        if '*' in pattern:
            # Convert wildcard pattern to regex
            regex_pattern = pattern.replace('*', '.*').replace('?', '.')
            return re.match(f'^{regex_pattern}$', origin)
        
        return False
    
    def get_allowed_origins(self):
        """Get list of allowed origins"""
        return current_app.config.get('CORS_ORIGINS', [])
    
    def add_origin(self, origin):
        """Add origin to allowed origins"""
        allowed_origins = self.get_allowed_origins()
        
        if origin not in allowed_origins:
            allowed_origins.append(origin)
            current_app.config['CORS_ORIGINS'] = allowed_origins
            return True
        
        return False
    
    def remove_origin(self, origin):
        """Remove origin from allowed origins"""
        allowed_origins = self.get_allowed_origins()
        
        if origin in allowed_origins:
            allowed_origins.remove(origin)
            current_app.config['CORS_ORIGINS'] = allowed_origins
            return True
        
        return False
    
    def set_allowed_origins(self, origins):
        """Set allowed origins"""
        current_app.config['CORS_ORIGINS'] = origins

# Create CORS middleware instance
def cors_middleware(app):
    """Apply CORS middleware to Flask app"""
    return CORSMiddleware(app)

# Decorators for CORS
def allow_cors(f):
    """Decorator to allow CORS for specific routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Add CORS headers to response
        response = f(*args, **kwargs)
        
        if hasattr(response, 'headers'):
            origin = request.headers.get('Origin')
            
            if origin:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
            
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = (
                'Content-Type, Authorization, X-Requested-With, '
                'X-CSRF-Token, X-API-Key, Accept, Origin'
            )
        
        return response
    
    return decorated_function

def allow_origins(*origins):
    """Decorator to allow specific origins"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)
            
            if hasattr(response, 'headers'):
                request_origin = request.headers.get('Origin')
                
                # Check if requested origin is allowed
                for origin in origins:
                    if origin == request_origin or origin == '*':
                        response.headers['Access-Control-Allow-Origin'] = request_origin
                        break
                    elif origin.startswith('.*') and request_origin.endswith(origin[1:]):
                        response.headers['Access-Control-Allow-Origin'] = request_origin
                        break
                
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = (
                    'Content-Type, Authorization, X-Requested-With, '
                    'X-CSRF-Token, X-API-Key, Accept, Origin'
                )
            
            return response
        
        return decorated_function
    return decorator

def allow_all_origins(f):
    """Decorator to allow all origins"""
    return allow_origins('*')(f)

def allow_localhost(f):
    """Decorator to allow localhost origins"""
    return allow_origins('http://localhost:*', 'http://127.0.0.1:*')(f)

def allow_production_origins(f):
    """Decorator to allow production origins"""
    return allow_origins(
        'https://yourdomain.com',
        'https://www.yourdomain.com'
    )(f)

def cors_preflight(f):
    """Decorator to handle CORS preflight requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Handle preflight requests
        if request.method == 'OPTIONS':
            response = jsonify({'message': 'CORS preflight request successful'})
            
            origin = request.headers.get('Origin')
            
            if origin:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
            
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = (
                'Content-Type, Authorization, X-Requested-With, '
                'X-CSRF-Token, X-API-Key, Accept, Origin'
            )
            response.headers['Access-Control-Max-Age'] = '86400'
            
            return response
        
        return f(*args, **kwargs)
    
    return decorated_function

def expose_headers(*headers):
    """Decorator to expose specific headers"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)
            
            if hasattr(response, 'headers'):
                response.headers['Access-Control-Expose-Headers'] = ', '.join(headers)
            
            return response
        
        return decorated_function
    return decorator

def vary_origin(f):
    """Decorator to add Vary header"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        if hasattr(response, 'headers'):
            response.headers['Vary'] = 'Origin'
        
        return response
    return decorated_function

def cache_control(max_age=3600, public=False):
    """Decorator to add cache control headers"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)
            
            if hasattr(response, 'headers'):
                cache_directive = 'public' if public else 'private'
                response.headers['Cache-Control'] = f'{cache_directive}, max-age={max_age}'
            
            return response
        return decorated_function
    return decorator

def no_cache(f):
    """Decorator to disable caching"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        if hasattr(response, 'headers'):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        return response
    return decorated_function

def etag(f):
    """Decorator to add ETag header"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        if hasattr(response, 'headers'):
            # Generate ETag based on response content
            content = response.get_data()
            if content:
                import hashlib
                etag = hashlib.md5(content).hexdigest()
                response.headers['ETag'] = etag
        
        return response
    return decorator

def last_modified(f):
    """Decorator to add Last-Modified header"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        if hasattr(response, 'headers'):
            response.headers['Last-Modified'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        return response
    return decorator
