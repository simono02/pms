from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from app import db, limiter
from app.models.user import User
from app.models.staff import Staff
from app.models.project import Project
from app.models.payment import Payment
from app.modules.staff import StaffModule
from app.middleware.auth import admin_required
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# ======================================================================
# DEBUG HELPER — remove once 422 is resolved
# ======================================================================

def _log_jwt_debug():
    """Log JWT state for every request to help diagnose 422s."""
    auth_header = request.headers.get('Authorization', 'MISSING')
    logger.warning(f"[JWT DEBUG] Method={request.method} Path={request.path}")
    logger.warning(f"[JWT DEBUG] Authorization header: {auth_header[:40] if auth_header != 'MISSING' else 'MISSING'}")

    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        parts = token.split('.')
        logger.warning(f"[JWT DEBUG] Token segments: {len(parts)} (need 3)")
        if len(parts) == 3:
            import base64, json
            try:
                # Decode payload without verification
                padded = parts[1] + '=' * (4 - len(parts[1]) % 4)
                payload = json.loads(base64.b64decode(padded))
                logger.warning(f"[JWT DEBUG] sub={payload.get('sub')!r}  type={type(payload.get('sub')).__name__}")
                logger.warning(f"[JWT DEBUG] role={payload.get('role')!r}")
                logger.warning(f"[JWT DEBUG] exp={payload.get('exp')}")
            except Exception as ex:
                logger.warning(f"[JWT DEBUG] Could not decode payload: {ex}")
    else:
        logger.warning("[JWT DEBUG] No Bearer token found in request")


# ======================================================================
# DASHBOARD STATS
# ======================================================================

@bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_dashboard_stats():
    _log_jwt_debug()
    try:
        total_users  = User.query.filter_by(role='user').count()
        total_staff  = Staff.query.count()
        active_users = User.query.filter_by(status='active', role='user').count()

        total_projects            = Project.query.count()
        pending_projects          = Project.query.filter_by(status='pending').count()
        in_progress_projects      = Project.query.filter_by(status='in_progress').count()
        completed_projects        = Project.query.filter_by(status='completed').count()
        payment_required_projects = Project.query.filter_by(status='payment_required').count()

        total_revenue = db.session.query(db.func.sum(Payment.amount)) \
                            .filter_by(status='completed').scalar() or 0

        return jsonify({
            'stats': {
                'users':    {'total': total_users, 'staff': total_staff, 'active': active_users},
                'projects': {
                    'total':            total_projects,
                    'pending':          pending_projects,
                    'in_progress':      in_progress_projects,
                    'completed':        completed_projects,
                    'payment_required': payment_required_projects,
                },
                'revenue': float(total_revenue),
            }
        }), 200

    except Exception as e:
        logger.error(f"[dashboard/stats] {e}", exc_info=True)
        return jsonify({'error': 'Failed to get dashboard stats', 'details': str(e)}), 500


# ======================================================================
# CLIENTS
# ======================================================================

@bp.route('/clients', methods=['GET'])
@jwt_required()
@admin_required
def get_clients():
    try:
        page     = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        status   = request.args.get('status')
        search   = request.args.get('search')

        query = User.query.filter_by(role='user')
        if status:
            query = query.filter_by(status=status)
        if search:
            query = query.filter(
                db.or_(User.name.ilike(f'%{search}%'),
                       User.email.ilike(f'%{search}%'))
            )
        users = query.order_by(User.created_at.desc()) \
                     .paginate(page=page, per_page=per_page, error_out=False)

        clients = []
        for user in users.items:
            data = user.to_dict()
            data['project_count'] = user.get_projects_count()
            clients.append(data)

        return jsonify({
            'clients': clients,
            'pagination': {
                'page': users.page, 'per_page': users.per_page,
                'total': users.total, 'pages': users.pages,
                'has_next': users.has_next, 'has_prev': users.has_prev,
            },
        }), 200

    except Exception as e:
        logger.error(f"[clients GET] {e}", exc_info=True)
        return jsonify({'error': 'Failed to get clients', 'details': str(e)}), 500


@bp.route('/clients/<int:client_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_client(client_id):
    try:
        user = User.find_by_id(client_id)
        if not user or user.role != 'user':
            return jsonify({'error': 'Client not found'}), 404
        data = user.to_dict()
        data['projects'] = [p.to_dict(include_details=True) for p in user.projects]
        return jsonify({'client': data}), 200
    except Exception as e:
        logger.error(f"[clients/{client_id} GET] {e}", exc_info=True)
        return jsonify({'error': 'Failed to get client', 'details': str(e)}), 500


@bp.route('/clients/<int:client_id>/status', methods=['PUT'])
@jwt_required()
@admin_required
@limiter.limit("10 per minute")
def update_client_status(client_id):
    try:
        user = User.find_by_id(client_id)
        if not user or user.role != 'user':
            return jsonify({'error': 'Client not found'}), 404
        data       = request.get_json() or {}
        new_status = data.get('status', '').strip()
        if new_status not in ['active', 'inactive']:
            return jsonify({'error': 'Status must be active or inactive'}), 400
        user.activate() if new_status == 'active' else user.deactivate()
        return jsonify({'message': f'Client {new_status} successfully', 'user': user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"[clients/{client_id}/status] {e}", exc_info=True)
        return jsonify({'error': 'Failed to update client status', 'details': str(e)}), 500


@bp.route('/clients/<int:client_id>', methods=['DELETE'])
@jwt_required()
@admin_required
@limiter.limit("5 per minute")
def delete_client(client_id):
    try:
        user = User.find_by_id(client_id)
        if not user or user.role != 'user':
            return jsonify({'error': 'Client not found'}), 404
        active = [p for p in user.projects if p.status in ['pending', 'in_progress']]
        if active:
            return jsonify({'error': 'Cannot delete client with active projects'}), 400
        user.delete()
        return jsonify({'message': 'Client deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"[clients/{client_id} DELETE] {e}", exc_info=True)
        return jsonify({'error': 'Failed to delete client', 'details': str(e)}), 500


# ======================================================================
# STAFF — GET ALL
# ======================================================================

@bp.route('/staff', methods=['GET'])
@jwt_required()
@admin_required
def get_staff():
    _log_jwt_debug()
    try:
        logger.info("[staff GET] Request received")
        search = request.args.get('search', '').strip().lower()
        query  = Staff.query.join(Staff.user)
        if search:
            query = query.filter(
                db.or_(
                    User.name.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%'),
                    Staff.specialization.ilike(f'%{search}%'),
                    Staff.id_number.ilike(f'%{search}%'),
                )
            )
        query = query.order_by(Staff.rating.desc(), Staff.experience_years.desc())

        staff_list = []
        for s in query.all():
            data = StaffModule.to_dict(s)
            data['projects'] = [
                {
                    'id':             p.id,
                    'title':          p.title,
                    'field_of_study': p.research_field,
                    'status':         p.status,
                    'created_at':     p.created_at.isoformat(),
                    'user':           {'name': p.user.name} if p.user else None,
                }
                for p in s.assigned_projects.all()
            ]
            staff_list.append(data)

        logger.info(f"[staff GET] Returning {len(staff_list)} staff members")
        return jsonify({'staff': staff_list, 'total': len(staff_list)}), 200

    except Exception as e:
        logger.error(f"[staff GET] {e}", exc_info=True)
        return jsonify({'error': 'Failed to get staff', 'details': str(e)}), 500


# ======================================================================
# STAFF — CREATE
# ======================================================================

@bp.route('/staff', methods=['POST'])
@jwt_required()
@admin_required
@limiter.limit("20 per hour")
def add_staff():
    _log_jwt_debug()
    try:
        logger.info("[staff POST] Request received")
        data = request.get_json() or {}
        logger.info(f"[staff POST] Payload keys: {list(data.keys())}")

        name      = (data.get('name') or '').strip()
        email     = (data.get('email') or '').strip().lower()
        id_number = (data.get('id_number') or '').strip()
        spec      = (data.get('specialization') or '').strip()

        if not name:
            return jsonify({'error': 'name is required.'}), 400
        if len(name) < 2:
            return jsonify({'error': 'name must be at least 2 characters.'}), 400
        if not email:
            return jsonify({'error': 'email is required.'}), 400
        if not id_number:
            return jsonify({'error': 'id_number is required.'}), 400
        if not spec:
            return jsonify({'error': 'specialization is required.'}), 400

        phone         = (data.get('phone') or '').strip() or None
        qualification = (data.get('qualification') or '').strip() or None
        bio           = (data.get('bio') or '').strip() or None

        try:
            experience_years = int(data.get('experience_years') or 0)
            if experience_years < 0:
                return jsonify({'error': 'experience_years must be 0 or more.'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'experience_years must be a number.'}), 400

        try:
            rate_per_page = float(data['rate_per_page']) \
                if data.get('rate_per_page') not in (None, '') else None
        except (ValueError, TypeError):
            return jsonify({'error': 'rate_per_page must be a number.'}), 400

        try:
            rate_per_chapter = float(data['rate_per_chapter']) \
                if data.get('rate_per_chapter') not in (None, '') else None
        except (ValueError, TypeError):
            return jsonify({'error': 'rate_per_chapter must be a number.'}), 400

        skills_raw = data.get('skills', [])
        if isinstance(skills_raw, str):
            skills = [s.strip() for s in skills_raw.split(',') if s.strip()]
        elif isinstance(skills_raw, list):
            skills = [s.strip() for s in skills_raw if s.strip()]
        else:
            skills = []

        logger.info(f"[staff POST] Creating staff: name={name} email={email} id={id_number}")

        staff = StaffModule.create_staff(
            name=name, email=email, id_number=id_number,
            specialization=spec, experience_years=experience_years,
            qualification=qualification, bio=bio,
            rate_per_page=rate_per_page, rate_per_chapter=rate_per_chapter,
            skills=skills, phone=phone,
        )

        logger.info(f"[staff POST] Staff created successfully: id={staff.id}")
        return jsonify({
            'message': 'Staff member created. A setup email has been sent.',
            'staff':   StaffModule.to_dict(staff),
        }), 201

    except ValueError as e:
        logger.warning(f"[staff POST] Validation error: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"[staff POST] {e}", exc_info=True)
        return jsonify({'error': 'Failed to add staff member', 'details': str(e)}), 500


# ======================================================================
# STAFF — GET ONE
# ======================================================================

@bp.route('/staff/<int:staff_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_staff_member(staff_id):
    try:
        staff = StaffModule.find_by_id(staff_id)
        if not staff:
            return jsonify({'error': 'Staff member not found'}), 404
        data = StaffModule.to_dict(staff)
        data['projects'] = [
            {
                'id':             p.id,
                'title':          p.title,
                'field_of_study': p.research_field,
                'status':         p.status,
                'created_at':     p.created_at.isoformat(),
                'user':           {'name': p.user.name} if p.user else None,
            }
            for p in staff.assigned_projects.all()
        ]
        return jsonify({'staff': data}), 200
    except Exception as e:
        logger.error(f"[staff/{staff_id} GET] {e}", exc_info=True)
        return jsonify({'error': 'Failed to get staff member', 'details': str(e)}), 500


# ======================================================================
# STAFF — UPDATE
# ======================================================================

@bp.route('/staff/<int:staff_id>', methods=['PUT'])
@jwt_required()
@admin_required
@limiter.limit("10 per minute")
def update_staff(staff_id):
    try:
        staff = StaffModule.find_by_id(staff_id)
        if not staff:
            return jsonify({'error': 'Staff member not found'}), 404

        data    = request.get_json() or {}
        updates = {}

        if 'name' in data:
            name = data['name'].strip()
            if len(name) < 2:
                return jsonify({'error': 'name must be at least 2 characters.'}), 400
            staff.user.name = name

        if 'phone' in data:
            staff.user.phone = (data['phone'] or '').strip() or None

        db.session.flush()

        for field in ('specialization', 'qualification', 'bio'):
            if field in data:
                updates[field] = data[field]

        if 'experience_years' in data:
            try:
                exp = int(data['experience_years'])
                if exp < 0:
                    return jsonify({'error': 'experience_years must be 0 or more.'}), 400
                updates['experience_years'] = exp
            except (ValueError, TypeError):
                return jsonify({'error': 'experience_years must be a number.'}), 400

        for rate_field in ('rate_per_page', 'rate_per_chapter'):
            if rate_field in data:
                try:
                    updates[rate_field] = float(data[rate_field])
                except (ValueError, TypeError):
                    return jsonify({'error': f'{rate_field} must be a number.'}), 400

        if 'availability' in data:
            updates['availability'] = bool(data['availability'])

        if 'skills' in data:
            skills = data['skills']
            if isinstance(skills, str):
                skills = [s.strip() for s in skills.split(',') if s.strip()]
            updates['skills'] = skills

        StaffModule.update_profile(staff, **updates)
        return jsonify({'message': 'Staff member updated successfully',
                        'staff':   StaffModule.to_dict(staff)}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"[staff/{staff_id} PUT] {e}", exc_info=True)
        return jsonify({'error': 'Failed to update staff member', 'details': str(e)}), 500


# ======================================================================
# STAFF — STATUS
# ======================================================================

@bp.route('/staff/<int:staff_id>/status', methods=['PUT'])
@jwt_required()
@admin_required
@limiter.limit("10 per minute")
def update_staff_status(staff_id):
    try:
        staff = StaffModule.find_by_id(staff_id)
        if not staff:
            return jsonify({'error': 'Staff member not found'}), 404
        data       = request.get_json() or {}
        new_status = data.get('status', '').strip()
        if new_status not in ['active', 'inactive']:
            return jsonify({'error': 'Status must be active or inactive'}), 400
        StaffModule.set_availability(staff, new_status == 'active')
        return jsonify({'message': f'Staff member set to {new_status}',
                        'staff':   StaffModule.to_dict(staff)}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"[staff/{staff_id}/status] {e}", exc_info=True)
        return jsonify({'error': 'Failed to update staff status', 'details': str(e)}), 500


# ======================================================================
# STAFF — RESEND INVITE
# ======================================================================

@bp.route('/staff/<int:staff_id>/resend-invite', methods=['POST'])
@jwt_required()
@admin_required
@limiter.limit("10 per hour")
def resend_staff_invite(staff_id):
    try:
        staff = StaffModule.find_by_id(staff_id)
        if not staff:
            return jsonify({'error': 'Staff member not found'}), 404
        StaffModule.resend_verification_email(staff)
        return jsonify({'message': f'Setup email resent to {staff.user.email}.'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"[staff/{staff_id}/resend-invite] {e}", exc_info=True)
        return jsonify({'error': 'Failed to resend invite', 'details': str(e)}), 500


# ======================================================================
# STAFF — DELETE
# ======================================================================

@bp.route('/staff/<int:staff_id>', methods=['DELETE'])
@jwt_required()
@admin_required
@limiter.limit("5 per minute")
def delete_staff(staff_id):
    try:
        staff = StaffModule.find_by_id(staff_id)
        if not staff:
            return jsonify({'error': 'Staff member not found'}), 404
        active = StaffModule.get_active_projects(staff)
        if active:
            return jsonify({'error': f'Cannot delete staff with {len(active)} active project(s).'}), 400
        StaffModule.delete(staff)
        return jsonify({'message': 'Staff member deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"[staff/{staff_id} DELETE] {e}", exc_info=True)
        return jsonify({'error': 'Failed to delete staff member', 'details': str(e)}), 500


# ======================================================================
# PROJECTS
# ======================================================================

@bp.route('/projects', methods=['GET'])
@jwt_required()
@admin_required
def get_all_projects():
    try:
        page     = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        status   = request.args.get('status')
        user_id  = request.args.get('user_id', type=int)
        staff_id = request.args.get('staff_id', type=int)
        search   = request.args.get('search')

        query = Project.query
        if status:   query = query.filter_by(status=status)
        if user_id:  query = query.filter_by(user_id=user_id)
        if staff_id: query = query.filter_by(assigned_staff_id=staff_id)
        if search:   query = query.filter(Project.title.ilike(f'%{search}%'))

        projects = query.order_by(Project.created_at.desc()) \
                        .paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'projects': [p.to_dict(include_details=True) for p in projects.items],
            'pagination': {
                'page': projects.page, 'per_page': projects.per_page,
                'total': projects.total, 'pages': projects.pages,
                'has_next': projects.has_next, 'has_prev': projects.has_prev,
            },
        }), 200

    except Exception as e:
        logger.error(f"[projects GET] {e}", exc_info=True)
        return jsonify({'error': 'Failed to get projects', 'details': str(e)}), 500


@bp.route('/projects/unassigned', methods=['GET'])
@jwt_required()
@admin_required
def get_unassigned_projects():
    try:
        projects = Project.get_unassigned_projects()
        return jsonify({'projects': [p.to_dict(include_details=True) for p in projects]}), 200
    except Exception as e:
        logger.error(f"[projects/unassigned] {e}", exc_info=True)
        return jsonify({'error': 'Failed to get unassigned projects', 'details': str(e)}), 500


@bp.route('/projects/<int:project_id>/allocate', methods=['POST'])
@jwt_required()
@admin_required
@limiter.limit("10 per minute")
def allocate_project(project_id):
    try:
        project = Project.find_by_id(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        data     = request.get_json() or {}
        staff_id = data.get('staff_id')
        if not staff_id:
            return jsonify({'error': 'staff_id is required'}), 400
        staff = StaffModule.find_by_id(staff_id)
        if not staff:
            return jsonify({'error': 'Staff member not found'}), 404
        if not StaffModule.can_take_project(staff):
            return jsonify({'error': 'Staff member cannot take more projects'}), 400
        project.assign_to_staff(staff_id)
        return jsonify({'message': 'Project allocated successfully',
                        'project': project.to_dict(include_details=True)}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"[projects/{project_id}/allocate] {e}", exc_info=True)
        return jsonify({'error': 'Failed to allocate project', 'details': str(e)}), 500


@bp.route('/projects/<int:project_id>/unallocate', methods=['POST'])
@jwt_required()
@admin_required
@limiter.limit("10 per minute")
def unallocate_project(project_id):
    try:
        project = Project.find_by_id(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        project.unassign_staff()
        return jsonify({'message': 'Project unallocated successfully',
                        'project': project.to_dict(include_details=True)}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"[projects/{project_id}/unallocate] {e}", exc_info=True)
        return jsonify({'error': 'Failed to unallocate project', 'details': str(e)}), 500


# ======================================================================
# PAYMENTS
# ======================================================================

@bp.route('/payments', methods=['GET'])
@jwt_required()
@admin_required
def get_all_payments():
    try:
        page     = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        status   = request.args.get('status')
        user_id  = request.args.get('user_id', type=int)

        query = Payment.query
        if status:  query = query.filter_by(status=status)
        if user_id: query = query.filter_by(user_id=user_id)

        payments = query.order_by(Payment.created_at.desc()) \
                        .paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'payments': [p.to_dict() for p in payments.items],
            'pagination': {
                'page': payments.page, 'per_page': payments.per_page,
                'total': payments.total, 'pages': payments.pages,
                'has_next': payments.has_next, 'has_prev': payments.has_prev,
            },
        }), 200

    except Exception as e:
        logger.error(f"[payments GET] {e}", exc_info=True)
        return jsonify({'error': 'Failed to get payments', 'details': str(e)}), 500


@bp.route('/payments/<int:payment_id>/refund', methods=['POST'])
@jwt_required()
@admin_required
@limiter.limit("5 per minute")
def refund_payment(payment_id):
    try:
        payment = Payment.find_by_id(payment_id)
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        data   = request.get_json() or {}
        reason = (data.get('reason') or '').strip()
        if not reason:
            return jsonify({'error': 'Refund reason is required'}), 400
        if not payment.can_be_refunded():
            return jsonify({'error': 'Payment cannot be refunded'}), 400
        payment.refund_payment(reason)
        return jsonify({'message': 'Payment refunded successfully',
                        'payment': payment.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"[payments/{payment_id}/refund] {e}", exc_info=True)
        return jsonify({'error': 'Failed to refund payment', 'details': str(e)}), 500


# ======================================================================
# ANALYTICS
# ======================================================================

@bp.route('/analytics', methods=['GET'])
@jwt_required()
@admin_required
def get_analytics():
    try:
        return jsonify({'analytics': {
            'totalRevenue': 15000.50, 'revenueGrowth': 12.5,
            'newUsers': 45, 'userGrowth': 8.2,
            'completedProjects': 23, 'projectGrowth': 15.3,
            'activeStaff': 8,
            'topFields': [
                {'name': 'Computer Science', 'count': 15},
                {'name': 'Engineering',      'count': 12},
                {'name': 'Medicine',         'count': 8},
                {'name': 'Business',         'count': 6},
            ],
            'topStaff': [
                {'name': 'John Doe',    'completedProjects': 5, 'rating': 4.8},
                {'name': 'Jane Smith',  'completedProjects': 4, 'rating': 4.6},
                {'name': 'Bob Johnson', 'completedProjects': 3, 'rating': 4.5},
            ],
            'recentActivity': [
                {'date': '2024-01-15', 'user': 'John Doe',  'action': 'Completed project', 'details': 'AI Research Paper'},
                {'date': '2024-01-14', 'user': 'Jane Smith', 'action': 'New project',      'details': 'Data Analysis'},
                {'date': '2024-01-13', 'user': 'Admin',      'action': 'Staff added',      'details': 'New team member'},
            ],
        }}), 200
    except Exception as e:
        logger.error(f"[analytics] {e}", exc_info=True)
        return jsonify({'error': 'Failed to get analytics', 'details': str(e)}), 500