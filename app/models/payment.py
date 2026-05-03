from datetime import datetime
from app import db

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    # Payment Details
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='KES')
    payment_type = db.Column(db.String(20), default='deposit')  # deposit, balance, full
    
    # Payment Method
    payment_method = db.Column(db.String(50))  # mpesa, card, bank_transfer
    
    # M-Pesa Details
    mpesa_number = db.Column(db.String(15))  # Phone number for M-Pesa
    mpesa_receipt_number = db.Column(db.String(100))  # M-Pesa confirmation code
    
    # Card Details (encrypted/tokenized in production)
    card_last4 = db.Column(db.String(4))  # Last 4 digits of card
    card_brand = db.Column(db.String(20))  # Visa, Mastercard, etc.
    cardholder_name = db.Column(db.String(100))
    
    # Payment Gateway Info
    gateway_transaction_id = db.Column(db.String(200))  # External payment gateway transaction ID
    gateway_response = db.Column(db.Text)  # JSON response from payment gateway
    
    # Status & Timestamps
    status = db.Column(db.String(20), nullable=False, default='pending')  
    # pending, processing, completed, failed, refunded, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    # Refund Info
    refund_reason = db.Column(db.Text)
    refunded_at = db.Column(db.DateTime)
    refund_amount = db.Column(db.Float)
    
    # Additional Metadata
    ip_address = db.Column(db.String(45))  # For fraud detection
    user_agent = db.Column(db.String(255))  # Browser/device info
    
    def __repr__(self):
        return f'<Payment {self.transaction_id}>'