# app.py - Main Flask application
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config
import os
import sys
from pathlib import Path

# Add current directory to path
CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def create_app(config_name=None):
    """Application factory pattern"""
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    
    # Configure CORS
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
    
    # Import models (important for migrations)
    with app.app_context():
        from models.user import User
        from models.staff import Staff
        from models.project import Project
        from models.payment import Payment
        from models.research_field import ResearchField
    
    # Register blueprints/routes
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        """Health check endpoint"""
        try:
            # Test database connection
            db.session.execute(db.text('SELECT 1'))
            db_status = 'connected'
        except Exception as e:
            db_status = f'error: {str(e)}'
        
        return jsonify({
            'status': 'healthy',
            'version': '1.0.0',
            'database': db_status
        })
    
    @app.route('/api')
    def api_root():
        """Root API endpoint"""
        return jsonify({
            'message': 'Research Platform API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/api/health',
                'auth': '/api/auth',
                'users': '/api/users',
                'staff': '/api/staff',
                'projects': '/api/projects',
                'payments': '/api/payments'
            }
        })
    
    @app.route('/api/models')
    def list_models():
        """List all database models"""
        models = []
        for table in db.metadata.tables.values():
            models.append({
                'name': table.name,
                'columns': [col.name for col in table.columns]
            })
        return jsonify({'models': models})
    
    return app


def register_blueprints(app):
    """Register Flask blueprints"""
    
    # Import and register auth blueprint
    from routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    # Add other blueprints as you create them
    # from routes.users import bp as users_bp
    # from routes.projects import bp as projects_bp
    # app.register_blueprint(users_bp)
    # app.register_blueprint(projects_bp)


def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400