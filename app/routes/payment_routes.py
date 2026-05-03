from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, limiter
from app.models.payment import Payment
from app.models.project import Project
from app.models.user import User

# ✅ ADDED: Import modules
from app.modules.user import UserModule
from app.modules.project import ProjectModule
from app.modules.payment import PaymentModule

bp = Blueprint('payments', __name__, url_prefix='/api/payments')

# ✅ NEW: Process deposit payment from dashboard
@bp.route('/deposit/<int:project_id>', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def process_deposit(project_id):
    """Process deposit payment for a new project"""
    try:
        current_user_id = get_jwt_identity()
        user = UserModule.find_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        project = ProjectModule.find_by_id(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check if user owns the project
        if project.user_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if project is in correct status
        if project.status not in ['pending']:
            return jsonify({'error': 'Deposit already paid or project not pending'}), 400
        
        data = request.get_json()
        
        # Validate payment method
        if not data.get('paymentMethod'):
            return jsonify({'error': 'Payment method is required'}), 400
        
        payment_method = data['paymentMethod']
        
        # Validate method-specific required fields
        if payment_method == 'mpesa':
            if not data.get('mpesaNumber'):
                return jsonify({'error': 'M-Pesa number is required'}), 400
        elif payment_method == 'card':
            required_card_fields = ['cardName', 'cardNumber', 'expiryDate', 'cvv']
            for field in required_card_fields:
                if not data.get(field):
                    return jsonify({'error': f'{field} is required'}), 400
        else:
            return jsonify({'error': 'Invalid payment method'}), 400
        
        # Add IP and user agent for fraud detection
        data['ip_address'] = request.remote_addr
        data['user_agent'] = request.headers.get('User-Agent', '')
        
        # Create deposit payment
        payment = PaymentModule.create_deposit_payment(
            current_user_id,
            project_id,
            data
        )
        
        # TODO: Integrate with actual payment gateway (M-Pesa STK Push, Card gateway, etc.)
        # For now, simulate payment processing
        gateway_transaction_id = f"gw_{payment.transaction_id[:8]}"
        
        PaymentModule.process_payment(
            payment,
            gateway_transaction_id=gateway_transaction_id,
            gateway_response=json.dumps({
                'status': 'success',
                'transaction_id': payment.transaction_id,
                'amount': payment.amount,
                'currency': 'KES',
                'method': payment_method
            })
        )
        
        # Simulate immediate completion (in production, this would be via webhook)
        PaymentModule.complete_payment(payment)
        
        return jsonify({
            'message': 'Deposit payment processed successfully',
            'payment': PaymentModule.to_dict(payment),
            'project': ProjectModule.to_dict(project, include_details=True)
        }), 200
        
    except ValueError as ve:
        db.session.rollback()
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Payment processing failed', 'details': str(e)}), 500

# ✅ NEW: Process balance payment
@bp.route('/balance/<int:project_id>', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def process_balance(project_id):
    """Process balance payment for a completed project"""
    try:
        current_user_id = get_jwt_identity()
        user = UserModule.find_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        project = ProjectModule.find_by_id(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check if user owns the project
        if project.user_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if project requires balance payment
        if project.status != 'payment_required':
            return jsonify({'error': 'Project does not require balance payment'}), 400
        
        data = request.get_json()
        
        # Validate payment method
        if not data.get('paymentMethod'):
            return jsonify({'error': 'Payment method is required'}), 400
        
        payment_method = data['paymentMethod']
        
        if payment_method == 'mpesa':
            if not data.get('mpesaNumber'):
                return jsonify({'error': 'M-Pesa number is required'}), 400
        elif payment_method == 'card':
            required_card_fields = ['cardName', 'cardNumber', 'expiryDate', 'cvv']
            for field in required_card_fields:
                if not data.get(field):
                    return jsonify({'error': f'{field} is required'}), 400
        else:
            return jsonify({'error': 'Invalid payment method'}), 400
        
        data['ip_address'] = request.remote_addr
        data['user_agent'] = request.headers.get('User-Agent', '')
        
        # Create balance payment
        payment = PaymentModule.create_balance_payment(
            current_user_id,
            project_id,
            data
        )
        
        # TODO: Integrate with actual payment gateway
        gateway_transaction_id = f"gw_{payment.transaction_id[:8]}"
        
        PaymentModule.process_payment(
            payment,
            gateway_transaction_id=gateway_transaction_id,
            gateway_response=json.dumps({
                'status': 'success',
                'transaction_id': payment.transaction_id,
                'amount': payment.amount,
                'currency': 'KES',
                'method': payment_method
            })
        )
        
        # Complete payment (this will mark project as completed)
        PaymentModule.complete_payment(payment)
        
        return jsonify({
            'message': 'Balance payment processed successfully',
            'payment': PaymentModule.to_dict(payment),
            'project': ProjectModule.to_dict(project, include_details=True)
        }), 200
        
    except ValueError as ve:
        db.session.rollback()
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Payment processing failed', 'details': str(e)}), 500

@bp.route('/verify/<int:payment_id>', methods=['POST'])
@jwt_required()
def verify_payment(payment_id):
    """Verify payment status"""
    try:
        current_user_id = get_jwt_identity()
        user = UserModule.find_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        payment = PaymentModule.find_by_id(payment_id)
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        # Check if user owns the payment
        if payment.user_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # TODO: Verify payment with gateway
        if PaymentModule.is_completed(payment):
            return jsonify({
                'verified': True,
                'status': payment.status,
                'payment': PaymentModule.to_dict(payment)
            }), 200
        else:
            return jsonify({
                'verified': False,
                'status': payment.status,
                'payment': PaymentModule.to_dict(payment)
            }), 200
        
    except Exception as e:
        return jsonify({'error': 'Payment verification failed', 'details': str(e)}), 500

@bp.route('/status/<int:payment_id>', methods=['GET'])
@jwt_required()
def get_payment_status(payment_id):
    """Get payment status"""
    try:
        current_user_id = get_jwt_identity()
        user = UserModule.find_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        payment = PaymentModule.find_by_id(payment_id)
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        # Check if user owns the payment
        if payment.user_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'status': payment.status,
            'payment': PaymentModule.to_dict(payment)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get payment status', 'details': str(e)}), 500

@bp.route('/history', methods=['GET'])
@jwt_required()
def get_payment_history():
    """Get payment history for current user"""
    try:
        current_user_id = get_jwt_identity()
        user = UserModule.find_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        status = request.args.get('status')
        payment_type = request.args.get('type')  # ✅ ADDED
        
        # Build query
        query = Payment.query.filter_by(user_id=current_user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if payment_type:  # ✅ ADDED
            query = query.filter_by(payment_type=payment_type)
        
        # Order by most recent
        query = query.order_by(Payment.created_at.desc())
        
        # Paginate
        payments = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'payments': [PaymentModule.to_dict(payment) for payment in payments.items],
            'pagination': {
                'page': payments.page,
                'per_page': payments.per_page,
                'total': payments.total,
                'pages': payments.pages,
                'has_next': payments.has_next,
                'has_prev': payments.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get payment history', 'details': str(e)}), 500

@bp.route('/<int:payment_id>', methods=['GET'])
@jwt_required()
def get_payment(payment_id):
    """Get specific payment details"""
    try:
        current_user_id = get_jwt_identity()
        user = UserModule.find_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        payment = PaymentModule.find_by_id(payment_id)
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        # Check if user owns the payment
        if payment.user_id != current_user_id and not UserModule.is_admin(user):
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'payment': PaymentModule.to_dict(payment)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get payment details', 'details': str(e)}), 500

@bp.route('/methods', methods=['GET'])
@jwt_required()
def get_payment_methods():
    """Get available payment methods"""
    try:
        # ✅ UPDATED: Dashboard payment methods
        methods = [
            {
                'id': 'mpesa',
                'name': 'M-Pesa',
                'type': 'mobile_money',
                'icon': '📱',
                'enabled': True,
                'description': 'Pay with M-Pesa mobile money'
            },
            {
                'id': 'card',
                'name': 'Card Payment',
                'type': 'card',
                'icon': '💳',
                'enabled': True,
                'description': 'Pay with Credit/Debit Card'
            }
        ]
        
        return jsonify({'methods': methods}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get payment methods', 'details': str(e)}), 500

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_payment_stats():
    """Get payment statistics"""
    try:
        current_user_id = get_jwt_identity()
        user = UserModule.find_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's payment statistics
        user_payments = PaymentModule.find_by_user_id(current_user_id)
        
        total_payments = len(user_payments)
        completed_payments = len([p for p in user_payments if PaymentModule.is_completed(p)])
        failed_payments = len([p for p in user_payments if PaymentModule.is_failed(p)])
        refunded_payments = len([p for p in user_payments if PaymentModule.is_refunded(p)])
        
        # ✅ ADDED: Separate deposit and balance payments
        deposit_payments = len([p for p in user_payments if p.payment_type == 'deposit' and PaymentModule.is_completed(p)])
        balance_payments = len([p for p in user_payments if p.payment_type == 'balance' and PaymentModule.is_completed(p)])
        
        total_spent = sum([p.amount for p in user_payments if PaymentModule.is_completed(p)])
        
        stats = {
            'total_payments': total_payments,
            'completed_payments': completed_payments,
            'failed_payments': failed_payments,
            'refunded_payments': refunded_payments,
            'deposit_payments': deposit_payments,  # ✅ ADDED
            'balance_payments': balance_payments,  # ✅ ADDED
            'total_spent': total_spent,
            'success_rate': (completed_payments / max(total_payments, 1)) * 100
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get payment stats', 'details': str(e)}), 500

# ✅ ADDED: Webhook endpoint for payment gateway callbacks
@bp.route('/webhook', methods=['POST'])
def payment_webhook():
    """Handle payment gateway webhooks (M-Pesa, Card processor, etc.)"""
    try:
        data = request.get_json()
        
        # TODO: Implement actual webhook handling
        # - Verify webhook signature
        # - Extract transaction details
        # - Update payment status
        # - Send notifications
        
        return jsonify({'message': 'Webhook received'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Webhook processing failed', 'details': str(e)}), 500