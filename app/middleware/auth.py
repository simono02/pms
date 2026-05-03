from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
import time


# ======================================================================
# ROLE-BASED DECORATORS
# ======================================================================

def role_required(*allowed_roles):
    """Decorator to require specific user roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()

                from app.modules.user import UserModule   # avoid circular import
                user = UserModule.find_by_id(current_user_id)

                if not user:
                    return jsonify({
                        'error': 'User not found',
                        'message': 'Invalid user token'
                    }), 404

                if user.role not in allowed_roles:
                    return jsonify({
                        'error': 'Access denied',
                        'message': f'Required role(s): {", ".join(allowed_roles)}'
                    }), 403

                return f(*args, **kwargs)

            except Exception as e:
                return jsonify({
                    'error': 'Authentication required',
                    'message': str(e)
                }), 401

        return decorated_function
    return decorator


def admin_required(f):
    return role_required('admin')(f)


def staff_required(f):
    return role_required('staff')(f)


def user_required(f):
    return role_required('user')(f)


# ======================================================================
# OTHER DECORATORS
# ======================================================================

def token_required(f):
    """Require any valid JWT token."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({
                'error': 'Authentication required',
                'message': str(e)
            }), 401
    return decorated_function


def active_user_required(f):
    """Require that the user's account is active."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()

            from app.modules.user import UserModule
            user = UserModule.find_by_id(current_user_id)

            if not user:
                return jsonify({'error': 'User not found'}), 404

            if not UserModule.is_active(user):
                return jsonify({'error': 'Account is deactivated'}), 403

            return f(*args, **kwargs)

        except Exception as e:
            return jsonify({
                'error': 'Authentication required',
                'message': str(e)
            }), 401

    return decorated_function


def ownership_required(resource_type):
    """Require ownership of a resource. Admins bypass this check."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()

                from app.modules.user import UserModule
                user = UserModule.find_by_id(current_user_id)

                if not user:
                    return jsonify({'error': 'User not found'}), 404

                if user.role == 'admin':
                    return f(*args, **kwargs)

                if resource_type == 'project':
                    project_id = kwargs.get('project_id') or \
                                 request.view_args.get('project_id')
                    if project_id:
                        from app.models.project import Project
                        project = Project.query.get(project_id)
                        if not project:
                            return jsonify({'error': 'Project not found'}), 404
                        if project.user_id != int(current_user_id):
                            return jsonify({'error': 'Access denied'}), 403

                elif resource_type == 'payment':
                    payment_id = kwargs.get('payment_id') or \
                                 request.view_args.get('payment_id')
                    if payment_id:
                        from app.models.payment import Payment
                        payment = Payment.query.get(payment_id)
                        if not payment:
                            return jsonify({'error': 'Payment not found'}), 404
                        if payment.user_id != int(current_user_id):
                            return jsonify({'error': 'Access denied'}), 403

                return f(*args, **kwargs)

            except Exception as e:
                return jsonify({
                    'error': 'Authentication required',
                    'message': str(e)
                }), 401

        return decorated_function
    return decorator


def log_request(f):
    """Log request duration."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import current_app
        start = time.time()
        try:
            result = f(*args, **kwargs)
            current_app.logger.info(
                f"{request.method} {request.path} "
                f"completed in {time.time() - start:.2f}s"
            )
            return result
        except Exception as e:
            current_app.logger.error(
                f"{request.method} {request.path} "
                f"error in {time.time() - start:.2f}s: {e}"
            )
            raise

    return decorated_function


# ======================================================================
# auth_middleware — intentional no-op.
# All auth is handled per-route via @jwt_required() + @admin_required.
# A global before_request hook caused double-validation and 401s.
# ======================================================================

def auth_middleware(app):
    pass