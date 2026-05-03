from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from app import db
from app.models.user import User


class UserModule:
    """Business logic for User operations."""

    # ================================================================
    # PASSWORD
    # ================================================================

    @staticmethod
    def set_password(user, password):
        user.password_hash = generate_password_hash(
            password, method='pbkdf2:sha256', salt_length=16
        )
        # No commit here — callers are responsible for the transaction.

    @staticmethod
    def check_password(user, password):
        return check_password_hash(user.password_hash, password)

    # ================================================================
    # TOKENS
    # identity must be a string for Flask-JWT-Extended v4+
    # ================================================================

    @staticmethod
    def generate_tokens(user):
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'email': user.email,
                'role':  user.role,
                'name':  user.name,
            }
        )
        refresh_token = create_refresh_token(identity=str(user.id))

        return {
            'access_token':  access_token,
            'refresh_token': refresh_token,
            'token_type':    'Bearer',
        }

    # ================================================================
    # LOOKUPS
    # ================================================================

    @staticmethod
    def find_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def find_by_id(user_id):
        """Accept both string and int — get_jwt_identity() returns a string."""
        try:
            return db.session.get(User, int(user_id))
        except (ValueError, TypeError):
            return None

    # ================================================================
    # CREATE / UPDATE / DELETE
    # ================================================================

    @staticmethod
    def create_user(name, email, password, role='user'):
        if UserModule.find_by_email(email):
            raise ValueError('User with this email already exists')
        user = User(name=name, email=email, role=role)
        # Set password before adding to session to avoid constraint violation
        UserModule.set_password(user, password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update_profile(user, **kwargs):
        for field in ('name', 'phone', 'avatar'):
            if field in kwargs:
                setattr(user, field, kwargs[field])
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return user

    @staticmethod
    def change_password(user, new_password):
        UserModule.set_password(user, new_password)
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()

    @staticmethod
    def update_last_login(user):
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()

    @staticmethod
    def activate(user):
        user.status = 'active'
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()

    @staticmethod
    def deactivate(user):
        user.status = 'inactive'
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()

    @staticmethod
    def delete(user):
        db.session.delete(user)
        db.session.commit()

    # ================================================================
    # CHECKS
    # ================================================================

    @staticmethod
    def is_admin(user):
        return user.role == 'admin'

    @staticmethod
    def is_staff(user):
        return user.role == 'staff'

    @staticmethod
    def is_active(user):
        return user.status == 'active'

    # ================================================================
    # SERIALISATION
    # ================================================================

    @staticmethod
    def to_dict(user):
        return {
            'id':             user.id,
            'name':           user.name,
            'email':          user.email,
            'role':           user.role,
            'status':         user.status,
            'avatar':         user.avatar,
            'phone':          user.phone,
            'email_verified': user.email_verified,
            'project_count':  UserModule._projects_count(user),
            'created_at':     user.created_at.isoformat() if user.created_at else None,
            'updated_at':     user.updated_at.isoformat() if user.updated_at else None,
            'last_login':     user.last_login.isoformat() if user.last_login else None,
        }

    # ================================================================
    # HELPERS
    # ================================================================

    @staticmethod
    def _projects_count(user):
        return len(user.projects) if user.projects else 0

    @staticmethod
    def get_projects_count(user):
        return UserModule._projects_count(user)

    @staticmethod
    def get_active_projects(user):
        if not user.projects:
            return []
        return [p for p in user.projects if p.status != 'archived']