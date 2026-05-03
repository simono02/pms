from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, limiter
from app.models.staff import Staff
from app.models.user import User
from app.models.project import Project
from app.modules.staff import StaffModule

bp = Blueprint('staff', __name__, url_prefix='/api/staff')


# ──────────────────────────────────────────────────────────────────────
# HELPER
# ──────────────────────────────────────────────────────────────────────

def _get_current_staff():
    """Return (user, staff) for the logged-in staff member, or (None, None)."""
    user_id = int(get_jwt_identity())          # ← cast string → int
    user    = User.query.get(user_id)
    if not user or user.role != 'staff':
        return None, None
    staff = StaffModule.find_by_user_id(user_id)
    return user, staff


# ──────────────────────────────────────────────────────────────────────
# PUBLIC — password setup (no JWT, called from the email link)
# ──────────────────────────────────────────────────────────────────────

@bp.route('/verify-token', methods=['GET'])
def verify_token():
    token = request.args.get('token', '').strip()
    if not token:
        return jsonify({'valid': False, 'error': 'Token is required.'}), 400
    try:
        staff = StaffModule.find_by_token(token)
        if not staff:
            return jsonify({'valid': False, 'error': 'Invalid token.'}), 400
        from datetime import datetime
        if not staff.verification_token_expires or \
                datetime.utcnow() > staff.verification_token_expires:
            return jsonify({'valid': False, 'error': 'Token has expired.'}), 400
        return jsonify({'valid': True, 'name': staff.user.name, 'email': staff.user.email}), 200
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 500


@bp.route('/setup-password', methods=['POST'])
def setup_password():
    try:
        data             = request.get_json() or {}
        token            = (data.get('token') or '').strip()
        password         = data.get('password', '')
        password_confirm = data.get('password_confirm', '')

        if not token:
            return jsonify({'error': 'Verification token is required.'}), 400
        if not password:
            return jsonify({'error': 'Password is required.'}), 400
        if password != password_confirm:
            return jsonify({'error': 'Passwords do not match.'}), 400

        staff = StaffModule.verify_and_set_password(token, password)

        from flask_jwt_extended import create_access_token, create_refresh_token
        access_token  = create_access_token(identity=str(staff.user_id))   # ← string
        refresh_token = create_refresh_token(identity=str(staff.user_id))  # ← string

        return jsonify({
            'message':       'Password set successfully. Welcome aboard!',
            'access_token':  access_token,
            'refresh_token': refresh_token,
            'staff':         StaffModule.to_dict(staff),
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to set password.', 'details': str(e)}), 500


@bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    try:
        data  = request.get_json() or {}
        email = (data.get('email') or '').strip().lower()
        if not email:
            return jsonify({'error': 'email is required.'}), 400

        user = User.query.filter_by(email=email).first()
        if user and user.role == 'staff':
            staff = StaffModule.find_by_user_id(user.id)
            if staff:
                try:
                    StaffModule.resend_verification_email(staff)
                except ValueError:
                    pass

        return jsonify({
            'message': 'If that email belongs to a pending staff account, a new link has been sent.'
        }), 200

    except Exception as e:
        return jsonify({'error': 'Failed to resend email.', 'details': str(e)}), 500


# ──────────────────────────────────────────────────────────────────────
# OWN PROFILE
# ──────────────────────────────────────────────────────────────────────

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user, staff = _get_current_staff()
        if not staff:
            return jsonify({'error': 'Staff profile not found.'}), 404
        return jsonify({'staff': StaffModule.to_dict(staff)}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get profile.', 'details': str(e)}), 500


@bp.route('/profile', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per minute")
def update_profile():
    try:
        user, staff = _get_current_staff()
        if not staff:
            return jsonify({'error': 'Staff profile not found.'}), 404

        data    = request.get_json() or {}
        updates = {}

        if 'phone' in data:
            user.phone = (data['phone'] or '').strip() or None
            db.session.flush()

        if 'specialization' in data:
            updates['specialization'] = data['specialization']

        if 'experience_years' in data:
            try:
                exp = int(data['experience_years'])
                if exp < 0:
                    return jsonify({'error': 'experience_years must be 0 or more.'}), 400
                updates['experience_years'] = exp
            except (ValueError, TypeError):
                return jsonify({'error': 'experience_years must be a number.'}), 400

        if 'qualification' in data:
            updates['qualification'] = data['qualification']

        if 'bio' in data:
            updates['bio'] = data['bio']

        if 'rate_per_page' in data:
            try:
                rate = float(data['rate_per_page'])
                if rate < 0:
                    return jsonify({'error': 'rate_per_page must be 0 or more.'}), 400
                updates['rate_per_page'] = rate
            except (ValueError, TypeError):
                return jsonify({'error': 'rate_per_page must be a number.'}), 400

        if 'rate_per_chapter' in data:
            try:
                rate = float(data['rate_per_chapter'])
                if rate < 0:
                    return jsonify({'error': 'rate_per_chapter must be 0 or more.'}), 400
                updates['rate_per_chapter'] = rate
            except (ValueError, TypeError):
                return jsonify({'error': 'rate_per_chapter must be a number.'}), 400

        if 'skills' in data:
            skills = data['skills']
            if isinstance(skills, str):
                skills = [s.strip() for s in skills.split(',') if s.strip()]
            updates['skills'] = skills

        StaffModule.update_profile(staff, **updates)

        return jsonify({
            'message': 'Profile updated successfully.',
            'staff':   StaffModule.to_dict(staff),
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile.', 'details': str(e)}), 500


# ──────────────────────────────────────────────────────────────────────
# OWN PROJECTS
# ──────────────────────────────────────────────────────────────────────

@bp.route('/projects', methods=['GET'])
@jwt_required()
def get_my_projects():
    try:
        user, staff = _get_current_staff()
        if not staff:
            return jsonify({'error': 'Staff profile not found.'}), 404

        page     = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        status   = request.args.get('status')

        query = Project.query.filter_by(assigned_staff_id=staff.id)
        if status:
            query = query.filter_by(status=status)
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
        return jsonify({'error': 'Failed to get projects.', 'details': str(e)}), 500


@bp.route('/projects/<int:project_id>', methods=['GET'])
@jwt_required()
def get_my_project(project_id):
    try:
        user, staff = _get_current_staff()
        if not staff:
            return jsonify({'error': 'Staff profile not found.'}), 404

        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found.'}), 404
        if project.assigned_staff_id != staff.id:
            return jsonify({'error': 'Access denied.'}), 403

        return jsonify({'project': project.to_dict(include_details=True)}), 200

    except Exception as e:
        return jsonify({'error': 'Failed to get project.', 'details': str(e)}), 500


@bp.route('/projects/<int:project_id>/status', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per minute")
def update_project_status(project_id):
    try:
        user, staff = _get_current_staff()
        if not staff:
            return jsonify({'error': 'Staff profile not found.'}), 404

        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found.'}), 404
        if project.assigned_staff_id != staff.id:
            return jsonify({'error': 'Access denied.'}), 403

        data       = request.get_json() or {}
        new_status = (data.get('status') or '').strip()

        if not new_status:
            return jsonify({'error': 'status is required.'}), 400
        if new_status not in ('in_progress', 'completed'):
            return jsonify({'error': 'You may only set status to in_progress or completed.'}), 400

        project.update_status(new_status)
        if new_status == 'completed':
            StaffModule.complete_project(staff, project)

        return jsonify({
            'message': 'Project status updated.',
            'project': project.to_dict(include_details=True),
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update status.', 'details': str(e)}), 500


@bp.route('/projects/<int:project_id>/result', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def upload_result(project_id):
    try:
        user, staff = _get_current_staff()
        if not staff:
            return jsonify({'error': 'Staff profile not found.'}), 404

        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found.'}), 404
        if project.assigned_staff_id != staff.id:
            return jsonify({'error': 'Access denied.'}), 403
        if project.status != 'in_progress':
            return jsonify({'error': 'Project must be in_progress to upload a result.'}), 400

        data = request.get_json() or {}
        if not data.get('file_path'):
            return jsonify({'error': 'file_path is required.'}), 400
        if not data.get('description'):
            return jsonify({'error': 'description is required.'}), 400

        project.complete_project(
            result_path=data['file_path'],
            result_filename=data.get('result_filename'),
        )

        return jsonify({
            'message': 'Result uploaded successfully.',
            'project': project.to_dict(include_details=True),
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to upload result.', 'details': str(e)}), 500


# ──────────────────────────────────────────────────────────────────────
# AVAILABLE PROJECTS
# ──────────────────────────────────────────────────────────────────────

@bp.route('/available-projects', methods=['GET'])
@jwt_required()
def get_available_projects():
    try:
        user, staff = _get_current_staff()
        if not staff:
            return jsonify({'error': 'Staff profile not found.'}), 404
        if not StaffModule.can_take_project(staff):
            return jsonify({'error': 'You have reached the maximum number of active projects.'}), 400

        projects = Project.query.filter_by(status='pending', assigned_staff_id=None).all()
        if staff.specialization:
            projects = [p for p in projects if p.research_field == staff.specialization]

        active = StaffModule.get_active_projects(staff)
        return jsonify({
            'projects':        [p.to_dict(include_details=True) for p in projects],
            'available_slots': 5 - len(active),
        }), 200

    except Exception as e:
        return jsonify({'error': 'Failed to get available projects.', 'details': str(e)}), 500


@bp.route('/request-project/<int:project_id>', methods=['POST'])
@jwt_required()
@limiter.limit("3 per minute")
def request_project(project_id):
    try:
        user, staff = _get_current_staff()
        if not staff:
            return jsonify({'error': 'Staff profile not found.'}), 404

        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found.'}), 404
        if project.status != 'pending' or project.assigned_staff_id:
            return jsonify({'error': 'Project is not available for assignment.'}), 400

        StaffModule.assign_project(staff, project)

        return jsonify({
            'message': 'Project assigned successfully.',
            'project': project.to_dict(include_details=True),
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to assign project.', 'details': str(e)}), 500


# ──────────────────────────────────────────────────────────────────────
# DASHBOARD & STATS
# ──────────────────────────────────────────────────────────────────────

@bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    try:
        user, staff = _get_current_staff()
        if not staff:
            return jsonify({'error': 'Staff profile not found.'}), 404
        return jsonify({'stats': StaffModule.get_performance_stats(staff)}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get stats.', 'details': str(e)}), 500


@bp.route('/workload', methods=['GET'])
@jwt_required()
def get_workload():
    try:
        user, staff = _get_current_staff()
        if not staff:
            return jsonify({'error': 'Staff profile not found.'}), 404

        active = StaffModule.get_active_projects(staff)

        return jsonify({
            'workload': {
                'active_projects': len(active),
                'max_projects':    5,
                'available_slots': 5 - len(active),
                'can_take_more':   StaffModule.can_take_project(staff),
                'projects': [
                    {
                        'id':         p.id,
                        'title':      p.title,
                        'status':     p.status,
                        'created_at': p.created_at.isoformat(),
                        'deadline':   p.deadline.isoformat() if getattr(p, 'deadline', None) else None,
                    }
                    for p in active
                ],
            }
        }), 200

    except Exception as e:
        return jsonify({'error': 'Failed to get workload.', 'details': str(e)}), 500


@bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    try:
        user, staff = _get_current_staff()
        if not staff:
            return jsonify({'error': 'Staff profile not found.'}), 404
        return jsonify({'notifications': [], 'unread_count': 0}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get notifications.', 'details': str(e)}), 500