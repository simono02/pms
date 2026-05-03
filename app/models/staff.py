from datetime import datetime
from app import db


class Staff(db.Model):
    __tablename__ = 'staff'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    # Identity
    id_number  = db.Column(db.String(50), unique=True, nullable=True)

    # Profile
    specialization   = db.Column(db.String(100))
    experience_years = db.Column(db.Integer, default=0)
    qualification    = db.Column(db.String(200))
    bio              = db.Column(db.Text)
    skills           = db.Column(db.Text)          # JSON string e.g. '["Python", "R"]'

    # Rates
    rate_per_page    = db.Column(db.Float, nullable=True)
    rate_per_chapter = db.Column(db.Float, nullable=True)
    hourly_rate      = db.Column(db.Float, nullable=True)   # kept for backwards compat

    # Status & performance
    availability       = db.Column(db.Boolean, default=True)
    rating             = db.Column(db.Float, default=0.0)
    total_projects     = db.Column(db.Integer, default=0)
    completed_projects = db.Column(db.Integer, default=0)

    # Account setup (set by admin, completed by staff via email link)
    password_set               = db.Column(db.Boolean, default=False)
    verification_token         = db.Column(db.String(128), nullable=True, unique=True)
    verification_token_expires = db.Column(db.DateTime, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user              = db.relationship('User', backref=db.backref('staff_profile', uselist=False))
    assigned_projects = db.relationship('Project', backref='assigned_staff', lazy='dynamic')

    def __repr__(self):
        return f'<Staff {self.user.name if self.user else "Unknown"} ({self.id_number})>'