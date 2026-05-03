from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, limiter
from app.models.project import Project
from app.models.user import User
from app.models.staff import Staff
from app.utils.validators import validators
import os
import uuid

# ✅ ADDED: Import modules
from app.modules.user import UserModule
from app.modules.staff import StaffModule
from app.modules.project import ProjectModule

bp = Blueprint('projects', __name__, url_prefix='/api/projects')

@bp.route('/', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def create_project():
    """Create a new project from dashboard"""
    try:
        current_user_id = get_jwt_identity()
        user = UserModule.find_by_id(current_user_id)  # ✅ CHANGED
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # ✅ NEW: Validate required fields for dashboard
        required_fields = ['projectType', 'academicLevel', 'citationStyle', 
                          'researchQuestion', 'description', 'pricingType']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # ✅ NEW: Validate pricing type and quantity
        pricing_type = data.get('pricingType')
        if pricing_type not in ['per-page', 'per-chapter']:
            return jsonify({'error': 'Invalid pricing type'}), 400
        
        if pricing_type == 'per-page':
            if not data.get('pages'):
                return jsonify({'error': 'Number of pages is required'}), 400
            try:
                pages = int(data['pages'])
                if pages < 1:
                    return jsonify({'error': 'Pages must be at least 1'}), 400
            except ValueError:
                return jsonify({'error': 'Invalid pages format'}), 400
        
        if pricing_type == 'per-chapter':
            if not data.get('chapters'):
                return jsonify({'error': 'Number of chapters is required'}), 400
            try:
                chapters = int(data['chapters'])
                if chapters < 1:
                    return jsonify({'error': 'Chapters must be at least 1'}), 400
            except ValueError:
                return jsonify({'error': 'Invalid chapters format'}), 400
        
        # ✅ NEW: Calculate pricing
        quantity = int(data.get('pages') or data.get('chapters'))
        pricing = ProjectModule.calculate_pricing(pricing_type, quantity)  # ✅ CHANGED
        
        # ✅ NEW: Generate title from research question if not provided
        title = data.get('title') or data.get('researchQuestion', 'Research Project')[:200]
        
        # ✅ NEW: Create project with all dashboard fields
        project = Project(
            user_id=current_user_id,
            title=title,
            project_type=data.get('projectType'),
            academic_level=data.get('academicLevel'),
            research_question=data.get('researchQuestion'),
            description=data.get('description'),
            keywords=data.get('keywords'),
            citation_style=data.get('citationStyle'),
            methodology=data.get('methodology'),
            specific_requirements=data.get('specificRequirements'),
            pricing_type=pricing_type,
            pages=data.get('pages'),
            chapters=data.get('chapters'),
            price_per_unit=pricing['price_per_unit'],
            total_price=pricing['total_price'],
            deposit_amount=pricing['deposit_amount'],
            balance_amount=pricing['balance_amount'],
            currency='KES',
            status='pending',
            progress=0,
            priority=data.get('priority', 'medium')
        )
        
        # ✅ NEW: Handle description file if uploaded
        if data.get('descriptionFile'):
            # TODO: Handle file upload
            # project.description_file_path = uploaded_file_path
            # project.description_file_name = uploaded_file_name
            pass
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'message': 'Project created successfully',
            'project': ProjectModule.to_dict(project, include_details=True)  # ✅ CHANGED
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create project', 'details': str(e)}), 500

@bp.route('/', methods=['GET'])
@jwt_required()
def get_projects():
    """Get projects (with filtering and pagination)"""
    try:
        current_user_id = get_jwt_identity()
        user = UserModule.find_by_id(current_user_id)  # ✅ CHANGED
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        status = request.args.get('status')
        research_field = request.args.get('research_field')
        search = request.args.get('search')
        user_id = request.args.get('user_id', type=int)
        staff_id = request.args.get('staff_id', type=int)
        
        # Build query
        query = Project.query
        
        # ✅ NEW: Regular users can only see their own projects
        if not UserModule.is_admin(user):  # ✅ CHANGED
            query = query.filter_by(user_id=current_user_id)
        elif user_id:
            query = query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if research_field:
            query = query.filter_by(research_field=research_field)
        
        if staff_id:
            query = query.filter_by(assigned_staff_id=staff_id)
        
        if search:
            query = query.filter(
                Project.title.contains(search) | 
                Project.research_question.contains(search)
            )
        
        # Order by most recent
        query = query.order_by(Project.created_at.desc())
        
        # Paginate
        projects = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'projects': [ProjectModule.to_dict(project, include_details=True) for project in projects.items],  # ✅ CHANGED
            'pagination': {
                'page': projects.page,
                'per_page': projects.per_page,
                'total': projects.total,
                'pages': projects.pages,
                'has_next': projects.has_next,
                'has_prev': projects.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get projects', 'details': str(e)}), 500

@bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """Get specific project"""
    try:
        current_user_id = get_jwt_identity()
        project = ProjectModule.find_by_id(project_id)  # ✅ CHANGED
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # ✅ NEW: Check access permissions
        user = UserModule.find_by_id(current_user_id)  # ✅ CHANGED
        if project.user_id != current_user_id and not UserModule.is_admin(user):  # ✅ CHANGED
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'project': ProjectModule.to_dict(project, include_details=True)  # ✅ CHANGED
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get project', 'details': str(e)}), 500

@bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per minute")
def update_project(project_id):
    """Update project"""
    try:
        current_user_id = get_jwt_identity()
        project = ProjectModule.find_by_id(project_id)  # ✅ CHANGED
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check permissions
        user = UserModule.find_by_id(current_user_id)  # ✅ CHANGED
        if project.user_id != current_user_id and not UserModule.is_admin(user):  # ✅ CHANGED
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if project can be edited
        if project.user_id == current_user_id and not ProjectModule.can_be_edited(project):  # ✅ CHANGED
            return jsonify({'error': 'Project can only be edited within 24 hours of creation'}), 400
        
        data = request.get_json()
        
        # ✅ NEW: Prepare update data
        update_data = {}
        
        # Update allowed fields
        if 'title' in data:
            title = data['title'].strip()
            if len(title) < 3:
                return jsonify({'error': 'Title must be at least 3 characters long'}), 400
            update_data['title'] = title
        
        if 'projectType' in data:
            update_data['project_type'] = data['projectType']
        
        if 'academicLevel' in data:
            update_data['academic_level'] = data['academicLevel']
        
        if 'researchQuestion' in data:
            update_data['research_question'] = data['researchQuestion']
        
        if 'citationStyle' in data:
            update_data['citation_style'] = data['citationStyle']
        
        if 'methodology' in data:
            update_data['methodology'] = data['methodology']
        
        if 'keywords' in data:
            update_data['keywords'] = data['keywords']
        
        if 'specificRequirements' in data:
            update_data['specific_requirements'] = data['specificRequirements']
        
        if 'description' in data:
            update_data['description'] = data['description']
        
        if 'priority' in data:
            if data['priority'] not in ['low', 'medium', 'high']:
                return jsonify({'error': 'Invalid priority level'}), 400
            update_data['priority'] = data['priority']
        
        # ✅ NEW: Recalculate pricing if pages/chapters changed
        if 'pages' in data or 'chapters' in data:
            pricing_type = data.get('pricingType', project.pricing_type)
            quantity = int(data.get('pages') or data.get('chapters'))
            
            pricing = ProjectModule.calculate_pricing(pricing_type, quantity)  # ✅ CHANGED
            
            update_data['pages'] = data.get('pages')
            update_data['chapters'] = data.get('chapters')
            update_data['pricing_type'] = pricing_type
            update_data['price_per_unit'] = pricing['price_per_unit']
            update_data['total_price'] = pricing['total_price']
            update_data['deposit_amount'] = pricing['deposit_amount']
            update_data['balance_amount'] = pricing['balance_amount']
        
        ProjectModule.update_details(project, **update_data)  # ✅ CHANGED
        
        return jsonify({
            'message': 'Project updated successfully',
            'project': ProjectModule.to_dict(project, include_details=True)  # ✅ CHANGED
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update project', 'details': str(e)}), 500

@bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
@limiter.limit("5 per minute")
def delete_project(project_id):
    """Delete project"""
    try:
        current_user_id = get_jwt_identity()
        project = ProjectModule.find_by_id(project_id)  # ✅ CHANGED
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check permissions
        user = UserModule.find_by_id(current_user_id)  # ✅ CHANGED
        if project.user_id != current_user_id and not UserModule.is_admin(user):  # ✅ CHANGED
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if project can be deleted
        if project.status == 'in_progress':
            return jsonify({'error': 'Cannot delete project that is in progress'}), 400
        
        if project.status == 'completed':
            return jsonify({'error': 'Cannot delete completed project'}), 400
        
        # Delete associated files
        if project.file_path and os.path.exists(project.file_path):
            os.remove(project.file_path)
        
        if project.result_path and os.path.exists(project.result_path):
            os.remove(project.result_path)
        
        if project.description_file_path and os.path.exists(project.description_file_path):
            os.remove(project.description_file_path)
        
        ProjectModule.delete(project)  # ✅ CHANGED
        
        return jsonify({'message': 'Project deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete project', 'details': str(e)}), 500

@bp.route('/<int:project_id>/progress', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per minute")
def update_project_progress(project_id):
    """Update project progress (staff only)"""
    try:
        current_user_id = get_jwt_identity()
        user = UserModule.find_by_id(current_user_id)  # ✅ CHANGED
        
        if not UserModule.is_staff(user) and not UserModule.is_admin(user):  # ✅ CHANGED
            return jsonify({'error': 'Access denied'}), 403
        
        project = ProjectModule.find_by_id(project_id)  # ✅ CHANGED
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check if staff is assigned to this project
        if UserModule.is_staff(user):  # ✅ CHANGED
            staff = StaffModule.find_by_user_id(current_user_id)  # ✅ CHANGED
            if project.assigned_staff_id != staff.id:
                return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        if 'progress' not in data:
            return jsonify({'error': 'Progress is required'}), 400
        
        try:
            progress = int(data['progress'])
            if not 0 <= progress <= 100:
                return jsonify({'error': 'Progress must be between 0 and 100'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid progress format'}), 400
        
        ProjectModule.update_progress(project, progress)  # ✅ CHANGED
        
        return jsonify({
            'message': 'Project progress updated successfully',
            'project': ProjectModule.to_dict(project, include_details=True)  # ✅ CHANGED
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update progress', 'details': str(e)}), 500

@bp.route('/<int:project_id>/assign', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def assign_project(project_id):
    """Assign project to staff member"""
    try:
        current_user_id = get_jwt_identity()
        user = UserModule.find_by_id(current_user_id)  # ✅ CHANGED
        
        if not UserModule.is_admin(user):  # ✅ CHANGED
            return jsonify({'error': 'Access denied'}), 403
        
        project = ProjectModule.find_by_id(project_id)  # ✅ CHANGED
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        
        if not data.get('staff_id'):
            return jsonify({'error': 'Staff ID is required'}), 400
        
        staff_id = data['staff_id']
        staff = StaffModule.find_by_id(staff_id)  # ✅ CHANGED
        
        if not staff:
            return jsonify({'error': 'Staff member not found'}), 404
        
        if not StaffModule.can_take_project(staff):  # ✅ CHANGED
            return jsonify({'error': 'Staff member cannot take more projects'}), 400
        
        ProjectModule.assign_to_staff(project, staff_id)  # ✅ CHANGED
        
        return jsonify({
            'message': 'Project assigned successfully',
            'project': ProjectModule.to_dict(project, include_details=True)  # ✅ CHANGED
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to assign project', 'details': str(e)}), 500

@bp.route('/<int:project_id>/unassign', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def unassign_project(project_id):
    """Unassign project from staff member"""
    try:
        current_user_id = get_jwt_identity()
        user = UserModule.find_by_id(current_user_id)  # ✅ CHANGED
        
        if not UserModule.is_admin(user):  # ✅ CHANGED
            return jsonify({'error': 'Access denied'}), 403
        
        project = ProjectModule.find_by_id(project_id)  # ✅ CHANGED
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        ProjectModule.unassign_staff(project)  # ✅ CHANGED
        
        return jsonify({
            'message': 'Project unassigned successfully',
            'project': ProjectModule.to_dict(project, include_details=True)  # ✅ CHANGED
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to unassign project', 'details': str(e)}), 500

@bp.route('/<int:project_id>/status', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per minute")
def update_project_status(project_id):
    """Update project status"""
    try:
        current_user_id = get_jwt_identity()
        project = ProjectModule.find_by_id(project_id)  # ✅ CHANGED
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        
        if not data.get('status'):
            return jsonify({'error': 'Status is required'}), 400
        
        new_status = data['status']
        
        # Check permissions
        user = UserModule.find_by_id(current_user_id)  # ✅ CHANGED
        
        # Staff can update status to in_progress or completed
        if UserModule.is_staff(user) and project.assigned_staff_id == user.staff_profile.id:  # ✅ CHANGED
            if new_status not in ['in_progress', 'payment_required']:
                return jsonify({'error': 'Invalid status for staff member'}), 400
        # Admin can update any status
        elif not UserModule.is_admin(user):  # ✅ CHANGED
            return jsonify({'error': 'Access denied'}), 403
        
        ProjectModule.update_status(project, new_status)  # ✅ CHANGED
        
        return jsonify({
            'message': 'Project status updated successfully',
            'project': ProjectModule.to_dict(project, include_details=True)  # ✅ CHANGED
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update status', 'details': str(e)}), 500

@bp.route('/unassigned', methods=['GET'])
@jwt_required()
def get_unassigned_projects():
    """Get unassigned projects"""
    try:
        current_user_id = get_jwt_identity()
        user = UserModule.find_by_id(current_user_id)  # ✅ CHANGED
        
        if not UserModule.is_admin(user):  # ✅ CHANGED
            return jsonify({'error': 'Access denied'}), 403
        
        projects = ProjectModule.get_unassigned_projects()  # ✅ CHANGED
        
        return jsonify({
            'projects': [ProjectModule.to_dict(project, include_details=True) for project in projects]  # ✅ CHANGED
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get unassigned projects', 'details': str(e)}), 500

@bp.route('/search', methods=['GET'])
@jwt_required()
def search_projects():
    """Search projects"""
    try:
        current_user_id = get_jwt_identity()
        user = UserModule.find_by_id(current_user_id)  # ✅ CHANGED
        
        query = request.args.get('q')
        user_id = request.args.get('user_id', type=int)
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        # ✅ NEW: Regular users can only search their own projects
        if not UserModule.is_admin(user):  # ✅ CHANGED
            user_id = current_user_id
        
        projects = ProjectModule.search_projects(query, user_id)  # ✅ CHANGED
        
        return jsonify({
            'projects': [ProjectModule.to_dict(project, include_details=True) for project in projects],  # ✅ CHANGED
            'query': query,
            'count': len(projects)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Search failed', 'details': str(e)}), 500

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_project_stats():
    """Get project statistics"""
    try:
        current_user_id = get_jwt_identity()
        user = UserModule.find_by_id(current_user_id)  # ✅ CHANGED
        
        # ✅ NEW: Users can see their own stats, admins can see all
        if UserModule.is_admin(user):  # ✅ CHANGED
            total_projects = Project.query.count()
            pending_projects = Project.query.filter_by(status='pending').count()
            in_progress_projects = Project.query.filter_by(status='in_progress').count()
            completed_projects = Project.query.filter_by(status='completed').count()
            payment_required_projects = Project.query.filter_by(status='payment_required').count()
            
            # Calculate total revenue
            total_revenue = db.session.query(db.func.sum(Project.total_price))\
                                  .filter_by(status='completed')\
                                  .scalar() or 0
        else:
            # User-specific stats
            total_projects = Project.query.filter_by(user_id=current_user_id).count()
            pending_projects = Project.query.filter_by(user_id=current_user_id, status='pending').count()
            in_progress_projects = Project.query.filter_by(user_id=current_user_id, status='in_progress').count()
            completed_projects = Project.query.filter_by(user_id=current_user_id, status='completed').count()
            payment_required_projects = Project.query.filter_by(user_id=current_user_id, status='payment_required').count()
            
            # Calculate user's total spent
            total_revenue = db.session.query(db.func.sum(Project.total_price))\
                                  .filter_by(user_id=current_user_id, status='completed')\
                                  .scalar() or 0
        
        stats = {
            'total_projects': total_projects,
            'pending_projects': pending_projects,
            'in_progress_projects': in_progress_projects,
            'completed_projects': completed_projects,
            'payment_required_projects': payment_required_projects,
            'total_spent': float(total_revenue)
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get stats', 'details': str(e)}), 500

@bp.route('/<int:project_id>/history', methods=['GET'])
@jwt_required()
def get_project_history(project_id):
    """Get project history"""
    try:
        current_user_id = get_jwt_identity()
        project = ProjectModule.find_by_id(project_id)  # ✅ CHANGED
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check permissions
        user = UserModule.find_by_id(current_user_id)  # ✅ CHANGED
        if project.user_id != current_user_id and not UserModule.is_admin(user):  # ✅ CHANGED
            return jsonify({'error': 'Access denied'}), 403
        
        # TODO: Implement project history logic
        history = [
            {
                'action': 'created',
                'timestamp': project.created_at.isoformat(),
                'user': project.user.name
            }
        ]
        
        if project.assigned_at:
            history.append({
                'action': 'assigned',
                'timestamp': project.assigned_at.isoformat(),
                'user': project.assigned_staff.user.name if project.assigned_staff else 'System'
            })
        
        if project.completed_at:
            history.append({
                'action': 'completed',
                'timestamp': project.completed_at.isoformat(),
                'user': project.assigned_staff.user.name if project.assigned_staff else 'System'
            })
        
        return jsonify({'history': history}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get project history', 'details': str(e)}), 500