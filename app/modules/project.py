from datetime import datetime, timedelta
import json
from app import db
from app.models.project import Project


class ProjectModule:
    """Business logic for Project operations"""
    
    @staticmethod
    def to_dict(project, include_details=False):
        """Convert project object to dictionary"""
        data = {
            'id': project.id,
            'title': project.title,
            'project_type': project.project_type,  # ✅ ADDED
            'academic_level': project.academic_level,  # ✅ ADDED
            'research_field': project.research_field,
            'research_question': project.research_question,  # ✅ ADDED
            'status': project.status,
            'priority': project.priority,
            'progress': project.progress,  # ✅ ADDED
            
            # ✅ ADDED: Pricing info
            'pricing_type': project.pricing_type,
            'pages': project.pages,
            'chapters': project.chapters,
            'price_per_unit': project.price_per_unit,
            'total_price': project.total_price,
            'deposit_amount': project.deposit_amount,
            'balance_amount': project.balance_amount,
            'currency': project.currency,
            
            # ✅ ADDED: Research details
            'citation_style': project.citation_style,
            'methodology': project.methodology,
            'keywords': project.keywords,
            'specific_requirements': project.specific_requirements,
            
            'estimated_duration': project.estimated_duration,
            'actual_duration': project.actual_duration,
            'original_filename': project.original_filename,
            'file_size': project.file_size,
            'created_at': project.created_at.isoformat() if project.created_at else None,
            'updated_at': project.updated_at.isoformat() if project.updated_at else None,
            'assigned_at': project.assigned_at.isoformat() if project.assigned_at else None,
            'completed_at': project.completed_at.isoformat() if project.completed_at else None,
            'deadline': project.deadline.isoformat() if project.deadline else None,
            'user': {
                'id': project.user.id,
                'name': project.user.name,
                'email': project.user.email
            } if project.user else None,
            'assigned_staff': {
                'id': project.assigned_staff.id,
                'name': project.assigned_staff.user.name,
                'specialization': project.assigned_staff.specialization
            } if project.assigned_staff else None
        }
        
        if include_details:
            data['description'] = project.description  # ✅ CHANGED: Now just text, not JSON
            data['has_file'] = bool(project.file_path)
            data['has_result'] = bool(project.result_path)
            data['has_description_file'] = bool(project.description_file_path)  # ✅ ADDED
            data['payments'] = [payment.to_dict() for payment in project.payments] if hasattr(project, 'payments') else []
        
        return data
    
    @staticmethod
    def get_description_dict(project):
        """Get description as dictionary"""
        if not project.description:
            return {}
        
        try:
            return json.loads(project.description)
        except:
            return {'objectives': project.description}
    
    @staticmethod
    def set_description_dict(project, description_dict):
        """Set description from dictionary"""
        project.description = json.dumps(description_dict)
        project.updated_at = datetime.utcnow()
        db.session.commit()
    
    # ✅ ADDED: Calculate pricing based on type and quantity
    @staticmethod
    def calculate_pricing(pricing_type, quantity):
        """Calculate project pricing based on type and quantity"""
        if pricing_type == 'per-page':
            price_per_unit = 370.0
            total = quantity * price_per_unit
        elif pricing_type == 'per-chapter':
            price_per_unit = 2000.0
            total = quantity * price_per_unit
        else:
            raise ValueError('Invalid pricing type. Must be "per-page" or "per-chapter"')
        
        deposit = total / 2  # 50% deposit
        balance = total - deposit
        
        return {
            'price_per_unit': price_per_unit,
            'total_price': total,
            'deposit_amount': deposit,
            'balance_amount': balance
        }
    
    # ✅ ADDED: Update project progress
    @staticmethod
    def update_progress(project, progress_percentage):
        """Update project progress"""
        if not 0 <= progress_percentage <= 100:
            raise ValueError('Progress must be between 0 and 100')
        
        project.progress = progress_percentage
        project.updated_at = datetime.utcnow()
        
        # Auto-update status based on progress
        if progress_percentage == 100 and project.status == 'in_progress':
            project.status = 'payment_required'
        elif progress_percentage > 0 and project.status == 'pending':
            project.status = 'in_progress'
        
        db.session.commit()
    
    @staticmethod
    def can_be_edited(project):
        """Check if project can be edited (within 24 hours of creation)"""
        if project.status not in ['pending']:
            return False
        
        time_diff = datetime.utcnow() - project.created_at
        return time_diff < timedelta(hours=24)
    
    @staticmethod
    def assign_to_staff(project, staff_id):
        """Assign project to staff member"""
        if project.status != 'pending':
            raise ValueError('Project cannot be assigned in current status')
        
        project.assigned_staff_id = staff_id
        project.status = 'in_progress'
        project.assigned_at = datetime.utcnow()
        project.updated_at = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def unassign_staff(project):
        """Unassign staff from project"""
        if project.status == 'completed':
            raise ValueError('Cannot unassign completed project')
        
        project.assigned_staff_id = None
        project.status = 'pending'
        project.assigned_at = None
        project.updated_at = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def complete_project(project, result_path=None, result_filename=None):
        """Mark project as completed"""
        if project.status != 'in_progress':
            raise ValueError('Project must be in progress to be completed')
        
        project.status = 'payment_required'
        project.progress = 100  # ✅ ADDED: Set progress to 100%
        
        if result_path:
            project.result_path = result_path
        if result_filename:
            project.result_filename = result_filename
        
        project.updated_at = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def confirm_payment(project):
        """Confirm payment and mark as completed"""
        if project.status != 'payment_required':
            raise ValueError('Payment is not required for this project')
        
        project.status = 'completed'
        project.completed_at = datetime.utcnow()
        
        # Calculate actual duration
        if project.assigned_at:
            duration = project.completed_at - project.assigned_at
            days = duration.days
            if days == 0:
                project.actual_duration = "Less than a day"
            elif days == 1:
                project.actual_duration = "1 day"
            elif days < 7:
                project.actual_duration = f"{days} days"
            elif days < 30:
                weeks = days // 7
                project.actual_duration = f"{weeks} week{'s' if weeks > 1 else ''}"
            else:
                months = days // 30
                project.actual_duration = f"{months} month{'s' if months > 1 else ''}"
        
        project.updated_at = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def cancel_project(project):
        """Cancel project"""
        if project.status == 'completed':
            raise ValueError('Cannot cancel completed project')
        
        project.status = 'cancelled'
        project.updated_at = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def archive_project(project):
        """Archive project"""
        project.status = 'archived'
        project.updated_at = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def set_deadline(project, days):
        """Set project deadline"""
        project.deadline = datetime.utcnow() + timedelta(days=days)
        project.updated_at = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def is_overdue(project):
        """Check if project is overdue"""
        if not project.deadline:
            return False
        
        return datetime.utcnow() > project.deadline and project.status not in ['completed', 'cancelled']
    
    @staticmethod
    def get_days_until_deadline(project):
        """Get days until deadline"""
        if not project.deadline:
            return None
        
        delta = project.deadline - datetime.utcnow()
        return delta.days
    
    @staticmethod
    def update_status(project, new_status):
        """Update project status"""
        valid_statuses = ['pending', 'in_progress', 'payment_required', 'completed', 'cancelled', 'archived']
        
        if new_status not in valid_statuses:
            raise ValueError(f'Invalid status: {new_status}')
        
        # Validate status transitions
        if project.status == 'completed' and new_status != 'archived':
            raise ValueError('Completed projects can only be archived')
        
        if project.status == 'cancelled' and new_status not in ['pending']:
            raise ValueError('Cancelled projects can only be reactivated')
        
        project.status = new_status
        project.updated_at = datetime.utcnow()
        
        if new_status == 'completed':
            project.completed_at = datetime.utcnow()
        
        db.session.commit()
    
    @staticmethod
    def update_details(project, **kwargs):
        """Update project details"""
        # ✅ UPDATED: Added new fields
        editable_fields = [
            'title', 'research_field', 'description', 'priority', 
            'price', 'currency', 'estimated_duration', 'deadline',
            'project_type', 'academic_level', 'research_question',
            'keywords', 'citation_style', 'methodology', 
            'specific_requirements', 'pricing_type', 'pages', 
            'chapters', 'price_per_unit', 'total_price', 
            'deposit_amount', 'balance_amount'
        ]
        
        for field in editable_fields:
            if field in kwargs:
                setattr(project, field, kwargs[field])
        
        project.updated_at = datetime.utcnow()
        db.session.commit()
        return project
    
    @staticmethod
    def get_file_info(project):
        """Get file information"""
        if not project.file_path:
            return None
        
        return {
            'path': project.file_path,
            'original_filename': project.original_filename,
            'size': project.file_size
        }
    
    @staticmethod
    def get_result_info(project):
        """Get result file information"""
        if not project.result_path:
            return None
        
        return {
            'path': project.result_path,
            'filename': project.result_filename
        }
    
    @staticmethod
    def find_by_id(project_id):
        """Find project by ID"""
        return Project.query.get(project_id)
    
    @staticmethod
    def find_by_user_id(user_id):
        """Find projects by user ID"""
        return Project.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def find_by_staff_id(staff_id):
        """Find projects by staff ID"""
        return Project.query.filter_by(assigned_staff_id=staff_id).all()
    
    @staticmethod
    def find_by_status(status):
        """Find projects by status"""
        return Project.query.filter_by(status=status).all()
    
    @staticmethod
    def find_by_research_field(field):
        """Find projects by research field"""
        return Project.query.filter_by(research_field=field).all()
    
    @staticmethod
    def get_unassigned_projects():
        """Get unassigned projects"""
        return Project.query.filter_by(status='pending').all()
    
    @staticmethod
    def get_overdue_projects():
        """Get overdue projects"""
        return Project.query.filter(
            Project.deadline < datetime.utcnow(),
            Project.status.in_(['pending', 'in_progress'])
        ).all()
    
    @staticmethod
    def search_projects(query, user_id=None):
        """Search projects"""
        # ✅ UPDATED: Search in more fields
        search_filter = (
            Project.title.contains(query) | 
            Project.description.contains(query) |
            Project.research_question.contains(query)
        )
        
        if user_id:
            search_filter &= Project.user_id == user_id
        
        return Project.query.filter(search_filter).all()
    
    @staticmethod
    def create_project(title, research_field, user_id, **kwargs):
        """Create a new project"""
        project = Project(
            title=title,
            research_field=research_field,
            user_id=user_id,
            **kwargs
        )
        db.session.add(project)
        db.session.commit()
        return project
    
    @staticmethod
    def delete(project):
        """Delete project"""
        db.session.delete(project)
        db.session.commit()