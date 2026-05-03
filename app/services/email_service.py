from flask_mail import Message
from flask import current_app
from app import mail
import os

class EmailService:
    @staticmethod
    def send_welcome_email(user):
        """Send welcome email to new user"""
        try:
            subject = "Welcome to Project Management System"
            body = f"""
            Dear {user.name},
            
            Welcome to our Project Management System! We're excited to have you on board.
            
            Your account has been successfully created with the email: {user.email}
            
            You can now start:
            - Creating and managing your projects
            - Uploading research papers
            - Tracking project progress
            - Collaborating with our expert team
            
            If you have any questions, please don't hesitate to contact our support team.
            
            Best regards,
            The Project Management Team
            """
            
            msg = Message(
                subject=subject,
                recipients=[user.email],
                body=body,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Failed to send welcome email: {e}")
            return False
    
    @staticmethod
    def send_password_reset_email(user, reset_token):
        """Send password reset email"""
        try:
            subject = "Password Reset Request"
            reset_link = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
            
            body = f"""
            Dear {user.name},
            
            You requested to reset your password. Click the link below to reset your password:
            
            {reset_link}
            
            This link will expire in 24 hours.
            
            If you didn't request this password reset, please ignore this email.
            
            Best regards,
            The Project Management Team
            """
            
            msg = Message(
                subject=subject,
                recipients=[user.email],
                body=body,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Failed to send password reset email: {e}")
            return False
    
    @staticmethod
    def send_password_reset_confirmation(user):
        """Send password reset confirmation"""
        try:
            subject = "Password Reset Successful"
            
            body = f"""
            Dear {user.name},
            
            Your password has been successfully reset.
            
            If you didn't make this change, please contact our support team immediately.
            
            Best regards,
            The Project Management Team
            """
            
            msg = Message(
                subject=subject,
                recipients=[user.email],
                body=body,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Failed to send password reset confirmation: {e}")
            return False
    
    @staticmethod
    def send_password_change_notification(user):
        """Send password change notification"""
        try:
            subject = "Password Changed Successfully"
            
            body = f"""
            Dear {user.name},
            
            Your password has been successfully changed.
            
            If you didn't make this change, please contact our support team immediately.
            
            Best regards,
            The Project Management Team
            """
            
            msg = Message(
                subject=subject,
                recipients=[user.email],
                body=body,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Failed to send password change notification: {e}")
            return False
    
    @staticmethod
    def notify_new_project(project):
        """Notify admin about new project"""
        try:
            subject = f"New Project Created: {project.title}"
            
            body = f"""
            A new project has been created:
            
            Title: {project.title}
            Research Field: {project.research_field}
            User: {project.user.name} ({project.user.email})
            Created: {project.created_at}
            
            Please review and assign to appropriate staff member.
            
            Best regards,
            The Project Management System
            """
            
            # Send to admin email
            admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@example.com')
            
            msg = Message(
                subject=subject,
                recipients=[admin_email],
                body=body,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Failed to send new project notification: {e}")
            return False
    
    @staticmethod
    def notify_project_assignment(project, staff):
        """Notify staff about project assignment"""
        try:
            subject = f"New Project Assigned: {project.title}"
            
            body = f"""
            Dear {staff.user.name},
            
            A new project has been assigned to you:
            
            Title: {project.title}
            Research Field: {project.research_field}
            Client: {project.user.name}
            Created: {project.created_at}
            
            Please review the project details and start working on it as soon as possible.
            
            You can view the project in your dashboard.
            
            Best regards,
            The Project Management Team
            """
            
            msg = Message(
                subject=subject,
                recipients=[staff.user.email],
                body=body,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Failed to send project assignment notification: {e}")
            return False
    
    @staticmethod
    def notify_project_completion(project, staff=None):
        """Notify user about project completion"""
        try:
            subject = f"Project Completed: {project.title}"
            
            body = f"""
            Dear {project.user.name},
            
            Your project has been completed successfully!
            
            Title: {project.title}
            Research Field: {project.research_field}
            Completed by: {staff.user.name if staff else 'Staff member'}
            Completed: {project.completed_at}
            
            Please proceed with the payment to download your results.
            
            You can view the completed project in your dashboard.
            
            Best regards,
            The Project Management Team
            """
            
            msg = Message(
                subject=subject,
                recipients=[project.user.email],
                body=body,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Failed to send project completion notification: {e}")
            return False
    
    @staticmethod
    def notify_result_upload(project, staff):
        """Notify user about result upload"""
        try:
            subject = f"Result Uploaded: {project.title}"
            
            body = f"""
            Dear {project.user.name},
            
            The result for your project has been uploaded:
            
            Title: {project.title}
            Research Field: {project.research_field}
            Uploaded by: {staff.user.name}
            Uploaded: {project.updated_at}
            
            Please review the result and proceed with payment to download the complete file.
            
            Best regards,
            The Project Management Team
            """
            
            msg = Message(
                subject=subject,
                recipients=[project.user.email],
                body=body,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Failed to send result upload notification: {e}")
            return False
    
    @staticmethod
    def notify_payment_confirmation(project, payment):
        """Notify user about payment confirmation"""
        try:
            subject = f"Payment Confirmed: {project.title}"
            
            body = f"""
            Dear {project.user.name},
            
            Your payment has been confirmed successfully!
            
            Project: {project.title}
            Amount: ${payment.amount} {payment.currency}
            Transaction ID: {payment.transaction_id}
            Payment Date: {payment.processed_at}
            
            You can now download your completed project results.
            
            Best regards,
            The Project Management Team
            """
            
            msg = Message(
                subject=subject,
                recipients=[project.user.email],
                body=body,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Failed to send payment confirmation notification: {e}")
            return False
    
    @staticmethod
    def notify_project_status_update(project, staff):
        """Notify user about project status update"""
        try:
            subject = f"Project Status Update: {project.title}"
            
            body = f"""
            Dear {project.user.name},
            
            Your project status has been updated:
            
            Title: {project.title}
            New Status: {project.status}
            Updated by: {staff.user.name}
            Updated: {project.updated_at}
            
            You can view the project details in your dashboard.
            
            Best regards,
            The Project Management Team
            """
            
            msg = Message(
                subject=subject,
                recipients=[project.user.email],
                body=body,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Failed to send project status update notification: {e}")
            return False
    
    @staticmethod
    def send_email_verification_email(user, verification_token):
        """Send email verification email"""
        try:
            subject = "Verify Your Email Address"
            verification_link = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/verify-email?token={verification_token}"
            
            body = f"""
            Dear {user.name},
            
            Please verify your email address by clicking the link below:
            
            {verification_link}
            
            This link will expire in 24 hours.
            
            Best regards,
            The Project Management Team
            """
            
            msg = Message(
                subject=subject,
                recipients=[user.email],
                body=body,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Failed to send email verification: {e}")
            return False
    
    @staticmethod
    def send_account_deactivation_email(user):
        """Send account deactivation email"""
        try:
            subject = "Account Deactivated"
            
            body = f"""
            Dear {user.name},
            
            Your account has been deactivated by the administrator.
            
            If you believe this is an error, please contact our support team.
            
            Best regards,
            The Project Management Team
            """
            
            msg = Message(
                subject=subject,
                recipients=[user.email],
                body=body,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Failed to send account deactivation email: {e}")
            return False
    
    @staticmethod
    def send_staff_welcome_email(staff):
        """Send welcome email to new staff member"""
        try:
            subject = "Welcome to the Team"
            
            body = f"""
            Dear {staff.user.name},
            
            Welcome to our team! Your staff account has been successfully created.
            
            Your profile details:
            - Specialization: {staff.specialization}
            - Experience: {staff.experience_years} years
            - Qualification: {staff.qualification}
            
            You can now:
            - View and manage assigned projects
            - Update your profile and skills
            - Track your performance metrics
            
            Please log in to your dashboard to get started.
            
            Best regards,
            The Project Management Team
            """
            
            msg = Message(
                subject=subject,
                recipients=[staff.user.email],
                body=body,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Failed to send staff welcome email: {e}")
            return False
