from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from datetime import datetime, timedelta
import secrets

class JWTUtils:
    @staticmethod
    def generate_tokens(user_id, additional_claims=None):
        """Generate JWT access and refresh tokens"""
        claims = {
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat()
        }
        
        if additional_claims:
            claims.update(additional_claims)
        
        access_token = create_access_token(
            identity=user_id,
            additional_claims=claims
        )
        
        refresh_token = create_refresh_token(identity=user_id)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600,  # 1 hour
            'claims': claims
        }
    
    @staticmethod
    def get_current_user_id():
        """Get current user ID from JWT token"""
        try:
            return get_jwt_identity()
        except:
            return None
    
    @staticmethod
    def generate_secure_token(length=32):
        """Generate secure random token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_reset_token():
        """Generate password reset token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_verification_token():
        """Generate email verification token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_api_key():
        """Generate API key"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def is_token_expired(token_data):
        """Check if token is expired"""
        try:
            created_at = token_data.get('created_at')
            if not created_at:
                return True
            
            created_time = datetime.fromisoformat(created_at)
            expiry_time = created_time + timedelta(hours=1)
            
            return datetime.utcnow() > expiry_time
        except:
            return True
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """Refresh access token using refresh token"""
        try:
            # This would typically be handled by flask-jwt-extended
            # For now, return a placeholder
            return {
                'access_token': 'new_access_token_placeholder',
                'token_type': 'Bearer',
                'expires_in': 3600
            }
        except:
            return None

# Create instance
jwt_utils = JWTUtils()
