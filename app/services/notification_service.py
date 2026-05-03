from app import db
from app.models.user import User
from app.models.project import Project
from app.models.staff import Staff
from datetime import datetime, timedelta
import json

class NotificationService:
    NOTIFICATION_TYPES = {
        'project_assigned': 'Project Assigned',
        'project_completed': 'Project Completed',
        'payment_received': 'Payment Received',
        'system_update': 'System Update',
        'message': 'Message',
        'reminder': 'Reminder',
        'deadline_approaching': 'Deadline Approaching',
        'project_status_update': 'Project Status Update',
        'result_uploaded': 'Result Uploaded',
        'payment_required': 'Payment Required'
    }
    
    @staticmethod
    def create_notification(user_id, notification_type, title, message, data=None):
        """Create a new notification"""
        try:
            # TODO: Implement notification model and database table
            # For now, we'll return a mock notification
            
            notification = {
                'id': None,  # Would be database ID
                'user_id': user_id,
                'type': notification_type,
                'title': title,
                'message': message,
                'data': data or {},
                'read': False,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            return {
                'success': True,
                'notification': notification
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Notification creation failed: {str(e)}'}
    
    @staticmethod
    def notify_project_assigned(project, staff):
        """Notify staff about project assignment"""
        try:
            title = f"New Project Assigned: {project.title}"
            message = f"You have been assigned to work on '{project.title}' in {project.research_field}."
            
            data = {
                'project_id': project.id,
                'project_title': project.title,
                'client_name': project.user.name,
                'research_field': project.research_field
            }
            
            return NotificationService.create_notification(
                staff.user_id,
                'project_assigned',
                title,
                message,
                data
            )
            
        except Exception as e:
            return {'success': False, 'message': f'Assignment notification failed: {str(e)}'}
    
    @staticmethod
    def notify_project_completed(project, staff):
        """Notify user about project completion"""
        try:
            title = f"Project Completed: {project.title}"
            message = f"Your project '{project.title}' has been completed by {staff.user.name}."
            
            data = {
                'project_id': project.id,
                'project_title': project.title,
                'staff_name': staff.user.name,
                'completion_date': project.completed_at
            }
            
            return NotificationService.create_notification(
                project.user_id,
                'project_completed',
                title,
                message,
                data
            )
            
        except Exception as e:
            return {'success': False, 'message': f'Completion notification failed: {str(e)}'}
    
    @staticmethod
    def notify_payment_required(project):
        """Notify user about payment requirement"""
        try:
            title = f"Payment Required: {project.title}"
            message = f"Your project '{project.title}' is complete. Please proceed with payment to download results."
            
            data = {
                'project_id': project.id,
                'project_title': project.title,
                'amount': project.price,
                'currency': project.currency
            }
            
            return NotificationService.create_notification(
                project.user_id,
                'payment_required',
                title,
                message,
                data
            )
            
        except Exception as e:
            return {'success': False, 'message': f'Payment notification failed: {str(e)}'}
    
    @staticmethod
    def notify_payment_received(project, payment):
        """Notify user about payment receipt"""
        try:
            title = f"Payment Received: {project.title}"
            message = f"Payment of ${payment.amount} {payment.currency} has been received for '{project.title}'."
            
            data = {
                'project_id': project.id,
                'project_title': project.title,
                'amount': payment.amount,
                'currency': payment.currency,
                'transaction_id': payment.transaction_id
            }
            
            return NotificationService.create_notification(
                project.user_id,
                'payment_received',
                title,
                message,
                data
            )
            
        except Exception as e:
            return {'success': False, 'message': f'Payment receipt notification failed: {str(e)}'}
    
    @staticmethod
    def notify_result_uploaded(project, staff):
        """Notify user about result upload"""
        try:
            title = f"Result Uploaded: {project.title}"
            message = f"Result has been uploaded for '{project.title}' by {staff.user.name}."
            
            data = {
                'project_id': project.id,
                'project_title': project.title,
                'staff_name': staff.user.name,
                'upload_date': project.updated_at
            }
            
            return NotificationService.create_notification(
                project.user_id,
                'result_uploaded',
                title,
                message,
                data
            )
            
        except Exception as e:
            return {'success': False, 'message': f'Result upload notification failed: {str(e)}'}
    
    @staticmethod
    def notify_project_status_update(project, staff, old_status, new_status):
        """Notify user about project status update"""
        try:
            title = f"Project Status Update: {project.title}"
            message = f"Project '{project.title}' status changed from {old_status} to {new_status}."
            
            data = {
                'project_id': project.id,
                'project_title': project.title,
                'old_status': old_status,
                'new_status': new_status,
                'staff_name': staff.user.name,
                'update_date': project.updated_at
            }
            
            return NotificationService.create_notification(
                project.user_id,
                'project_status_update',
                title,
                message,
                data
            )
            
        except Exception as e:
            return {'success': False, 'message': f'Status update notification failed: {str(e)}'}
    
    @staticmethod
    def notify_deadline_approaching(project):
        """Notify staff about approaching deadline"""
        try:
            if not project.assigned_staff_id:
                return {'success': False, 'message': 'No staff assigned to project'}
            
            days_until_deadline = project.get_days_until_deadline()
            
            if days_until_deadline is None or days_until_deadline > 3:
                return {'success': True, 'message': 'No deadline notification needed'}
            
            title = f"Deadline Approaching: {project.title}"
            message = f"Project '{project.title}' deadline is approaching in {days_until_deadline} days."
            
            data = {
                'project_id': project.id,
                'project_title': project.title,
                'deadline': project.deadline,
                'days_until_deadline': days_until_deadline
            }
            
            return NotificationService.create_notification(
                project.assigned_staff_id,
                'deadline_approaching',
                title,
                message,
                data
            )
            
        except Exception as e:
            return {'success': False, 'message': f'Deadline notification failed: {str(e)}'}
    
    @staticmethod
    def notify_new_user(user):
        """Notify admin about new user registration"""
        try:
            title = f"New User Registration: {user.name}"
            message = f"New user {user.name} ({user.email}) has registered as {user.role}."
            
            data = {
                'user_id': user.id,
                'user_name': user.name,
                'user_email': user.email,
                'user_role': user.role,
                'registration_date': user.created_at
            }
            
            # TODO: Get admin user ID
            admin_id = 1  # This should be dynamic
            
            return NotificationService.create_notification(
                admin_id,
                'system_update',
                title,
                message,
                data
            )
            
        except Exception as e:
            return {'success': False, 'message': f'New user notification failed: {str(e)}'}
    
    @staticmethod
    def notify_staff_performance_update(staff, old_rating, new_rating):
        """Notify staff about performance update"""
        try:
            title = "Performance Rating Updated"
            message = f"Your performance rating has been updated from {old_rating} to {new_rating}."
            
            data = {
                'staff_id': staff.id,
                'old_rating': old_rating,
                'new_rating': new_rating,
                'completed_projects': staff.completed_projects,
                'total_projects': staff.total_projects
            }
            
            return NotificationService.create_notification(
                staff.user_id,
                'system_update',
                title,
                message,
                data
            )
            
        except Exception as e:
            return {'success': False, 'message': f'Performance notification failed: {str(e)}'}
    
    @staticmethod
    def notify_system_maintenance(message, target_users='all'):
        """Notify users about system maintenance"""
        try:
            title = "System Maintenance"
            
            data = {
                'maintenance_type': 'scheduled',
                'message': message,
                'scheduled_date': datetime.utcnow()
            }
            
            notifications = []
            
            if target_users == 'all':
                # Send to all users
                users = User.query.all()
                for user in users:
                    notification = NotificationService.create_notification(
                        user.id,
                        'system_update',
                        title,
                        message,
                        data
                    )
                    notifications.append(notification)
            else:
                # Send to specific users
                for user_id in target_users:
                    notification = NotificationService.create_notification(
                        user_id,
                        'system_update',
                        title,
                        message,
                        data
                    )
                    notifications.append(notification)
            
            return {
                'success': True,
                'message': f'Sent {len(notifications)} maintenance notifications',
                'notifications': notifications
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Maintenance notification failed: {str(e)}'}
    
    @staticmethod
    def get_user_notifications(user_id, unread_only=False, limit=50):
        """Get notifications for a user"""
        try:
            # TODO: Implement database query for notifications
            # For now, return mock data
            
            notifications = []
            
            return {
                'success': True,
                'notifications': notifications,
                'unread_count': 0
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get notifications: {str(e)}'}
    
    @staticmethod
    def mark_notification_as_read(notification_id, user_id):
        """Mark notification as read"""
        try:
            # TODO: Implement database update
            return {
                'success': True,
                'message': 'Notification marked as read'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to mark notification as read: {str(e)}'}
    
    @staticmethod
    def mark_all_notifications_as_read(user_id):
        """Mark all notifications as read for a user"""
        try:
            # TODO: Implement database update
            return {
                'success': True,
                'message': 'All notifications marked as read'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to mark all notifications as read: {str(e)}'}
    
    @staticmethod
    def delete_notification(notification_id, user_id):
        """Delete notification"""
        try:
            # TODO: Implement database deletion
            return {
                'success': True,
                'message': 'Notification deleted'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to delete notification: {str(e)}'}
    
    @staticmethod
    def get_notification_stats(user_id):
        """Get notification statistics for a user"""
        try:
            # TODO: Implement database query
            stats = {
                'total_notifications': 0,
                'unread_notifications': 0,
                'notifications_by_type': {},
                'recent_notifications': []
            }
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get notification stats: {str(e)}'}
    
    @staticmethod
    def cleanup_old_notifications(days=30):
        """Clean up old notifications"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # TODO: Implement database cleanup
            deleted_count = 0
            
            return {
                'success': True,
                'message': f'Cleaned up {deleted_count} old notifications',
                'deleted_count': deleted_count
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Notification cleanup failed: {str(e)}'}
    
    @staticmethod
    def send_bulk_notification(user_ids, notification_type, title, message, data=None):
        """Send bulk notification to multiple users"""
        try:
            notifications = []
            
            for user_id in user_ids:
                notification = NotificationService.create_notification(
                    user_id,
                    notification_type,
                    title,
                    message,
                    data
                )
                notifications.append(notification)
            
            return {
                'success': True,
                'message': f'Sent {len(notifications)} notifications',
                'notifications': notifications
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Bulk notification failed: {str(e)}'}
    
    @staticmethod
    def get_notification_types():
        """Get available notification types"""
        return {
            'success': True,
            'types': NotificationService.NOTIFICATION_TYPES
        }


# Create instance for direct use
notification_service = NotificationService()
