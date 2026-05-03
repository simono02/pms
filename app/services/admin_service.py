from app.models.user import User
from app.models.staff import Staff
from app.models.project import Project
from app.models.payment import Payment
from app.utils.email_service import EmailService
import os
from datetime import datetime, timedelta

class AdminService:
    @staticmethod
    def get_dashboard_stats():
        """Get admin dashboard statistics"""
        try:
            # User statistics
            total_users = User.query.count()
            total_staff = Staff.query.count()
            active_users = User.query.filter_by(status='active').count()
            
            # Project statistics
            total_projects = Project.query.count()
            pending_projects = Project.query.filter_by(status='pending').count()
            in_progress_projects = Project.query.filter_by(status='in_progress').count()
            completed_projects = Project.query.filter_by(status='completed').count()
            payment_required_projects = Project.query.filter_by(status='payment_required').count()
            
            # Payment statistics
            total_revenue = db.session.query(db.func.sum(Payment.amount))\
                                  .filter_by(status='completed')\
                                  .scalar() or 0
            
            stats = {
                'users': {
                    'total': total_users,
                    'staff': total_staff,
                    'active': active_users
                },
                'projects': {
                    'total': total_projects,
                    'pending': pending_projects,
                    'in_progress': in_progress_projects,
                    'completed': completed_projects,
                    'payment_required': payment_required_projects
                },
                'revenue': float(total_revenue)
            }
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Dashboard stats failed: {str(e)}'}
    
    @staticmethod
    def get_clients(page=1, per_page=10, status=None, search=None):
        """Get all clients (users)"""
        try:
            # Build query
            query = User.query.filter_by(role='user')
            
            if status:
                query = query.filter_by(status=status)
            
            if search:
                query = query.filter(
                    User.name.contains(search) | User.email.contains(search)
                )
            
            # Order by most recent
            query = query.order_by(User.created_at.desc())
            
            # Paginate
            users = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            # Add project count for each user
            clients = []
            for user in users.items:
                client_data = user.to_dict()
                client_data['project_count'] = len(user.projects)
                clients.append(client_data)
            
            return {
                'success': True,
                'clients': clients,
                'pagination': {
                    'page': users.page,
                    'per_page': users.per_page,
                    'total': users.total,
                    'pages': users.pages,
                    'has_next': users.has_next,
                    'has_prev': users.has_prev
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get clients: {str(e)}'}
    
    @staticmethod
    def get_client(client_id):
        """Get specific client"""
        try:
            user = User.find_by_id(client_id)
            
            if not user or user.role != 'user':
                return {'success': False, 'message': 'Client not found'}
            
            client_data = user.to_dict()
            client_data['projects'] = [
                project.to_dict(include_details=True) 
                for project in user.projects
            ]
            
            return {
                'success': True,
                'client': client_data
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get client: {str(e)}'}
    
    @staticmethod
    def update_client_status(client_id, status):
        """Update client status"""
        try:
            user = User.find_by_id(client_id)
            
            if not user or user.role != 'user':
                return {'success': False, 'message': 'Client not found or not a client'}
            
            valid_statuses = ['active', 'inactive']
            if status not in valid_statuses:
                return {'success': False, 'message': 'Invalid status'}
            
            if status == 'active':
                user.activate()
            else:
                user.deactivate()
            
            return {
                'success': True,
                'message': f'Client {status} successfully',
                'user': user.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Client status update failed: {str(e)}'}
    
    @staticmethod
    def delete_client(client_id):
        """Delete client account"""
        try:
            user = User.find_by_id(client_id)
            
            if not user or user.role != 'user':
                return {'success': False, 'message': 'Client not found or not a client'}
            
            # Check if client has active projects
            active_projects = [
                p for p in user.projects 
                if p.status in ['pending', 'in_progress']
            ]
            
            if active_projects:
                return {'success': False, 'message': 'Cannot delete client with active projects'}
            
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
                'message': 'Client deleted successfully'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Client deletion failed: {str(e)}'}
    
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
    def get_staff_member(staff_id):
        """Get specific staff member"""
        try:
            staff = Staff.find_by_id(staff_id)
            
            if not staff:
                return {'success': False, 'message': 'Staff member not found'}
            
            return {
                'success': True,
                'staff': staff.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get staff member: {str(e)}}
    
    @staticmethod
    def add_staff(name, email, password, **kwargs):
        """Add new staff member"""
        try:
            # Validate input
            if not name or len(name.strip()) < 2:
                return {'success': False, 'message': 'Name must be at least 2 characters long'}
            
            if not validate_email(email):
                return {'success': False, 'message': 'Invalid email format'}
            
            # Check if user already exists
            if User.find_by_email(email):
                return {'success': False, 'message': 'User with this email already exists'}
            
            # Create user with staff role
            user = User.create_user(name, email, password, 'staff')
            
            # Create staff profile
            staff_data = {
                'specialization': kwargs.get('specialization'),
                'experience_years': kwargs.get('experience_years', 0),
                'qualification': kwargs.get('qualification'),
                'bio': kwargs.get('bio'),
                'hourly_rate': kwargs.get('hourly_rate'),
                'skills': kwargs.get('skills', [])
            }
            
            staff = Staff.create_staff_profile(user.id, **staff_data)
            
            return {
                'success': True,
                'message': 'Staff member added successfully',
                'user': user.to_dict(),
                'staff': staff.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Staff addition failed: {str(e)}'}
    
    @staticmethod
    def update_staff(staff_id, **kwargs):
        """Update staff member"""
        try:
            staff = Staff.find_by_id(staff_id)
            
            if not staff:
                return {'success': False, 'message': 'Staff member not found'}
            
            # Update user info
            if 'name' in kwargs:
                staff.user.name = kwargs['name']
            
            # Update staff profile
            if 'specialization' in kwargs:
                staff.specialization = kwargs['specialization']
            
            if 'experience_years' in kwargs:
                staff.experience_years = int(kwargs['experience_years'])
            
            if 'qualification' in kwargs:
                staff.qualification = kwargs['qualification']
            
            if 'bio' in kwargs:
                staff.bio = kwargs['bio']
            
            if 'hourly_rate' in kwargs:
                staff.hourly_rate = float(kwargs['hourly_rate'])
            
            if 'skills' in kwargs:
                staff.set_skills_list(kwargs['skills'])
            
            staff.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Staff member updated successfully',
                'staff': staff.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Staff update failed: {str(e)}'}
    
    @staticmethod
    def update_staff_status(staff_id, status):
        """Update staff availability status"""
        try:
            staff = Staff.find_by_id(staff_id)
            
            if not staff:
                return {'success': False, 'message': 'Staff member not found'}
            
            availability = status == 'active'
            staff.set_availability(availability)
            
            status_text = 'active' if availability else 'inactive'
            
            return {
                'success': True,
                'message': f'Staff {status_text} successfully',
                'staff': staff.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Staff status update failed: {str(e)}}
    
    @staticmethod
    def delete_staff(staff_id):
        """Delete staff member"""
        try:
            staff = Staff.find_by_id(staff_id)
            
            if not staff:
                return {'success': False, 'message': 'Staff member not found'}
            
            # Check if staff has active projects
            active_projects = staff.get_active_projects()
            
            if active_projects:
                return {'success': False, 'message': 'Cannot delete staff member with active projects'}
            
            # Delete staff profile and user
            user = staff.user
            staff.delete()
            user.delete()
            
            return {
                'success': True,
                'message': 'Staff member deleted successfully'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Staff deletion failed: {str(e)}'}
    
    @staticmethod
    def get_all_clients():
        """Get all clients with project counts"""
        try:
            users = User.query.filter_by(role='user').all()
            
            clients = []
            for user in users:
                client_data = user.to_dict()
                client_data['project_count'] = len(user.projects)
                clients.append(client_data)
            
            return {
                'success': True,
                'clients': clients
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get clients: {str(e)}'}
    
    @staticmethod
    def get_client_projects(client_id):
        """Get all projects for a specific client"""
        try:
            user = User.find_by_id(client_id)
            
            if not user or user.role != 'user':
                return {'success': False, 'message': 'Client not found or not a client'}
            
            projects = Project.find_by_user_id(client_id)
            
            return {
                'success': True,
                'projects': [project.to_dict(include_details=True) for project in projects]
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get client projects: {str(e)}}
    
    @staticmethod
    def get_payment_stats():
        """Get payment statistics"""
        try:
            stats = Payment.get_payment_stats()
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Payment stats failed: {str(e)}}
    
    @staticmethod
    def get_payment_history():
        """Get payment history"""
        try:
            current_user_id = get_jwt_identity()
            user = User.find_by_id(current_user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            payments = Payment.find_by_user_id(current_user_id)
            
            return {
                'success': True,
                'payments': [payment.to_dict() for payment in payments]
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Payment history failed: {str(e)}}
    
    @staticmethod
    def get_payment(payment_id):
        """Get specific payment details"""
        try:
            payment = Payment.find_by_id(payment_id)
            
            if not payment:
                return {'success': False, 'message': 'Payment not found'}
            
            return {
                'success': True,
                'payment': payment.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Payment details failed: {str(e)}}
    
    @staticmethod
    def refund_payment(payment_id, reason):
        """Refund payment"""
        try:
            payment = Payment.find_by_id(payment_id)
            
            if not payment:
                return {'success': False, 'message': 'Payment not found'}
            
            if not payment.can_be_refunded():
                return {'success': False, 'message': 'Payment cannot be refunded'}
            
            payment.refund_payment(reason)
            
            return {
                'success': True,
                'payment': payment.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Refund failed: {str(e)}'}
    
    @staticmethod
def admin_service():
    """Create admin service instance"""
    return AdminService()

# Create instance for direct use
admin_service = AdminService()
