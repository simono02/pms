from datetime import datetime
import json
import uuid
from app import db
from app.models.payment import Payment
from app.models.project import Project


class PaymentModule:
    """Business logic for Payment operations"""
    
    @staticmethod
    def to_dict(payment):
        """Convert payment object to dictionary"""
        return {
            'id': payment.id,
            'transaction_id': payment.transaction_id,
            'user_id': payment.user_id,
            'project_id': payment.project_id,
            'amount': payment.amount,
            'currency': payment.currency,
            'payment_type': payment.payment_type,  # ✅ ADDED
            'status': payment.status,
            'payment_method': payment.payment_method,
            
            # ✅ ADDED: M-Pesa details
            'mpesa_number': payment.mpesa_number,
            'mpesa_receipt_number': payment.mpesa_receipt_number,
            
            # ✅ ADDED: Card details (masked)
            'card_last4': payment.card_last4,
            'card_brand': payment.card_brand,
            'cardholder_name': payment.cardholder_name,
            
            'gateway_transaction_id': payment.gateway_transaction_id,
            'refund_reason': payment.refund_reason,
            'refund_amount': payment.refund_amount,  # ✅ ADDED
            'created_at': payment.created_at.isoformat() if payment.created_at else None,
            'updated_at': payment.updated_at.isoformat() if payment.updated_at else None,
            'processed_at': payment.processed_at.isoformat() if payment.processed_at else None,
            'refunded_at': payment.refunded_at.isoformat() if payment.refunded_at else None,
            'user': {
                'id': payment.user.id,
                'name': payment.user.name,
                'email': payment.user.email
            } if payment.user else None,
            'project': {
                'id': payment.project.id,
                'title': payment.project.title,
                'project_type': payment.project.project_type,  # ✅ CHANGED
                'total_price': payment.project.total_price,  # ✅ CHANGED
                'deposit_amount': payment.project.deposit_amount,  # ✅ ADDED
                'balance_amount': payment.project.balance_amount  # ✅ ADDED
            } if payment.project else None
        }
    
    # ✅ ADDED: Create deposit payment from dashboard
    @staticmethod
    def create_deposit_payment(user_id, project_id, payment_data):
        """Create deposit payment from dashboard"""
        project = Project.query.get(project_id)
        if not project:
            raise ValueError('Project not found')
        
        # Validate payment method
        payment_method = payment_data.get('paymentMethod')
        if payment_method not in ['mpesa', 'card']:
            raise ValueError('Invalid payment method')
        
        transaction_id = PaymentModule.generate_transaction_id()
        
        payment = Payment(
            transaction_id=transaction_id,
            user_id=user_id,
            project_id=project_id,
            amount=project.deposit_amount,
            currency='KES',
            payment_type='deposit',
            payment_method=payment_method,
            status='pending'
        )
        
        # Add method-specific details
        if payment_method == 'mpesa':
            mpesa_number = payment_data.get('mpesaNumber', '').strip()
            if not mpesa_number:
                raise ValueError('M-Pesa number is required')
            
            # Validate M-Pesa number format
            mpesa_clean = mpesa_number.replace(' ', '').replace('-', '')
            if not mpesa_clean.isdigit() or len(mpesa_clean) != 10:
                raise ValueError('Invalid M-Pesa number format')
            
            payment.mpesa_number = mpesa_clean
            
        elif payment_method == 'card':
            card_name = payment_data.get('cardName', '').strip()
            card_number = payment_data.get('cardNumber', '').replace(' ', '')
            expiry = payment_data.get('expiryDate', '').strip()
            cvv = payment_data.get('cvv', '').strip()
            
            # Validate card details
            if not card_name:
                raise ValueError('Cardholder name is required')
            if not card_number or len(card_number) != 16 or not card_number.isdigit():
                raise ValueError('Invalid card number')
            if not expiry or len(expiry) != 5 or expiry[2] != '/':
                raise ValueError('Invalid expiry date format (MM/YY)')
            if not cvv or len(cvv) < 3 or len(cvv) > 4 or not cvv.isdigit():
                raise ValueError('Invalid CVV')
            
            payment.cardholder_name = card_name
            # NEVER store full card number - only last 4 digits
            payment.card_last4 = card_number[-4:]
            # Determine card brand (simplified)
            if card_number[0] == '4':
                payment.card_brand = 'Visa'
            elif card_number[0:2] in ['51', '52', '53', '54', '55']:
                payment.card_brand = 'Mastercard'
            else:
                payment.card_brand = 'Unknown'
        
        # Store IP and user agent for fraud detection
        # These would be passed from the request in the route
        payment.ip_address = payment_data.get('ip_address')
        payment.user_agent = payment_data.get('user_agent')
        
        db.session.add(payment)
        db.session.commit()
        return payment
    
    # ✅ ADDED: Create balance payment
    @staticmethod
    def create_balance_payment(user_id, project_id, payment_data):
        """Create balance payment for project"""
        project = Project.query.get(project_id)
        if not project:
            raise ValueError('Project not found')
        
        if project.status != 'payment_required':
            raise ValueError('Project is not ready for balance payment')
        
        # Validate payment method
        payment_method = payment_data.get('paymentMethod')
        if payment_method not in ['mpesa', 'card']:
            raise ValueError('Invalid payment method')
        
        transaction_id = PaymentModule.generate_transaction_id()
        
        payment = Payment(
            transaction_id=transaction_id,
            user_id=user_id,
            project_id=project_id,
            amount=project.balance_amount,
            currency='KES',
            payment_type='balance',
            payment_method=payment_method,
            status='pending'
        )
        
        # Add method-specific details (same as deposit)
        if payment_method == 'mpesa':
            mpesa_number = payment_data.get('mpesaNumber', '').strip()
            if not mpesa_number:
                raise ValueError('M-Pesa number is required')
            
            mpesa_clean = mpesa_number.replace(' ', '').replace('-', '')
            if not mpesa_clean.isdigit() or len(mpesa_clean) != 10:
                raise ValueError('Invalid M-Pesa number format')
            
            payment.mpesa_number = mpesa_clean
            
        elif payment_method == 'card':
            card_name = payment_data.get('cardName', '').strip()
            card_number = payment_data.get('cardNumber', '').replace(' ', '')
            
            if not card_name or not card_number:
                raise ValueError('Card details are required')
            if len(card_number) != 16 or not card_number.isdigit():
                raise ValueError('Invalid card number')
            
            payment.cardholder_name = card_name
            payment.card_last4 = card_number[-4:]
            
            if card_number[0] == '4':
                payment.card_brand = 'Visa'
            elif card_number[0:2] in ['51', '52', '53', '54', '55']:
                payment.card_brand = 'Mastercard'
            else:
                payment.card_brand = 'Unknown'
        
        payment.ip_address = payment_data.get('ip_address')
        payment.user_agent = payment_data.get('user_agent')
        
        db.session.add(payment)
        db.session.commit()
        return payment
    
    @staticmethod
    def process_payment(payment, gateway_transaction_id, gateway_response):
        """Process payment with gateway response"""
        payment.gateway_transaction_id = gateway_transaction_id
        payment.gateway_response = gateway_response
        payment.status = 'processing'
        payment.processed_at = datetime.utcnow()
        payment.updated_at = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def complete_payment(payment):
        """Mark payment as completed"""
        if payment.status not in ['processing', 'pending']:  # ✅ CHANGED: Allow pending
            raise ValueError('Payment must be in processing or pending status to be completed')
        
        payment.status = 'completed'
        payment.processed_at = datetime.utcnow()
        payment.updated_at = datetime.utcnow()
        
        # ✅ CHANGED: Update project status based on payment type
        if payment.project:
            if payment.payment_type == 'deposit':
                # Deposit paid - keep project in pending/in_progress
                if payment.project.status == 'pending':
                    payment.project.status = 'pending'  # Ready for assignment
                    payment.project.updated_at = datetime.utcnow()
            elif payment.payment_type == 'balance':
                # Balance paid - mark project as completed
                from app.modules.project import ProjectModule
                ProjectModule.confirm_payment(payment.project)
        
        db.session.commit()
    
    @staticmethod
    def fail_payment(payment, reason=None):
        """Mark payment as failed"""
        payment.status = 'failed'
        payment.processed_at = datetime.utcnow()
        payment.updated_at = datetime.utcnow()
        
        if reason:
            if not payment.gateway_response:
                payment.gateway_response = '{}'
            
            response_data = json.loads(payment.gateway_response)
            response_data['failure_reason'] = reason
            payment.gateway_response = json.dumps(response_data)
        
        db.session.commit()
    
    @staticmethod
    def refund_payment(payment, reason, refund_amount=None):  # ✅ CHANGED: Added refund_amount
        """Refund payment"""
        if payment.status != 'completed':
            raise ValueError('Only completed payments can be refunded')
        
        payment.status = 'refunded'
        payment.refund_reason = reason
        payment.refund_amount = refund_amount or payment.amount  # ✅ ADDED
        payment.refunded_at = datetime.utcnow()
        payment.updated_at = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def is_completed(payment):
        """Check if payment is completed"""
        return payment.status == 'completed'
    
    @staticmethod
    def is_refunded(payment):
        """Check if payment is refunded"""
        return payment.status == 'refunded'
    
    @staticmethod
    def is_failed(payment):
        """Check if payment failed"""
        return payment.status == 'failed'
    
    @staticmethod
    def can_be_refunded(payment):
        """Check if payment can be refunded"""
        return payment.status == 'completed' and not PaymentModule.is_refunded(payment)
    
    @staticmethod
    def get_gateway_response_dict(payment):
        """Get gateway response as dictionary"""
        if not payment.gateway_response:
            return {}
        
        try:
            return json.loads(payment.gateway_response)
        except:
            return {}
    
    @staticmethod
    def set_gateway_response(payment, response_data):
        """Set gateway response from dictionary"""
        payment.gateway_response = json.dumps(response_data)
        payment.updated_at = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def update_status(payment, new_status):
        """Update payment status"""
        valid_statuses = ['pending', 'processing', 'completed', 'failed', 'refunded', 'cancelled']
        
        if new_status not in valid_statuses:
            raise ValueError(f'Invalid status: {new_status}')
        
        # Validate status transitions
        if payment.status == 'completed' and new_status != 'refunded':
            raise ValueError('Completed payments can only be refunded')
        
        if payment.status == 'refunded':
            raise ValueError('Refunded payments cannot change status')
        
        if payment.status == 'failed' and new_status not in ['pending']:
            raise ValueError('Failed payments can only be retried')
        
        payment.status = new_status
        payment.updated_at = datetime.utcnow()
        
        if new_status in ['completed', 'failed', 'refunded']:
            payment.processed_at = datetime.utcnow()
        
        if new_status == 'refunded':
            payment.refunded_at = datetime.utcnow()
        
        db.session.commit()
    
    @staticmethod
    def generate_transaction_id():
        """Generate unique transaction ID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def find_by_transaction_id(transaction_id):
        """Find payment by transaction ID"""
        return Payment.query.filter_by(transaction_id=transaction_id).first()
    
    @staticmethod
    def find_by_id(payment_id):
        """Find payment by ID"""
        return Payment.query.get(payment_id)
    
    @staticmethod
    def find_by_user_id(user_id):
        """Find payments by user ID"""
        return Payment.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def find_by_project_id(project_id):
        """Find payments by project ID"""
        return Payment.query.filter_by(project_id=project_id).all()
    
    @staticmethod
    def find_by_status(status):
        """Find payments by status"""
        return Payment.query.filter_by(status=status).all()
    
    @staticmethod
    def get_completed_payments():
        """Get all completed payments"""
        return Payment.query.filter_by(status='completed').all()
    
    @staticmethod
    def get_failed_payments():
        """Get all failed payments"""
        return Payment.query.filter_by(status='failed').all()
    
    @staticmethod
    def get_refunded_payments():
        """Get all refunded payments"""
        return Payment.query.filter_by(status='refunded').all()
    
    @staticmethod
    def get_payment_stats():
        """Get payment statistics"""
        total_payments = Payment.query.count()
        completed_payments = Payment.query.filter_by(status='completed').count()
        failed_payments = Payment.query.filter_by(status='failed').count()
        refunded_payments = Payment.query.filter_by(status='refunded').count()
        pending_payments = Payment.query.filter_by(status='pending').count()
        
        total_revenue = db.session.query(db.func.sum(Payment.amount))\
                              .filter_by(status='completed')\
                              .scalar() or 0
        
        return {
            'total_payments': total_payments,
            'completed_payments': completed_payments,
            'failed_payments': failed_payments,
            'refunded_payments': refunded_payments,
            'pending_payments': pending_payments,
            'total_revenue': float(total_revenue),
            'success_rate': (completed_payments / max(total_payments, 1)) * 100
        }
    
    @staticmethod
    def create_payment(user_id, project_id, amount, **kwargs):
        """Create a new payment"""
        transaction_id = PaymentModule.generate_transaction_id()
        
        payment = Payment(
            transaction_id=transaction_id,
            user_id=user_id,
            project_id=project_id,
            amount=amount
        )
        
        for key, value in kwargs.items():
            if hasattr(payment, key):
                setattr(payment, key, value)
        
        db.session.add(payment)
        db.session.commit()
        return payment
    
    @staticmethod
    def delete(payment):
        """Delete payment"""
        db.session.delete(payment)
        db.session.commit()