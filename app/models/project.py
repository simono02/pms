from datetime import datetime
from app import db

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)  # JSON string storing detailed project info
    
    # Project Type & Academic Info
    project_type = db.Column(db.String(50), nullable=False)  # research, thesis, dissertation, etc.
    academic_level = db.Column(db.String(50))  # undergraduate, masters, phd, professional
    research_field = db.Column(db.String(100))
    
    # Research Details
    research_question = db.Column(db.Text)
    keywords = db.Column(db.Text)  # Comma-separated or JSON
    citation_style = db.Column(db.String(50))  # apa, mla, chicago, harvard, ieee, vancouver
    methodology = db.Column(db.String(50))  # qualitative, quantitative, mixed, theoretical, experimental
    specific_requirements = db.Column(db.Text)
    
    # Pricing Information
    pricing_type = db.Column(db.String(20), default='per-page')  # per-page or per-chapter
    pages = db.Column(db.Integer)  # Number of pages
    chapters = db.Column(db.Integer)  # Number of chapters
    price_per_unit = db.Column(db.Float)  # Price per page or per chapter
    total_price = db.Column(db.Float, nullable=False)  # Total project cost
    deposit_amount = db.Column(db.Float)  # 50% deposit
    balance_amount = db.Column(db.Float)  # Remaining balance
    currency = db.Column(db.String(3), default='KES')
    
    # Status & Progress
    status = db.Column(db.String(20), nullable=False, default='pending')  
    # pending, in_progress, pending_review, payment_required, completed, cancelled
    progress = db.Column(db.Integer, default=0)  # 0-100%
    priority = db.Column(db.String(10), default='medium')  # low, medium, high
    
    # File Management
    description_file_path = db.Column(db.String(500))  # Optional description file
    description_file_name = db.Column(db.String(255))
    file_path = db.Column(db.String(500))  # Original project file (if any)
    original_filename = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    result_path = db.Column(db.String(500))  # Completed work file
    result_filename = db.Column(db.String(255))
    
    # Dates & Timeline
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deadline = db.Column(db.DateTime)
    assigned_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    estimated_duration = db.Column(db.String(50))  # e.g., "2 weeks", "1 month"
    actual_duration = db.Column(db.String(50))
    
    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    payments = db.relationship('Payment', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Project {self.title}>'