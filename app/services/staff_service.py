from app.models.staff import Staff
from app.models.user import User
from app.models.project import Project
from app.utils.email_service import EmailService
from app.utils.validators import validate_email
import os
from datetime import datetime, timedelta

class StaffService:
    @staticmethod
    def get_profile(staff_id):
        """Get staff profile"""
        try:
            staff = Staff.find_by_id(staff_id)
            
            if not staff:
                return {'success': False, 'message': 'Staff profile not found'}
            
            return {
                'success': True,
                'staff': staff.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get staff profile: {str(e)}'}
    
    @staticmethod
    def update_profile(staff_id, **kwargs):
        """Update staff profile"""
        try:
            staff = Staff.find_by_id(staff_id)
            
            if not staff:
                return {'success': False, 'message': 'Staff profile not found'}
            
            # Update allowed fields
            allowed_fields = [
                'specialization', 'experience_years', 'qualification', 'bio', 
                'hourly_rate', 'skills'
            ]
            
            for field in allowed_fields:
                if field in kwargs:
                    setattr(staff, field, kwargs[field])
            
            if 'skills' in kwargs:
                staff.set_skills_list(kwargs['skills'])
            
            staff.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Staff profile updated successfully',
                'staff': staff.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Staff profile update failed: {str(e)}'}
    
    @staticmethod
    def get_assigned_projects(staff_id, page=1, per_page=10, status=None):
        """Get projects assigned to staff member"""
        try:
            staff = Staff.find_by_id(staff_id)
            
            if not staff:
                return {'success': False, 'message': 'Staff member not found'}
            
            # Build query
            query = Project.query.filter_by(assigned_staff_id=staff_id)
            
            if status:
                query = query.filter_by(status=status)
            
            # Order by most recent
            query = query.order_by(Project.created_at.desc())
            
            # Paginate
            projects = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            return {
                'success': True,
                'projects': [project.to_dict(include_details=True) for project in projects.items],
                'pagination': {
                    'page': projects.page,
                    'per_page': projects.per_page,
                    'total': projects.total,
                    'pages': projects.pages,
                    'has_next': projects.has_next,
                    'has_prev': projects.has_prev
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get assigned projects: {str(e)}'}
    
    @staticmethod
    def get_project(staff_id, project_id):
        """Get specific project assigned to staff member"""
        try:
            staff = Staff.find_by_id(staff_id)
            
            if not staff:
                return {'success': False, 'message': 'Staff member not found'}
            
            project = Project.find_by_id(project_id)
            
            if not project:
                return {'success': False, 'message': 'Project not found'}
            
            # Check if project is assigned to this staff member
            if project.assigned_staff_id != staff.id:
                return {'success': False, 'message': 'Project not assigned to this staff member'}
            
            return {
                'success': True,
                'project': project.to_dict(include_details=True)
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get project: {str(e)}'}
    
    @staticmethod
    def update_project_status(staff_id, project_id, status):
        """Update project status"""
        try:
            staff = Staff.find_by_id(staff_id)
            
            if not staff:
                return {'success': False, 'message': 'Staff member not found'}
            
            project = Project.find_by_id(project_id)
            
            if not project:
                return {'success': False, 'message': 'Project not found'}
            
            # Check if project is assigned to this staff member
            if project.assigned_staff_id != staff.id:
                return {'success': False, 'message': 'Project not assigned to this staff member'}
            
            # Staff can only update to in_progress or completed
            if status not in ['in_progress', 'completed']:
                return {'success': False, 'message': 'Invalid status for staff member'}
            
            project.update_status(status)
            
            # Update staff performance if completed
            if status == 'completed':
                staff.complete_project(project)
            
            # Notify user
            try:
                EmailService.notify_project_status_update(project, staff)
            except Exception:
                pass
            
            return {
                'success': True,
                'message': f'Project status updated to {status}',
                'project': project.to_dict(include_details=True)
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Project status update failed: {str(e)}'}
    
    @staticmethod
    def upload_result(staff_id, project_id, result_data):
        """Upload project result"""
        try:
            staff = Staff.find_by_id(staff_id)
            
            if not staff:
                return {'success': False, 'message': 'Staff member not found'}
            
            project = Project.find_by_id(project_id)
            
            if not project:
                return {'success': False, 'message': 'Project not found'}
            
            # Check if project is assigned to this staff member
            if project.assigned_staff_id != staff.id:
                return {'success': False, 'message': 'Project not assigned to this staff member'}
            
            if project.status != 'in_progress':
                return {'success': False, 'message': 'Project must be in progress to upload result'}
            
            # Validate result data
            if not result_data.get('file_path'):
                return {'success': False, 'message': 'Result file path is required'}
            
            if not result_data.get('description'):
                return {'success': False, 'message': 'Result description is required'}
            
            result_path = result_data['file_path']
            result_filename = result_data.get('result_filename')
            description = result_data['description']
            
            # TODO: Validate result file
            if not os.path.exists(result_path):
                return {'success': False, 'message': 'Result file not found'}
            
            # Complete project with result
            project.complete_project(result_path, result_filename)
            
            # Update staff performance
            staff.complete_project(project)
            
            # Notify user
            try:
                EmailService.notify_result_upload(project, staff)
            except Exception:
                pass
            
            return {
                'success': True,
                'message': 'Result uploaded successfully',
                'project': project.to_dict(include_details=True)
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Result upload failed: {str(e)}'}
    
    @staticmethod
    def get_dashboard_stats(staff_id):
        """Get staff dashboard statistics"""
        try:
            staff = Staff.find_by_id(staff_id)
            
            if not staff:
                return {'success': False, 'message': 'Staff member not found'}
            
            stats = staff.get_performance_stats()
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get dashboard stats: {str(e)}'}
    
    @staticmethod
    def get_performance_stats(staff_id):
        """Get detailed performance statistics"""
        try:
            staff = Staff.find_by_id(staff_id)
            
            if not staff:
                return {'success': False, 'message': 'Staff member not found'}
            
            projects = staff.get_assigned_projects()
            
            performance_data = {
                'total_projects': len(projects),
                'completed_projects': len(staff.get_completed_projects()),
                'active_projects': len(staff.get_active_projects()),
                'rating': staff.rating,
                'experience_years': staff.experience_years,
                'specialization': staff.specialization,
                'skills': staff.get_skills_list(),
                'recent_projects': [
                    {
                        'id': p.id,
                        'title': p.title,
                        'status': p.status,
                        'created_at': p.created_at.isoformat(),
                        'completed_at': p.completed_at.isoformat() if p.completed_at else None
                    }
                    for p in projects[:5]
            }
            
            return {
                'success': True,
                'performance': performance_data
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Performance stats failed: {str(e)}'}
    
    @staticmethod
    def get_available_projects(staff_id):
        """Get available projects for staff member"""
        try:
            staff = Staff.find_by_id(staff_id)
            
            if not staff:
                return {'success': False, 'message': 'Staff member not found'}
            
            if not staff.can_take_project():
                return {'success': False, 'message': 'Staff member cannot take more projects'}
            
            # Get unassigned projects
            projects = Project.get_unassigned_projects()
            
            # Filter by specialization if staff has one
            if staff.specialization:
                projects = [
                    p for p in projects 
                    if p.research_field == staff.specialization
                ]
            
            return {
                'success': True,
                'projects': [project.to_dict(include_details=True) for project in projects],
                'available_slots': 5 - len(staff.get_active_projects())
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get available projects: {str(e)}'}
    
    @staticmethod
    def request_project(staff_id, project_id):
        """Request project assignment"""
        try:
            staff = Staff.find_by_id(staff_id)
            
            if not staff:
                return {'success': False, 'message': 'Staff member not found'}
            
            project = Project.find_by_id(project_id)
            
            if not project:
                return {'success': False, 'message': 'Project not found'}
            
            if project.status != 'pending':
                return {'success': False, 'message': 'Project is not available for assignment'}
            
            if not staff.can_take_project():
                return {'success': False, 'message': 'Staff member cannot take more projects'}
            
            # Auto-assign project to staff
            project.assign_to_staff(staff.id)
            
            # Notify staff member
            try:
                EmailService.notify_project_assignment(project, staff)
            except Exception:
                pass
            
            return {
                'success': True,
                'message': 'Project assigned successfully',
                'project': project.to_dict(include_details=True)
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Project request failed: {str(e)}'}
    
    @staticmethod
    def get_workload(staff_id):
        """Get current workload"""
        try:
            staff = Staff.find_by_id(staff_id)
            
            if not staff:
                return {'success': False, 'message': 'Staff member not found'}
            
            active_projects = staff.get_active_projects()
            
            workload_data = {
                'active_projects': len(active_projects),
                'max_projects': 5,
                'available_slots': 5 - len(active_projects),
                'can_take_more': staff.can_take_project(),
                'projects': [
                    {
                        'id': p.id,
                        'title': p.title,
                        'status': p.status,
                        'created_at': p.created_at.isoformat(),
                        'deadline': p.deadline.isoformat() if p.deadline else None
                    }
                    for p in active_projects
                ]
            }
            
            return {
                'success': True,
                'workload': workload_data
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Workload check failed: {str(e)}'}
    
    @staticmethod
    def set_availability(staff_id, available):
        """Set staff availability"""
        try:
            staff = Staff.find_by_id(staff_id)
            
            if not staff:
                return {'success': False, 'message': 'Staff member not found'}
            
            staff.set_availability(available)
            
            status = 'available' if available else 'unavailable'
            
            return {
                'success': True,
                'message': f'Staff availability set to {status}',
                'staff': staff.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Availability update failed: {str(e)}'}
    
    @staticmethod
    def update_rating(staff_id):
        """Update staff rating"""
        try:
            staff = Staff.find_by_id(staff_id)
            
            if not staff:
                return {'success': False, 'message': 'Staff member not found'}
            
            staff.update_rating()
            
            return {
                'success': True,
                'message': 'Rating updated successfully',
                'staff': staff.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Rating update failed: {str(e)}'}
    
    @staticmethod
    def get_skills(staff_id):
        """Get staff skills"""
        try:
            staff = Staff.find_by_id(staff_id)
            
            if not staff:
                return {'success': False, 'message': 'Staff member not found'}
            
            return {
                'success': True,
                'skills': staff.get_skills_list()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get skills: {str(e)}'}
    
    @staticmethod
    def set_skills(staff_id, skills_list):
        """Update staff skills"""
        try:
            staff = Staff.find_by_id(staff_id)
            
            if not staff:
                return {'success': False, 'message': 'Staff member not found'}
            
            staff.set_skills_list(skills_list)
            
            return {
                'success': True,
                'message': 'Skills updated successfully',
                'skills': staff.get_skills_list()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Skills update failed: {str(e)}'}
    
    @staticmethod
    def get_all_staff():
        """Get all staff members"""
        try:
            staff_members = Staff.get_all_active()
            
            return {
                'success': True,
                'staff': [staff.to_dict() for staff in staff_members]
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get staff members: {str(e)}'}
    
    @staticmethod
    def get_staff_by_specialization(specialization):
        """Get staff by specialization"""
        try:
            staff_members = Staff.get_staff_by_specialization(specialization)
            
            return {
                'success': True,
                'staff': [staff.to_dict() for staff in staff_members]
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get staff by specialization: {str(e)}'}
    
    @staticmethod
    def get_top_rated_staff(limit=10):
        """Get top rated staff members"""
        try:
            staff_members = Staff.get_top_rated_staff(limit)
            
            return {
                'success': True,
                'staff': [staff.to_dict() for staff in staff_members]
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get top rated staff: {str(e)}'}
    
    @staticmethod
    def create_staff_profile(user_id, **kwargs):
        """Create staff profile for user"""
        try:
            user = User.find_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Check if user already has staff profile
            existing_staff = Staff.find_by_user_id(user_id)
            if existing_staff:
                return {'success': False, 'message': 'Staff profile already exists for this user'}
            
            # Create staff profile
            staff = Staff.create_staff_profile(user_id, **kwargs)
            
            return {
                'success': True,
                'message': 'Staff profile created successfully',
                'staff': staff.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Staff profile creation failed: {str(e)}'}
    
    @staticmethod
    def delete_staff(staff_id):
        """Delete staff profile"""
        try:
            staff = Staff.find_by_id(staff_id)
            
            if not staff:
                return {'success': False, 'message': 'Staff member not found'}
            
            user = staff.user
            user.delete()
            staff.delete()
            
            return {
                'success': True,
                'message': 'Staff member deleted successfully'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Staff deletion failed: {str(e)}'
    
    @staticmethod
    def get_staff_performance_stats():
        """Get overall staff performance statistics"""
        try:
            all_staff = Staff.get_all()
            
            total_staff = len(all_staff)
            active_staff = len([s for s in all_staff if s.availability])
            total_projects = sum([s.total_projects for s in all_staff])
            completed_projects = sum([s.completed_projects for s in all_staff])
            
            avg_rating = sum([s.rating for s in all_staff]) / max(total_staff, 1) if total_staff > 0 else 0
            
            stats = {
                'total_staff': total_staff,
                'active_staff': active_staff,
                'total_projects': total_projects,
                'completed_projects': completed_projects,
                'average_rating': round(avg_rating, 2),
                'productivity': (completed_projects / max(total_projects, 1)) * 100 if total_projects > 0 else 0
            }
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Staff performance stats failed: {str(e)}'}


# Create instance for direct use
staff_service = StaffService()
