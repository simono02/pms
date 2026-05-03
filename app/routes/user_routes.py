from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, limiter
from app.models.user import User
from app.models.project import Project
from app.modules.user import UserModule
from app.utils.validators import validators
import os

bp = Blueprint('user', __name__, url_prefix='/api/user')


def _current_user_id():
    """Always returns an int, regardless of JWT identity type."""
    return int(get_jwt_identity())


@bp.route('/profile', methods=['GET'])
def get_profile():
    try:
        # Get user_id from parameter OR require JWT for logged-in user
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            # Require JWT for accessing own profile
            try:
                from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
                verify_jwt_in_request()
                user_id = int(get_jwt_identity())
            except:
                return jsonify({'error': 'Authentication required to view your profile'}), 401
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Use UserModule.to_dict — the User model has no to_dict() of its own
        return jsonify({'user': UserModule.to_dict(user)}), 200

    except Exception as e:
        return jsonify({'error': 'Failed to get profile', 'details': str(e)}), 500


@bp.route('/profile', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per minute")
def update_profile():
    try:
        user = User.query.get(_current_user_id())
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json() or {}

        if 'email' in data:
            email = data['email'].strip().lower()
            if not validators.is_valid_email(email):
                return jsonify({'error': 'Invalid email format'}), 400
            existing = User.query.filter_by(email=email).first()
            if existing and existing.id != user.id:
                return jsonify({'error': 'Email already in use'}), 400
            user.email = email

        if 'name' in data:
            name = data['name'].strip()
            if len(name) < 2:
                return jsonify({'error': 'Name must be at least 2 characters long'}), 400
            user.name = name

        if 'phone' in data:
            user.phone = data['phone']

        if 'avatar' in data:
            user.avatar = data['avatar']

        UserModule.update_profile(user)

        return jsonify({'message': 'Profile updated successfully', 'user': UserModule.to_dict(user)}), 200

    except Exception as e:
        return jsonify({'error': 'Failed to update profile', 'details': str(e)}), 500


@bp.route('/projects', methods=['GET'])
def get_projects():
    try:
        # Get user_id from parameter OR require JWT for logged-in user
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            # Require JWT for accessing own projects
            try:
                from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
                verify_jwt_in_request()
                user_id = int(get_jwt_identity())
            except:
                return jsonify({'error': 'Authentication required to view your projects'}), 401
        
        page     = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        status   = request.args.get('status')
        search   = request.args.get('search')

        query = Project.query.filter_by(user_id=user_id)

        # Support comma-separated status values e.g. "pending,in_progress,payment_required"
        if status:
            status_list = [s.strip() for s in status.split(',') if s.strip()]
            if len(status_list) == 1:
                query = query.filter(Project.status == status_list[0])
            elif len(status_list) > 1:
                query = query.filter(Project.status.in_(status_list))

        if search:
            query = query.filter(Project.title.contains(search))

        query    = query.order_by(Project.created_at.desc())
        projects = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'projects': [p.to_dict(include_details=True) for p in projects.items],
            'pagination': {
                'page':     projects.page,
                'per_page': projects.per_page,
                'total':    projects.total,
                'pages':    projects.pages,
                'has_next': projects.has_next,
                'has_prev': projects.has_prev,
            },
        }), 200

    except Exception as e:
        return jsonify({'error': 'Failed to get projects', 'details': str(e)}), 500


@bp.route('/projects/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    try:
        uid     = _current_user_id()
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        if project.user_id != uid:
            return jsonify({'error': 'Access denied'}), 403
        return jsonify({'project': project.to_dict(include_details=True)}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get project', 'details': str(e)}), 500


@bp.route('/projects/<int:project_id>', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per minute")
def update_project(project_id):
    try:
        uid     = _current_user_id()
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        if project.user_id != uid:
            return jsonify({'error': 'Access denied'}), 403
        if not project.can_be_edited():
            return jsonify({'error': 'Project can only be edited within 24 hours of creation'}), 400

        data = request.get_json() or {}

        if 'title' in data:
            title = data['title'].strip()
            if len(title) < 3:
                return jsonify({'error': 'Title must be at least 3 characters long'}), 400
            project.title = title

        if 'research_field' in data:
            project.research_field = data['research_field']

        if 'description' in data:
            project.set_description_dict(data['description'])

        if 'priority' in data:
            if data['priority'] not in ('low', 'medium', 'high'):
                return jsonify({'error': 'Invalid priority level'}), 400
            project.priority = data['priority']

        project.update_details()

        return jsonify({'message': 'Project updated successfully',
                        'project': project.to_dict(include_details=True)}), 200

    except Exception as e:
        return jsonify({'error': 'Failed to update project', 'details': str(e)}), 500


@bp.route('/projects/<int:project_id>', methods=['DELETE'])
@jwt_required()
@limiter.limit("5 per minute")
def delete_project(project_id):
    try:
        uid     = _current_user_id()
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        if project.user_id != uid:
            return jsonify({'error': 'Access denied'}), 403
        if project.status == 'in_progress':
            return jsonify({'error': 'Cannot delete project that is in progress'}), 400
        if project.status == 'completed':
            return jsonify({'error': 'Cannot delete completed project'}), 400

        for path in (project.file_path, project.result_path):
            if path and os.path.exists(path):
                os.remove(path)

        project.delete()
        return jsonify({'message': 'Project deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': 'Failed to delete project', 'details': str(e)}), 500


@bp.route('/projects/<int:project_id>/describe', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def describe_project(project_id):
    try:
        uid     = _current_user_id()
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        if project.user_id != uid:
            return jsonify({'error': 'Access denied'}), 403

        data = request.get_json() or {}
        for field in ('objectives', 'methodology', 'expected_outcomes', 'timeline'):
            if not data.get(field) or not str(data[field]).strip():
                return jsonify({'error': f'{field} is required'}), 400

        project.set_description_dict(data)
        return jsonify({'message': 'Project description saved successfully',
                        'project': project.to_dict(include_details=True)}), 200

    except Exception as e:
        return jsonify({'error': 'Failed to save description', 'details': str(e)}), 500


@bp.route('/projects/<int:project_id>/download', methods=['GET'])
@jwt_required()
def download_project(project_id):
    try:
        uid     = _current_user_id()
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        if project.user_id != uid:
            return jsonify({'error': 'Access denied'}), 403
        if project.status != 'completed':
            return jsonify({'error': 'Project must be completed to download result'}), 400
        if not project.result_path or not os.path.exists(project.result_path):
            return jsonify({'error': 'Result file not found'}), 404

        return jsonify({
            'download_url': f'/api/files/download/{project_id}',
            'filename':     project.result_filename or 'result.pdf',
        }), 200

    except Exception as e:
        return jsonify({'error': 'Failed to prepare download', 'details': str(e)}), 500


@bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    return jsonify({'notifications': [], 'unread_count': 0}), 200


@bp.route('/settings', methods=['GET'])
@jwt_required()
def get_settings():
    return jsonify({'settings': {
        'email_notifications': True,
        'push_notifications':  False,
        'theme':               'light',
        'language':            'en',
    }}), 200


@bp.route('/settings', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per minute")
def update_settings():
    return jsonify({'message': 'Settings updated successfully'}), 200


@bp.route('/stats', methods=['GET'])
def get_user_stats():
    try:
        # Get user_id from parameter OR require JWT for logged-in user
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            # Require JWT for accessing own stats
            try:
                from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
                verify_jwt_in_request()
                user_id = int(get_jwt_identity())
            except:
                return jsonify({'error': 'Authentication required to view your stats'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        projects = Project.query.filter_by(user_id=user_id).all()

        total_spent = sum(
            (p.deposit_amount or 0)
            for p in projects
            if p.status not in ('cancelled',)
        )

        return jsonify({'stats': {
            'total_projects':            len(projects),
            'pending_projects':          sum(1 for p in projects if p.status == 'pending'),
            'in_progress_projects':      sum(1 for p in projects if p.status == 'in_progress'),
            'completed_projects':        sum(1 for p in projects if p.status == 'completed'),
            'payment_required_projects': sum(1 for p in projects if p.status == 'payment_required'),
            'total_spent':               total_spent,
        }}), 200

    except Exception as e:
        return jsonify({'error': 'Failed to get stats', 'details': str(e)}), 500