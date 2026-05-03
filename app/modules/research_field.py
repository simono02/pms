from datetime import datetime
from app import db
from app.models.research_field import ResearchField


class ResearchFieldModule:
    """Business logic for ResearchField operations"""
    
    @staticmethod
    def to_dict(field):
        """Convert research field to dictionary"""
        return {
            'id': field.id,
            'name': field.name,
            'display_name': field.display_name,
            'description': field.description,
            'icon': field.icon,
            'color': field.color,
            'is_active': field.is_active,
            'sort_order': field.sort_order,
            'created_at': field.created_at.isoformat() if field.created_at else None,
            'updated_at': field.updated_at.isoformat() if field.updated_at else None
        }
    
    @staticmethod
    def activate(field):
        """Activate research field"""
        field.is_active = True
        field.updated_at = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def deactivate(field):
        """Deactivate research field"""
        field.is_active = False
        field.updated_at = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def update_details(field, **kwargs):
        """Update research field details"""
        allowed_fields = [
            'display_name', 'description', 'icon', 'color', 
            'is_active', 'sort_order'
        ]
        
        for field_name in allowed_fields:
            if field_name in kwargs:
                setattr(field, field_name, kwargs[field_name])
        
        field.updated_at = datetime.utcnow()
        db.session.commit()
        return field
    
    @staticmethod
    def find_by_id(field_id):
        """Find research field by ID"""
        return ResearchField.query.get(field_id)
    
    @staticmethod
    def find_by_name(name):
        """Find research field by name"""
        return ResearchField.query.filter_by(name=name).first()
    
    @staticmethod
    def get_all_active():
        """Get all active research fields"""
        return ResearchField.query.filter_by(is_active=True)\
                                .order_by(ResearchField.sort_order.asc(), ResearchField.display_name.asc())\
                                .all()
    
    @staticmethod
    def get_all():
        """Get all research fields"""
        return ResearchField.query.order_by(
            ResearchField.sort_order.asc(), 
            ResearchField.display_name.asc()
        ).all()
    
    @staticmethod
    def create_field(name, display_name, **kwargs):
        """Create a new research field"""
        # Check if field already exists
        if ResearchFieldModule.find_by_name(name):
            raise ValueError('Research field with this name already exists')
        
        field = ResearchField(name=name, display_name=display_name)
        
        for key, value in kwargs.items():
            if hasattr(field, key):
                setattr(field, key, value)
        
        db.session.add(field)
        db.session.commit()
        return field
    
    @staticmethod
    def delete(field):
        """Delete research field"""
        db.session.delete(field)
        db.session.commit()