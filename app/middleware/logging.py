import logging
import json
import time
from datetime import datetime
from flask import request, current_app, g
from functools import wraps

class LoggingMiddleware:
    def __init__(self, app):
        self.app = app
        self.setup_logging()
        self.setup_request_logging()
        self.setup_error_logging()
        self.setup_performance_logging()
    
    def setup_logging(self):
        """Setup application logging"""
        # Create custom logger
        self.logger = logging.getLogger('project_management')
        self.logger.setLevel(logging.INFO)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Create handlers
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # File handler for detailed logs
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Error file handler
        error_handler = logging.FileHandler('logs/errors.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        # Security log handler
        security_handler = logging.FileHandler('logs/security.log')
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(detailed_formatter)
        
        # Add handlers to logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        
        # Security logger
        self.security_logger = logging.getLogger('security')
        self.security_logger.setLevel(logging.WARNING)
        self.security_logger.addHandler(security_handler)
        
        # Performance logger
        self.performance_logger = logging.getLogger('performance')
        self.performance_logger.setLevel(logging.INFO)
        
        # Create performance file handler
        perf_handler = logging.FileHandler('logs/performance.log')
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(detailed_formatter)
        self.performance_logger.addHandler(perf_handler)
        
        # Create logs directory if it doesn't exist
        import os
        os.makedirs('logs', exist_ok=True)
    
    def setup_request_logging(self):
        """Setup request logging middleware"""
        
        @self.app.before_request
        def log_request_start():
            g.start_time = time.time()
            g.request_id = self.generate_request_id()
            
            # Log request details
            request_data = {
                'request_id': g.request_id,
                'method': request.method,
                'url': request.url,
                'path': request.path,
                'query_string': dict(request.args),
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'content_type': request.content_type,
                'content_length': request.content_length,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Log sensitive data (excluding passwords)
            if request.is_json and request.get_json():
                json_data = request.get_json()
                if isinstance(json_data, dict):
                    # Remove sensitive fields
                    safe_data = {k: v for k, v in json_data.items() 
                               if k.lower() not in ['password', 'token', 'secret', 'key']}
                    request_data['json_data'] = safe_data
            
            self.logger.info(f"Request started: {json.dumps(request_data)}")
            
            return None
        
        @self.app.after_request
        def log_request_end(response):
            if hasattr(g, 'start_time'):
                duration = time.time() - g.start_time
                
                response_data = {
                    'request_id': getattr(g, 'request_id', 'unknown'),
                    'method': request.method,
                    'url': request.url,
                    'path': request.path,
                    'status_code': response.status_code,
                    'content_length': response.content_length,
                    'duration_ms': round(duration * 1000, 2),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # Log slow requests
                if duration > 2.0:  # Log requests taking more than 2 seconds
                    self.performance_logger.warning(f"Slow request: {json.dumps(response_data)}")
                else:
                    self.logger.info(f"Request completed: {json.dumps(response_data)}")
                
                # Log errors
                if response.status_code >= 400:
                    error_data = response_data.copy()
                    error_data['response_data'] = response.get_data(as_text=True)[:500]  # Limit response data
                    self.logger.error(f"Request error: {json.dumps(error_data)}")
            
            return response
    
    def setup_error_logging(self):
        """Setup error logging"""
        
        @self.app.errorhandler(Exception)
        def log_exception(error):
            error_data = {
                'error_type': type(error).__name__,
                'error_message': str(error),
                'request_id': getattr(g, 'request_id', 'unknown'),
                'method': request.method,
                'url': request.url,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'timestamp': datetime.utcnow().isoformat(),
                'stack_trace': self.get_stack_trace()
            }
            
            self.logger.error(f"Unhandled exception: {json.dumps(error_data)}")
            
            # Return JSON error response for API requests
            if request.path.startswith('/api/'):
                return jsonify({
                    'error': 'Internal server error',
                    'message': 'An unexpected error occurred',
                    'request_id': getattr(g, 'request_id', 'unknown')
                }), 500
            
            return None
        
        @self.app.errorhandler(404)
        def log_404(error):
            error_data = {
                'error_type': 'NotFound',
                'request_id': getattr(g, 'request_id', 'unknown'),
                'method': request.method,
                'url': request.url,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.logger.warning(f"404 Not Found: {json.dumps(error_data)}")
            
            if request.path.startswith('/api/'):
                return jsonify({
                    'error': 'Not found',
                    'message': 'The requested resource was not found',
                    'request_id': getattr(g, 'request_id', 'unknown')
                }), 404
            
            return None
        
        @self.app.errorhandler(403)
        def log_403(error):
            error_data = {
                'error_type': 'Forbidden',
                'request_id': getattr(g, 'request_id', 'unknown'),
                'method': request.method,
                'url': request.url,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.logger.warning(f"403 Forbidden: {json.dumps(error_data)}")
            
            if request.path.startswith('/api/'):
                return jsonify({
                    'error': 'Access denied',
                    'message': 'You do not have permission to access this resource',
                    'request_id': getattr(g, 'request_id', 'unknown')
                }), 403
            
            return None
        
        @self.app.errorhandler(429)
        def log_429(error):
            error_data = {
                'error_type': 'TooManyRequests',
                'request_id': getattr(g, 'request_id', 'unknown'),
                'method': request.method,
                'url': request.url,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.logger.warning(f"429 Too Many Requests: {json.dumps(error_data)}")
            
            if request.path.startswith('/api/'):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': 'Too many requests. Please try again later.',
                    'request_id': getattr(g, 'request_id', 'unknown')
                }), 429
            
            return None
    
    def setup_performance_logging(self):
        """Setup performance logging"""
        
        @self.app.before_request
        def start_performance_timer():
            g.perf_start_time = time.time()
            return None
        
        @self.app.after_request
        def end_performance_timer(response):
            if hasattr(g, 'perf_start_time'):
                duration = time.time() - g.perf_start_time
                
                # Log database queries if available
                db_queries = getattr(g, 'db_queries', [])
                
                perf_data = {
                    'request_id': getattr(g, 'request_id', 'unknown'),
                    'method': request.method,
                    'path': request.path,
                    'duration_ms': round(duration * 1000, 2),
                    'db_queries_count': len(db_queries),
                    'db_queries_time': sum(q.get('time', 0) for q in db_queries),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # Log slow database queries
                slow_queries = [q for q in db_queries if q.get('time', 0) > 0.1]
                if slow_queries:
                    perf_data['slow_queries'] = slow_queries
                
                self.performance_logger.info(f"Performance: {json.dumps(perf_data)}")
            
            return response
    
    def generate_request_id(self):
        """Generate unique request ID"""
        import uuid
        return str(uuid.uuid4())
    
    def get_stack_trace(self):
        """Get formatted stack trace"""
        import traceback
        return traceback.format_exc()
    
    def log_security_event(self, event_type, details, severity='medium', user_id=None):
        """Log security events"""
        security_data = {
            'event_type': event_type,
            'severity': severity,
            'details': details,
            'user_id': user_id,
            'request_id': getattr(g, 'request_id', 'unknown'),
            'method': request.method,
            'url': request.url,
            'path': request.path,
            'remote_addr': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.security_logger.warning(f"Security Event: {event_type} - {details}")
        
        # In production, you might send this to a security monitoring service
        return security_data
    
    def log_business_event(self, event_type, details, user_id=None, severity='info'):
        """Log business events"""
        business_data = {
            'event_type': event_type,
            'severity': severity,
            'details': details,
            'user_id': user_id,
            'request_id': getattr(g, 'request_id', 'unknown'),
            'method': request.method,
            'path': request.path,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"Business Event: {event_type} - {details}")
        return business_data
    
    def log_api_call(self, endpoint, method, user_id=None, params=None, response_data=None, duration=None):
        """Log API calls for analytics"""
        api_data = {
            'endpoint': endpoint,
            'method': method,
            'user_id': user_id,
            'params': params or {},
            'response_status': response_data.get('status_code') if response_data else None,
            'duration_ms': duration,
            'request_id': getattr(g, 'request_id', 'unknown'),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"API Call: {endpoint} - {method} - {duration}ms")
        return api_data
    
    def log_database_query(self, query, params=None, duration=None):
        """Log database queries"""
        query_data = {
            'query': str(query),
            'params': params or {},
            'duration_ms': duration,
            'request_id': getattr(g, 'request_id', 'unknown'),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Store query for performance analysis
        if not hasattr(g, 'db_queries'):
            g.db_queries = []
        
        g.db_queries.append(query_data)
        
        # Log slow queries
        if duration and duration > 0.1:
            self.performance_logger.warning(f"Slow DB Query: {query} - {duration:.3f}s")
        
        return query_data
    
    def create_audit_log(self, action, entity_type, entity_id, user_id=None, old_values=None, new_values=None):
        """Create audit log entry"""
        audit_data = {
            'action': action,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'user_id': user_id,
            'old_values': old_values,
            'new_values': new_values,
            'request_id': getattr(g, 'request_id', 'unknown'),
            'method': request.method,
            'path': request.path,
            'remote_addr': request.remote_addr,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"Audit Log: {action} - {entity_type}:{entity_id}")
        
        # In production, you'd save this to a database table
        return audit_data
    
    def get_request_stats(self, start_time=None, end_time=None):
        """Get request statistics"""
        # This would typically query a database or log files
        # For now, return mock data
        return {
            'total_requests': 0,
            'successful_requests': 0,
            'error_requests': 0,
            'average_response_time': 0,
            'slow_requests': 0,
            'top_endpoints': [],
            'error_rate': 0.0
        }

# Create logging middleware instance
def logging_middleware(app):
    """Apply logging middleware to Flask app"""
    return LoggingMiddleware(app)

# Decorators for logging
def log_request_details(f):
    """Decorator to log detailed request information"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        try:
            # Log request start
            current_app.logger.info(f"Function {f.__name__} started")
            
            # Execute the function
            result = f(*args, **kwargs)
            
            # Log completion
            duration = time.time() - start_time
            current_app.logger.info(f"Function {f.__name__} completed in {duration:.3f}s")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            current_app.logger.error(f"Function {f.__name__} failed after {duration:.3f}s: {str(e)}")
            raise
    
    return decorated_function

def log_performance(f):
    """Decorator to log function performance"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = f(*args, **kwargs)
            
            duration = time.time() - start_time
            
            # Log slow functions
            if duration > 1.0:
                current_app.logger.warning(f"Slow function: {f.__name__} took {duration:.3f}s")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            current_app.logger.error(f"Function {f.__name__} failed after {duration:.3f}s: {str(e)}")
            raise
    
    return decorated_function

def log_api_call(endpoint):
    """Decorator to log API calls"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                
                duration = time.time() - start_time
                
                # Log API call
                logging_middleware(current_app).log_api_call(
                    endpoint=endpoint,
                    method=request.method,
                    duration=duration,
                    response_data=result if hasattr(result, 'status_code') else None
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                logging_middleware(current_app).log_api_call(
                        endpoint=endpoint,
                        method=request.method,
                        duration=duration,
                        response_data={'error': str(e)}
                    )
                
                raise
        
        return decorated_function
    return decorator
