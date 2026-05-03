from app.models.user import User
from app.models.project import Project
from app.models.payment import Payment
from app.utils.validators import validate_email
from app.utils.email_service import EmailService

class UserService:
    @staticmethod
    def get_profile(user_id):
        """Get user profile"""
        try:
            user = User.find_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            return {
                'success': True,
                'user': user.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get profile: {str(e)}'}
    
    @staticmethod
    def update_profile(user_id, **kwargs):
        """Update user profile"""
        try:
            user = User.find_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Update allowed fields
            allowed_fields = ['name', 'phone', 'avatar']
            
            for field in allowed_fields:
                if field in kwargs:
                    setattr(user, field, kwargs[field])
            
            user.updated_at = db.func.now()
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Profile updated successfully',
                'user': user.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Profile update failed: {str(e)}'}
    
    @staticmethod
    def get_projects(user_id, page=1, per_page=10, status=None, search=None):
        """Get user's projects"""
        try:
            user = User.find_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Build query
            query = Project.query.filter_by(user_id=user_id)
            
            if status:
                query = query.filter_by(status=status)
            
            if search:
                query = query.filter(Project.title.contains(search))
            
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
            return {'success': False, 'message': f'Failed to get projects: {str(e)}'}
    
    @staticmethod
    def get_project(user_id, project_id):
        """Get specific project"""
        try:
            user = User.find_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            project = Project.find_by_id(project_id)
            
            if not project:
                return {'success': False, 'message': 'Project not found'}
            
            # Check if user owns the project
            if project.user_id != user_id:
                return {'success': False, 'message': 'Access denied'}
            
            return {
                'success': True,
                'project': project.to_dict(include_details=True)
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get project: {str(e)}'}
    
    @staticmethod
    def update_project(user_id, project_id, **kwargs):
        """Update project"""
        try:
            user = User.find_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            project = Project.find_by_id(project_id)
            
            if not project:
                return {'success': False, 'message': 'Project not found'}
            
            # Check if user owns the project
            if project.user_id != user_id:
                return {'success': False, 'message': 'Access denied'}
            
            # Check if project can be edited (within 24 hours)
            if not project.can_be_edited():
                return {'success': False, 'message': 'Project can only be edited within 24 hours of creation'}
            
            # Update allowed fields
            allowed_fields = ['title', 'research_field', 'description', 'priority']
            
            for field in allowed_fields:
                if field in kwargs:
                    setattr(project, field, kwargs[field])
            
            project.updated_at = db.func.now()
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Project updated successfully',
                'project': project.to_dict(include_details=True)
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Project update failed: {str(e)}'}
    
    @staticmethod
    def delete_project(user_id, project_id):
        """Delete project"""
        try:
            user = User.find_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            project = Project.find_by_id(project_id)
            
            if not project:
                return {'success': False, 'message': 'Project not found'}
            
            # Check if user owns the project
            if project.user_id != user_id:
                return {'success': False, 'message': 'Access denied'}
            
            # Check if project can be deleted
            if project.status == 'in_progress':
                return {'success': False, 'message': 'Cannot delete project that is in progress'}
            
            if project.status == 'completed':
                return {'success': False, 'message': 'Cannot delete completed project'}
            
            # Delete associated files
            import os
            if project.file_path and os.path.exists(project.file_path):
                os.remove(project.file_path)
            
            if project.result_path and os.path.exists(project.result_path):
                os.remove(project.result_path)
            
            project.delete()
            
            return {
                'success': True,
                'message': 'Project deleted successfully'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Project deletion failed: {str(e)}'}
    
    @staticmethod
    def describe_project(user_id, project_id, description_data):
        """Add or update project description"""
        try:
            user = User.find_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            project = Project.find_by_id(project_id)
            
            if not project:
                return {'success': False, 'message': 'Project not found'}
            
            # Check if user owns the project
            if project.user_id != user_id:
                return {'success': False, 'message': 'Access denied'}
            
            # Validate required fields
            required_fields = ['objectives', 'methodology', 'expected_outcomes', 'timeline']
            for field in required_fields:
                if not description_data.get(field) or not description_data[field].strip():
                    return {'success': False, 'message': f'{field} is required'}
            
            project.set_description_dict(description_data)
            
            return {
                'success': True,
                'message': 'Project description saved successfully',
                'project': project.to_dict(include_details=True)
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Description save failed: {str(e)}'}
    
    @staticmethod
    def get_project_preview(user_id, project_id):
        """Get project preview"""
        try:
            user = User.find_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            project = Project.find_by_id(project_id)
            
            if not project:
                return {'success': False, 'message': 'Project not found'}
            
            # Check if user owns the project
            if project.user_id != user_id:
                return {'success': False, 'message': 'Access denied'}
            
            if not project.file_path:
                return {'success': False, 'message': 'Project file not found'}
            
            # TODO: Implement PDF preview logic
            return {
                'success': True,
                'preview_url': f'/api/files/preview/{project_id}',
                'message': 'Preview generated successfully'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Preview generation failed: {str(e)}'}
    
    @staticmethod
    def get_download_link(user_id, project_id):
        """Get download link for project result"""
        try:
            user = User.find_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            project = Project.find_by_id(project_id)
            
            if not project:
                return {'success': False, 'message': 'Project not found'}
            
            # Check if user owns the project
            if project.user_id != user_id:
                return {'success': False, 'message': 'Access denied'}
            
            if project.status != 'completed':
                return {'success': False, 'message': 'Project must be completed to download result'}
            
            if not project.result_path:
                return {'success': False, 'message': 'Result file not found'}
            
            return {
                'success': True,
                'download_url': f'/api/files/download/{project_id}',
                'filename': project.result_filename or 'result.pdf',
                'message': 'Download ready'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Download preparation failed: {str(e)}'}
    
    @staticmethod
    def get_notifications(user_id):
        """Get user notifications"""
        try:
            user = User.find_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # TODO: Implement notifications logic
            notifications = []
            
            return {
                'success': True,
                'notifications': notifications,
                'unread_count': 0
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get notifications: {str(e)}'}
    
    @staticmethod
    def get_settings(user_id):
        """Get user settings"""
        try:
            user = User.find_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # TODO: Implement settings logic
            settings = {
                'email_notifications': True,
                'push_notifications': False,
                'theme': 'light',
                'language': 'en',
                'timezone': 'UTC'
            }
            
            return {
                'success': True,
                'settings': settings
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get settings: {str(e)}'}
    
    @staticmethod
    def update_settings(user_id, settings_data):
        """Update user settings"""
        try:
            user = User.find_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # TODO: Implement settings update logic
            # This would update user preferences in database
            
            return {
                'success': True,
                'message': 'Settings updated successfully'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Settings update failed: {str(e)}'}
    
    @staticmethod
    def upload_avatar(user_id, file):
        """Upload user avatar"""
        try:
            user = User.find_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            if not file:
                return {'success': False, 'message': 'No file provided'}
            
            # TODO: Implement file upload logic
            # This would save the file and update user.avatar
            
            avatar_url = f'/uploads/avatars/{user_id}_{file.filename}'
            user.avatar = avatar_url
            user.update_profile()
            
            return {
                'success': True,
                'message': 'Avatar uploaded successfully',
                'avatar_url': avatar_url
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Avatar upload failed: {str(e)}'}
    
    @staticmethod
    def delete_account(user_id):
        """Delete user account"""
        try:
            user = User.find_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Check if user has active projects
            active_projects = [
                p for p in user.projects 
                if p.status in ['pending', 'in_progress']
            ]
            
            if active_projects:
                return {'success': False, 'message': 'Cannot delete account with active projects'}
            
            # Delete associated files
            for project in user.projects:
                if project.file_path and os.path.exists(project.file_path):
                    os.remove(project.file_path)
                if project.result_path and os.path.exists(project.result_path):
                    os.remove(project.result_path)
            
            # Delete user
            user.delete()
            
            return {
                'success': True,
                'message': 'Account deleted successfully'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Account deletion failed: {str(e)}'}
    
    @staticmethod
    def get_stats(user_id):
        """Get user statistics"""
        try:
            user = User.find_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            projects = Project.find_by_user_id(user_id)
            
            stats = {
                'total_projects': len(projects),
                'pending_projects': len([p for p in projects if p.status == 'pending']),
                'in_progress_projects': len([p for p in projects if p.status == 'in_progress']),
                'completed_projects': len([p for p in projects if p.status == 'completed']),
                'payment_required_projects': len([p for p in projects if p.status == 'payment_required']),
                'total_spent': sum([p.price for p in projects if p.status == 'completed'])
            }
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Stats calculation failed: {str(e)}'}
    
    @staticmethod
    def deactivate_user(user_id):
        """Deactivate user account"""
        try:
            user = User.find_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            user.deactivate()
            
            return {
                'success': True,
                'message': 'Account deactivated successfully'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Account deactivation failed: {str(e)}'}
    
    @staticmethod
    def activate_user(user_id):
        """Activate user account"""
        try:
            user = User.find_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            user.activate()
            
            return {
                'success': True,
                'message': 'Account activated successfully'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Account activation failed: {str(e)}'
