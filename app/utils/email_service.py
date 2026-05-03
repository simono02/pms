from flask_mail import Message
from flask import current_app
from app import mail
import os

class EmailService:
    @staticmethod
    def send_email(to, subject, body, html_body=None, attachments=None):
        """Send email"""
        try:
            msg = Message(
                subject=subject,
                recipients=[to] if isinstance(to, list) else [to],
                body=body,
                html=html_body,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@projectmanagement.com')
            )
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    with open(attachment['path'], 'rb') as f:
                        msg.attach(
                            attachment['filename'],
                            attachment['content_type'],
                            f.read(),
                            disposition=f'attachment; filename="{attachment["filename"]}"'
                        )
            
            mail.send(msg)
            return True, "Email sent successfully"
            
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"
    
    @staticmethod
    def send_welcome_email(user):
        """Send welcome email to new user"""
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
        
        return EmailService.send_email(user.email, subject, body)
    
    @staticmethod
    def send_password_reset_email(user, reset_token):
        """Send password reset email"""
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
        
        return EmailService.send_email(user.email, subject, body)
    
    @staticmethod
    def send_project_assignment_notification(project, staff):
        """Notify staff about project assignment"""
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
        
        return EmailService.send_email(staff.user.email, subject, body)
    
    @staticmethod
    def send_project_completion_notification(project, staff=None):
        """Notify user about project completion"""
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
        
        return EmailService.send_email(project.user.email, subject, body)
    
    @staticmethod
    def send_payment_confirmation(project, payment):
        """Notify user about payment confirmation"""
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
        
        return EmailService.send_email(project.user.email, subject, body)
    
    @staticmethod
    def send_staff_welcome_email(staff):
        """Send welcome email to new staff member"""
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
        
        return EmailService.send_email(staff.user.email, subject, body)

# Create instance
email_service = EmailService()
