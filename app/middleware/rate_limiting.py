from flask import request, jsonify, current_app, g
from functools import wraps
import time
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimitingMiddleware:
    def __init__(self, app):
        self.app = app
        self.rate_limits = {}
        self.setup_rate_limiting()
    
    def setup_rate_limiting(self):
        """Setup rate limiting middleware"""
        
        @self.app.before_request
        def check_rate_limit():
            # Get client identifier
            client_id = self.get_client_identifier()
            
            # Get rate limit rules
            rate_limit_rules = self.get_rate_limit_rules()
            
            # Check each rule
            for rule_name, rule in rate_limit_rules.items():
                if self.should_apply_rule(rule):
                    if not self.check_rate_limit(client_id, rule):
                        return jsonify({
                            'error': 'Rate limit exceeded',
                            'message': f'Rate limit exceeded for {rule_name}',
                            'limit': rule['limit'],
                            'window': rule['window'],
                            'retry_after': rule.get('retry_after', rule['window'])
                        }), 429
            
            return None
    
    def get_client_identifier(self):
        """Get client identifier for rate limiting"""
        # Try to get unique client identifier
        client_id = None
        
        # Priority order for client identification
        if request.headers.get('X-Client-ID'):
            client_id = request.headers['X-Client-ID']
        elif request.headers.get('X-API-Key'):
            client_id = f"api_key_{request.headers['X-API-Key']}"
        elif hasattr(g, 'current_user') and g.current_user:
            client_id = f"user_{g.current_user.id}"
        elif request.remote_addr:
            client_id = f"ip_{request.remote_addr}"
        else:
            client_id = "anonymous"
        
        return client_id
    
    def get_rate_limit_rules(self):
        """Get rate limiting rules"""
        return {
            'default': {
                'limit': 100,  # requests
                'window': 3600,  # 1 hour
                'block_duration': 3600, # 1 hour
                'retry_after': 3600
            },
            'auth': {
                'limit': 10,  # requests
                'window': 900,  # 15 minutes
                'block_duration': 900,
                'retry_after': 900
            },
            'upload': {
                'limit': 5,  # requests
                'window': 3600, # 1 hour
                'block_duration': 3600,
                'retry_after': 3600
            },
            'api': {
                'limit': 1000, # requests
                'window': 3600, # 1 hour
                'block_duration': 3600,
                'retry_after': 3600
            },
            'password_reset': {
                'limit': 3, # requests
                'window': 3600, # 1 hour
                'block_duration': 3600,
                'retry_after': 3600
            },
            'registration': {
                'limit': 5, # requests
                'window': 3600, # 1 hour
                'block_duration': 3600,
                'retry_after': 3600
            }
        }
    
    def should_apply_rule(self, rule):
        """Check if rate limit rule should apply to current request"""
        rule_conditions = rule.get('conditions', {})
        
        # Check path patterns
        if 'paths' in rule_conditions:
            request_path = request.path
            for path_pattern in rule_conditions['paths']:
                if request_path.startswith(path_pattern):
                    return True
        
        # Check methods
        if 'methods' in rule_conditions:
            if request.method not in rule_conditions['methods']:
                return False
        
        # Check headers
        if 'headers' in rule_conditions:
            for header_name, header_value in rule_conditions['headers'].items():
                if request.headers.get(header_name) != header_value:
                    return False
        
        # Check query parameters
        if 'query_params' in rule_conditions:
            for param_name, param_value in rule_conditions['query_params'].items():
                if request.args.get(param_name) != param_value:
                    return False
        
        return True
    
    def check_rate_limit(self, client_id, rule):
        """Check if client has exceeded rate limit"""
        current_time = time.time()
        window_start = current_time - rule['window']
        
        # Get or create rate limit data for this client and rule
        rule_key = f"{client_id}:{rule.get('name', 'default')}"
        
        if rule_key not in self.rate_limits:
            self.rate_limits[rule_key] = {
                'requests': [],
                'blocked_until': None
            }
        
        rate_limit_data = self.rate_limits[rule_key]
        
        # Check if client is blocked
        if rate_limit_data['blocked_until']:
            if current_time < rate_limit_data['blocked_until']:
                return False
            else:
                # Unblock client
                rate_limit_data['blocked_until'] = None
                rate_limit_data['requests'] = []
        
        # Clean old requests outside the window
        rate_limit_data['requests'] = [
            timestamp for timestamp in rate_limit_data['requests']
            if timestamp > window_start
        ]
        
        # Check if limit exceeded
        if len(rate_limit_data['requests']) >= rule['limit']:
            # Block client
            rate_limit_data['blocked_until'] = current_time + rule.get('block_duration', rule['window'])
            
            # Log rate limit violation
            current_app.logger.warning(
                f"Rate limit exceeded for {client_id} "
                f"(rule: {rule.get('name', 'default')}, "
                f"limit: {rule['limit']}, "
                f"window: {rule['window']}s)"
            )
            
            return False
        
        # Add current request
        rate_limit_data['requests'].append(current_time)
        
        return True
    
    def get_rate_limit_status(self, client_id, rule_name='default'):
        """Get rate limit status for client"""
        rule = self.get_rate_limit_rules().get(rule_name)
        if not rule:
            return None
        
        rule_key = f"{client_id}:{rule_name}"
        
        if rule_key not in self.rate_limits:
            return {
                'limit': rule['limit'],
                'window': rule['window'],
                'remaining': rule['limit'],
                'reset_time': time.time() + rule['window'],
                'blocked': False
            }
        
        rate_limit_data = self.rate_limits[rule_key]
        current_time = time.time()
        window_start = current_time - rule['window']
        
        # Clean old requests
        rate_limit_data['requests'] = [
            timestamp for timestamp in rate_limit_data['requests']
            if timestamp > window_start
        ]
        
        remaining = max(0, rule['limit'] - len(rate_limit_data['requests']))
        reset_time = None
        
        if rate_limit_data['requests']:
            oldest_request = min(rate_limit_data['requests'])
            reset_time = oldest_request + rule['window']
        
        return {
            'limit': rule['limit'],
            'window': rule['window'],
            'remaining': remaining,
            'reset_time': reset_time,
            'blocked': rate_limit_data['blocked_until'] is not None,
            'blocked_until': rate_limit_data['blocked_until']
        }
    
    def reset_rate_limit(self, client_id, rule_name='default'):
        """Reset rate limit for client"""
        rule_key = f"{client_id}:{rule_name}"
        
        if rule_key in self.rate_limits:
            self.rate_limits[rule_key] = {
                'requests': [],
                'blocked_until': None
            }
    
    def block_client(self, client_id, duration=3600, reason=None):
        """Block client for specified duration"""
        for rule_key, rate_limit_data in self.rate_limits.items():
            if rule_key.startswith(client_id):
                rate_limit_data['blocked_until'] = time.time() + duration
        
        current_app.logger.warning(f"Client {client_id} blocked for {duration}s: {reason}")
    
    def unblock_client(self, client_id):
        """Unblock client"""
        for rule_key, rate_limit_data in self.rate_limits.items():
            if rule_key.startswith(client_id):
                rate_limit_data['blocked_until'] = None
                rate_limit_data['requests'] = []
        
        current_app.logger.info(f"Client {client_id} unblocked")
    
    def get_client_stats(self, client_id):
        """Get rate limiting statistics for client"""
        stats = {
            'client_id': client_id,
            'rules': {}
        }
        
        for rule_key, rate_limit_data in self.rate_limits.items():
            if rule_key.startswith(client_id):
                rule_name = rule_key.split(':', 1)
                rule = self.get_rate_limit_rules().get(rule_name)
                
                if rule:
                    stats['rules'][rule_name] = {
                        'limit': rule['limit'],
                        'window': rule['window'],
                        'current_requests': len(rate_limit_data['requests']),
                        'blocked': rate_limit_data['blocked_until'] is not None,
                        'blocked_until': rate_limit_data['blocked_until']
                    }
        
        return stats
    
    def cleanup_expired_blocks(self):
        """Clean up expired blocks"""
        current_time = time.time()
        cleaned_count = 0
        
        for rule_key, rate_limit_data in self.rate_limits.items():
            if rate_limit_data['blocked_until'] and current_time >= rate_limit_data['blocked_until']:
                rate_limit_data['blocked_until'] = None
                rate_limit_data['requests'] = []
                cleaned_count += 1
        
        if cleaned_count > 0:
            current_app.logger.info(f"Cleaned up {cleaned_count} expired rate limit blocks")
    
    def get_global_stats(self):
        """Get global rate limiting statistics"""
        total_clients = len(set(key.split(':')[0] for key in self.rate_limits.keys()))
        blocked_clients = len([
            key for key, data in self.rate_limits.items()
            if data['blocked_until'] is not None
        ])
        
        rule_stats = {}
        for rule_name in self.get_rate_limit_rules():
            rule_stats[rule_name] = {
                'total_requests': 0,
                'blocked_requests': 0,
                'active_clients': 0
            }
        
        for rule_key, rate_limit_data in self.rate_limits.items():
            rule_name = rule_key.split(':', 1)
            if rule_name in rule_stats:
                rule_stats[rule_name]['total_requests'] += len(rate_limit_data['requests'])
                if rate_limit_data['blocked_until']:
                    rule_stats[rule_name]['blocked_requests'] += 1
                else:
                    rule_stats[rule_name]['active_clients'] += 1
        
        return {
            'total_clients': total_clients,
            'blocked_clients': blocked_clients,
            'rules': rule_stats
        }

# Create rate limiting middleware instance
def rate_limiting_middleware(app):
    """Apply rate limiting middleware to Flask app"""
    return RateLimitingMiddleware(app)

# Decorators for rate limiting
def rate_limit(limit=100, window=3600, scope='default'):
    """Decorator to apply rate limiting to route"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_id = RateLimitingMiddleware(app).get_client_identifier()
            
            rule = {
                'limit': limit,
                'window': window,
                'name': scope,
                'conditions': {
                    'paths': [request.path]
                }
            }
            
            if not RateLimitingMiddleware(app).check_rate_limit(client_id, rule):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Rate limit exceeded: {limit} requests per {window} seconds',
                    'limit': limit,
                    'window': window,
                    'retry_after': window
                }), 429
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def rate_limit_by_user(limit=100, window=3600):
    """Decorator to rate limit by user"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if hasattr(g, 'current_user') and g.current_user:
                client_id = f"user_{g.current_user.id}"
                
                rule = {
                    'limit': limit,
                    'window': window,
                    'name': 'user',
                    'conditions': {
                        'paths': [request.path]
                    }
                }
                
                if not RateLimitingMiddleware(app).check_rate_limit(client_id, rule):
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'message': f'Rate limit exceeded: {limit} requests per {window} seconds',
                        'limit': limit,
                        'window': window,
                        'retry_after': window
                    }), 429
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def rate_limit_by_ip(limit=100, window=3600):
    """Decorator to rate limit by IP address"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_id = f"ip_{request.remote_addr}"
            
            rule = {
                'limit': limit,
                'window': window,
                'name': 'ip',
                'conditions': {
                    'paths': [request.path]
                }
            }
            
            if not RateLimitingMiddleware(app).check_rate_limit(client_id, rule):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Rate limit exceeded: {limit} requests per {window} seconds',
                    'limit': limit,
                    'window': window,
                    'retry_after': window
                }), 429
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def rate_limit_by_api_key(limit=1000, window=3600):
    """Decorator to rate limit by API key"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            
            if api_key:
                client_id = f"api_key_{api_key}"
                
                rule = {
                    'limit': limit,
                    'window': window,
                    'name': 'api_key',
                    'conditions': {
                        'paths': [request.path]
                    }
                }
                
                if not RateLimitingMiddleware(app).check_rate_limit(client_id, rule):
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'message': f'Rate limit exceeded: {limit} requests per {window} seconds',
                        'limit': limit,
                        'window': window,
                        'retry_after': window
                    }), 429
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def rate_limit_auth(limit=10, window=900):
    """Decorator to rate limit authentication endpoints"""
    return rate_limit(limit=limit, window=window, scope='auth')

def rate_limit_upload(limit=5, window=3600):
    """Decorator to rate limit upload endpoints"""
    return rate_limit(limit=limit, window=window, scope='upload')

def rate_limit_password_reset(limit=3, window=3600):
    """Decorator to rate limit password reset endpoints"""
    return rate_limit(limit=limit, window=window, scope='password_reset')

def rate_limit_registration(limit=5, window=3600):
    """Decorator to rate limit registration endpoints"""
    return rate_limit(limit=limit, window=window, scope='registration')

def rate_limit_api(limit=1000, window=3600):
    """Decorator to rate limit API endpoints"""
    return rate_limit(limit=limit, window=window, scope='api')
