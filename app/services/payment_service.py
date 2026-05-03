from app.models.payment import Payment
from app.models.project import Project
from app.models.user import User
from app.utils.email_service import EmailService
from app.utils.validators import validate_card_number, validate_expiry_date, validate_cvv
import uuid
import os
from datetime import datetime, timedelta

class PaymentService:
    @staticmethod
    def process_payment(project_id, payment_data):
        """Process payment for a project"""
        try:
            project = Project.find_by_id(project_id)
            
            if not project:
                return {'success': False, 'message': 'Project not found'}
            
            # Check if project is ready for payment
            if project.status != 'payment_required':
                return {'success': False, 'message': 'Project is not ready for payment'}
            
            # Validate payment data
            required_fields = ['amount', 'payment_method', 'card_number', 'card_name', 'expiry_date', 'cvv']
            
            for field in required_fields:
                if not payment_data.get(field) or not payment_data[field].strip():
                    return {'success': False, message': f'{field} is required'}
            
            amount = payment_data['amount']
            payment_method = payment_data['payment_method']
            card_number = payment_data['card_number'].replace(' ', '')
            card_name = payment_data['card_name'].strip()
            expiry_date = payment_data['expiry_date']
            cvv = payment_data['cvv']
            
            # Validate amount
            try:
                amount = float(amount)
                if amount <= 0:
                    return {'success': False, 'message': 'Amount must be positive'}
            except ValueError:
                return {'success': False, 'message': 'Invalid amount format'}
            
            # Validate card number
            if len(card_number) != 16 or not card_number.isdigit():
                return {'success': False, 'message': 'Invalid card number (must be 16 digits)'}
            
            # Validate expiry date
            if not validate_expiry_date(expiry_date):
                return {'success': False, 'message': 'Invalid expiry date format (MM/YY)'}
            
            # Validate CVV
            if len(cvv) < 3 or len(cvv) > 4 or not cvv.isdigit():
                return {'success': False, 'message': 'CVV must be 3 or 4 digits'}
            
            # Validate payment method
            valid_methods = ['credit_card', 'debit_card', 'paypal', 'stripe', 'bank_transfer']
            if payment_method not in valid_methods:
                return {'success': False, 'message': 'Invalid payment method'}
            
            # Create payment record
            transaction_id = Payment.generate_transaction_id()
            
            payment = Payment(
                transaction_id=transaction_id,
                user_id=project.user_id,
                project_id=project_id,
                amount=amount,
                currency=project.currency,
                payment_method=payment_method,
                card_number=card_number,
                card_name=card_name,
                expiry_date=expiry_date,
                cvv=cvv
            )
            
            # Process payment (simulate)
            payment.process_payment(
                gateway_transaction_id=f"gw_{transaction_id}",
                gateway_response={
                    'status': 'success',
                    'transaction_id': transaction_id,
                    'amount': amount,
                    'currency': project.currency,
                    'payment_method': payment_method,
                    'card_number': card_number,
                    'card_name': card_name,
                    'expiry_date': expiry_date
                }
            )
            
            # Complete payment
            payment.complete_payment()
            
            return {
                'success': True,
                'message': 'Payment processed successfully',
                'payment': payment.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Payment processing failed: {str(e)}'}
    
    @staticmethod
    def verify_payment(payment_id):
        """Verify payment status"""
        try:
            payment = Payment.find_by_id(payment_id)
            
            if not payment:
                return {'success': False, 'message': 'Payment not found'}
            
            if payment.is_completed():
                return {'success': True, 'verified': True, 'payment': payment.to_dict()}
            
            # TODO: Verify with payment gateway
            # For now, we'll check the current status
            return {
                'success': True,
                'verified': False,
                'status': payment.status,
                'payment': payment.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Payment verification failed: {str(e)}'}
    
    @staticmethod
    def get_payment_status(payment_id):
        """Get payment status"""
        try:
            payment = Payment.find_by_id(payment_id)
            
            if not payment:
                return {'success': False, 'message': 'Payment not found'}
            
            return {
                'success': True,
                'status': payment.status,
                'can_be_refunded': payment.can_be_refunded(),
                'is_completed': payment.is_completed(),
                'is_failed': payment.is_failed(),
                'is_refunded': payment.is_refunded(),
                'payment': payment.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Payment status check failed: {str(e)}'
    
    @staticmethod
    def get_payment_history(user_id=None, page=1, per_page=10, status=None):
        """Get payment history"""
        try:
            if user_id:
                user = User.find_by_id(user_id)
                
                if not user:
                    return {'success': False, 'message': 'User not found'}
                
                payments = Payment.query.filter_by(user_id=user_id)
            else:
                payments = Payment.query.order_by(Payment.created_at.desc())
            
            if status:
                payments = payments.filter_by(status=status)
            
            # Order by most recent
            payments = payments.order_by(Payment.created_at.desc())
            
            # Paginate
            payments = payments.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            return {
                'success': True,
                'payments': [payment.to_dict() for payment in payments.items],
                'pagination': {
                    'page': payments.page,
                    'per_page': payments.per_page,
                    'total': payments.total,
                    'pages': payments.pages,
                    'has_next': payments.has_next,
                    'has_prev': payments.has_prev
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Payment history failed: {str(e)}'}
    
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
            return {'success': False, 'message': f'Payment stats failed: {str(e)}'}
    
    @staticmethod
    def get_user_payment_summary(user_id):
        """Get payment summary for a user"""
        try:
            user = User.find_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            payments = Payment.query.filter_by_user_id=user_id)
            
            total_payments = len(payments)
            completed_payments = len([p for p in payments if p.is_completed()])
            failed_payments = len([p for p in payments if p.is_failed()])
            refunded_payments = len([p for p in payments if p.is_refunded()])
            total_spent = sum([p.amount for p in payments if p.is_completed()])
            
            return {
                'success': True,
                'summary': {
                    'total_payments': total_payments,
                    'completed_payments': completed_payments,
                    'failed_payments': failed_payments,
                    'refunded_payments': refunded_payments,
                    'total_spent': total_spent
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Payment summary failed: {str(e)}'}
    
    @staticmethod
    def get_payment_details(payment_id):
        """Get detailed payment information"""
        try:
            payment = Payment.find_by_id(payment_id)
            
            if not payment:
                return {'success': False, 'message': 'Payment not found'}
            
            return {
                'success': True,
                'payment': payment.to_dict()
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Payment details failed: {str(e)}'}
    
    @staticmethod
def payment_service():
    """Create payment service instance"""
    return PaymentService()

# Create instance for direct use
payment_service = PaymentService()
