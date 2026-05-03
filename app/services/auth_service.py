import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
from app.models.user import User
from app.utils.jwt_utils import generate_tokens
from app.utils.email_service import EmailService
from app.utils.validators import validate_email, validate_password
import secrets
import string

class AuthService:
    @staticmethod
    def login(email, password):
        """Authenticate user and return tokens"""
        try:
            # Find user by email
            user = User.find_by_email(email)
            
            if not user:
                return {'success': False, 'message': 'Invalid email or password'}
            
            # Check password
            if not user.check_password(password):
                return {'success': False, 'message': 'Invalid email or password'}
            
            # Check if user is active
            if not user.is_active():
                return {'success': False, 'message': 'Account is deactivated'}
            
            # Generate tokens
            tokens = user.generate_tokens()
            
            # Update last login
            user.update_last_login()
            
            return {
                'success': True,
                'message': 'Login successful',
                'user': user.to_dict(),
                'tokens': tokens
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Login failed: {str(e)}'}
    
    @staticmethod
    def register(name, email, password, role='user'):
        """Register a new user"""
        try:
            # Validate input
            if not name or len(name.strip()) < 2:
                return {'success': False, 'message': 'Name must be at least 2 characters long'}
            
            if not validate_email(email):
                return {'success': False, 'message': 'Invalid email format'}
            
            if not validate_password(password):
                return {'success': False, 'message': 'Password must be at least 6 characters long'}
            
            # Check if user already exists
            if User.find_by_email(email):
                return {'success': False, 'message': 'User with this email already exists'}
            
            # Create user
            user = User.create_user(name, email, password, role)
            
            # Send welcome email
            try:
                EmailService.send_welcome_email(user)
            except Exception:
                # Continue even if email fails
                pass
            
            return {
                'success': True,
                'message': 'Registration successful',
                'user': user.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Registration failed: {str(e)}'}
    
    @staticmethod
    def logout():
        """Logout user (client-side token removal)"""
        return {'success': True, 'message': 'Logout successful'}
    
    @staticmethod
    def refresh_token(refresh_token):
        """Refresh access token"""
        try:
            current_user_id = get_jwt_identity(refresh_token)
            user = User.find_by_id(current_user_id)
            
            if not user or not user.is_active():
                return {'success': False, 'message': 'Invalid or inactive user'}
            
            # Generate new access token
            new_token = create_access_token(
                identity=user.id,
                additional_claims={
                    'email': user.email,
                    'role': user.role,
                    'name': user.name
                }
            )
            
            return {
                'success': True,
                'access_token': new_token,
                'token_type': 'Bearer'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Token refresh failed: {str(e)}'}
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """Change user password"""
        try:
            user = User.find_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Verify current password
            if not user.check_password(current_password):
                return {'success': False, 'message': 'Current password is incorrect'}
            
            # Validate new password
            if not validate_password(new_password):
                return {'success': False, 'message': 'New password must be at least 6 characters long'}
            
            # Update password
            user.change_password(new_password)
            
            # Send password change notification
            try:
                EmailService.send_password_change_notification(user)
            except Exception:
                pass
            
            return {
                'success': True,
                'message': 'Password changed successfully'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Password change failed: {str(e)}'}
    
    @staticmethod
    def forgot_password(email):
        """Send password reset email"""
        try:
            user = User.find_by_email(email)
            
            # Always return success to prevent email enumeration
            if user:
                reset_token = AuthService._generate_reset_token()
                user.reset_token = reset_token
                user.updated_at = db.func.now()
                db.session.commit()
                
                EmailService.send_password_reset_email(user, reset_token)
            
            return {
                'success': True,
                'message': 'If an account with this email exists, a password reset link has been sent'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Password reset failed: {str(e)}'}
    
    @staticmethod
    def reset_password(token, new_password):
        """Reset password with token"""
        try:
            # Find user by reset token
            user = User.query.filter_by(reset_token=token).first()
            
            if not user:
                return {'success': False, 'message': 'Invalid or expired reset token'}
            
            # Check if token is expired (24 hours)
            # TODO: Implement token expiration check
            
            # Validate new password
            if not validate_password(new_password):
                return {'success': False, 'message': 'New password must be at least 6 characters long'}
            
            # Update password
            user.change_password(new_password)
            
            # Clear reset token
            user.reset_token = None
            user.updated_at = db.func.now()
            db.session.commit()
            
            # Send password change confirmation
            try:
                EmailService.send_password_reset_confirmation(user)
            except Exception:
                pass
            
            return {
                'success': True,
                'message': 'Password reset successfully'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Password reset failed: {str(e)}'}
    
    @staticmethod
    def verify_email(token):
        """Verify email address"""
        try:
            # Find user by verification token
            user = User.query.filter_by(email_verification_token=token).first()
            
            if not user:
                return {'success': False, 'message': 'Invalid or expired verification token'}
            
            # Check if token is expired
            # TODO: Implement token expiration check
            
            # Mark email as verified
            user.email_verified = True
            user.email_verification_token = None
            user.updated_at = db.func.now()
            db.session.commit()
            
            # Send welcome email
            try:
                EmailService.send_welcome_email(user)
            except Exception:
                pass
            
            return {
                'success': True,
                'message': 'Email verified successfully'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Email verification failed: {str(e)}'}
    
    @staticmethod
    def _generate_reset_token():
        """Generate secure reset token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    @staticmethod
    def _generate_verification_token():
        """Generate email verification token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    @staticmethod
    def is_token_expired(created_at, hours=24):
        """Check if token is expired"""
        from datetime import datetime, timedelta
        return datetime.utcnow() > created_at + timedelta(hours=hours)
