# backend/app/routes/auth_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db, limiter
from app.models.user import User
from app.modules.user import UserModule
from app.modules.staff import StaffModule
from app.utils.validators import validators
import logging
import os

logger = logging.getLogger(__name__)

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# ================================================================
# REGISTER
# ================================================================

@bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    try:
        data = request.get_json()

        safe_data = {k: v for k, v in data.items() if k != 'password'}
        logger.info(f"Registration attempt with data: {safe_data}")

        required_fields = ['name', 'email', 'password']
        missing_fields = [field for field in required_fields if not data.get(field)]

        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            logger.warning(f"Registration failed: {error_msg}")
            return jsonify({'error': error_msg}), 400

        name     = data['name'].strip()
        email    = data['email'].strip().lower()
        password = data['password']
        role     = data.get('role', 'user')

        if len(name) < 2:
            return jsonify({'error': 'Name must be at least 2 characters long'}), 400

        if not validators.is_valid_email(email):
            return jsonify({'error': 'Invalid email format'}), 400

        if not validators.is_valid_password(password):
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400

        if role not in ['user', 'staff', 'admin']:
            return jsonify({'error': 'Invalid role'}), 400

        admin_email = os.getenv('ADMIN_EMAIL', '').strip().lower()
        if email == admin_email:
            return jsonify({'error': 'Cannot register with this email'}), 403

        if UserModule.find_by_email(email):
            return jsonify({'error': 'User with this email already exists'}), 409

        user = UserModule.create_user(name, email, password, role)
        logger.info(f"User registered successfully: {email}")

        return jsonify({
            'message': 'User registered successfully',
            'user':    UserModule.to_dict(user)
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500


# ================================================================
# LOGIN
# ================================================================

@bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    try:
        data = request.get_json()

        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400

        email    = data['email'].strip().lower()
        password = data['password']

        admin_email    = os.getenv('ADMIN_EMAIL', '').strip().lower()
        admin_password = os.getenv('ADMIN_PASSWORD', '')
        admin_name     = os.getenv('ADMIN_NAME', 'Admin User')

        if email == admin_email:
            if password == admin_password:
                user = UserModule.find_by_email(email)
                if not user:
                    user = UserModule.create_user(admin_name, email, admin_password, 'admin')

                if user.role != 'admin':
                    user.role = 'admin'
                    db.session.commit()

                tokens = UserModule.generate_tokens(user)
                UserModule.update_last_login(user)

                return jsonify({
                    'message': 'Admin login successful',
                    'user':    UserModule.to_dict(user),
                    'tokens':  tokens
                }), 200
            else:
                return jsonify({'error': 'Invalid admin credentials'}), 401

        user = UserModule.find_by_email(email)
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401

        if not UserModule.check_password(user, password):
            return jsonify({'error': 'Invalid credentials'}), 401

        if not UserModule.is_active(user):
            return jsonify({'error': 'Account is deactivated'}), 401

        tokens = UserModule.generate_tokens(user)
        UserModule.update_last_login(user)

        logger.info(f"User logged in successfully: {email}")

        return jsonify({
            'message': 'Login successful',
            'user':    UserModule.to_dict(user),
            'tokens':  tokens
        }), 200

    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500


# ================================================================
# STAFF — SETUP PASSWORD  (called from the email verification link)
# ================================================================

@bp.route('/staff/setup-password', methods=['POST'])
@limiter.limit("10 per minute")
def staff_setup_password():
    try:
        data = request.get_json()

        token    = data.get('token', '').strip()
        password = data.get('password', '').strip()

        if not token:
            return jsonify({'error': 'Verification token is required'}), 400

        if not password:
            return jsonify({'error': 'Password is required'}), 400

        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400

        staff = StaffModule.verify_and_set_password(token, password)

        tokens = UserModule.generate_tokens(staff.user)
        UserModule.update_last_login(staff.user)

        logger.info(f"Staff account activated: {staff.user.email}")

        return jsonify({
            'message': 'Account activated successfully. You can now log in.',
            'user':    UserModule.to_dict(staff.user),
            'tokens':  tokens
        }), 200

    except ValueError as e:
        logger.warning(f"Staff setup-password failed: {str(e)}")
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        db.session.rollback()
        logger.error(f"Staff setup-password error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to activate account', 'details': str(e)}), 500


# ================================================================
# ME
# ================================================================

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        current_user_id = get_jwt_identity()
        user = UserModule.find_by_id(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({'user': UserModule.to_dict(user)}), 200

    except Exception as e:
        logger.error(f"Get current user error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get user info', 'details': str(e)}), 500


# ================================================================
# LOGOUT
# ================================================================

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    current_user_id = get_jwt_identity()
    logger.info(f"User logged out: {current_user_id}")
    return jsonify({'message': 'Logout successful'}), 200


# ================================================================
# REFRESH TOKEN
# ================================================================

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user_id = get_jwt_identity()
        user = UserModule.find_by_id(current_user_id)

        if not user or not UserModule.is_active(user):
            return jsonify({'error': 'Invalid user'}), 401

        access_token = create_access_token(identity=current_user_id)

        return jsonify({'access_token': access_token}), 200

    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to refresh token', 'details': str(e)}), 500