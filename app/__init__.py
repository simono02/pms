from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import sys
from pathlib import Path

# Ensure backend directory is on path
BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from config import config

# ── Extensions (initialised without app — bound in create_app) ────────
db      = SQLAlchemy()
migrate = Migrate()
jwt     = JWTManager()
mail    = Mail()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
)


def create_app(config_name: str = None) -> Flask:
    """Application factory."""

    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # ── Bind extensions ───────────────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)

    # ── CORS ──────────────────────────────────────────────────────────
    CORS(
        app,
        origins=app.config.get('CORS_ORIGINS', ['http://localhost:3000', 'http://localhost:5000', 'http://localhost:8080']),
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )
    
    # Handle preflight requests
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = app.make_default_options_response()
            response.headers.add_header("Access-Control-Allow-Origin", request.headers.get("Origin"))
            response.headers.add_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
            response.headers.add_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            response.headers.add_header("Access-Control-Allow-Credentials", "true")
            return response

    # ── Import models so Flask-Migrate can detect them ────────────────
    with app.app_context():
        from app.models.user import User               # noqa: F401
        from app.models.staff import Staff             # noqa: F401
        from app.models.project import Project         # noqa: F401
        from app.models.payment import Payment         # noqa: F401
        from app.models.research_field import ResearchField  # noqa: F401

    # ── Blueprints & error handlers ───────────────────────────────────
    _register_blueprints(app)
    _register_error_handlers(app)

    # ── Built-in utility endpoints ────────────────────────────────────
    @app.route('/api/health')
    def health_check():
        try:
            db.session.execute(db.text('SELECT 1'))
            db_status = 'connected'
        except Exception as e:
            db_status = f'error: {e}'
        return jsonify({
            'status':      'healthy',
            'version':     '1.0.0',
            'database':    db_status,
            'environment': config_name,
        })

    @app.route('/api')
    def api_root():
        return jsonify({
            'message': 'Research Platform API',
            'version': '1.0.0',
            'status':  'running',
            'endpoints': {
                'health':          '/api/health',
                'auth':            '/api/auth',
                'admin':           '/api/admin',
                'staff':           '/api/staff',
                'user':            '/api/user',
                'projects':        '/api/projects',
                'payments':        '/api/payments',
                'research_fields': '/api/research-fields',
            },
        })

    @app.route('/api/models')
    def list_models():
        return jsonify({
            'models': [
                {'name': t.name, 'columns': [c.name for c in t.columns]}
                for t in db.metadata.tables.values()
            ]
        })

    return app


# ── Private helpers ────────────────────────────────────────────────────

def _register_blueprints(app: Flask) -> None:
    from app.routes.auth_routes import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.admin_routes import bp as admin_bp
    app.register_blueprint(admin_bp)

    from app.routes.staff_routes import bp as staff_bp
    app.register_blueprint(staff_bp)

    # ── Previously missing blueprints ─────────────────────────────────
    from app.routes.user_routes import bp as user_bp
    app.register_blueprint(user_bp)

    from app.routes.project_routes import bp as projects_bp
    app.register_blueprint(projects_bp)

    from app.routes.payment_routes import bp as payments_bp
    app.register_blueprint(payments_bp)


def _register_error_handlers(app: Flask) -> None:

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': 'Bad request', 'details': str(e)}), 400

    @app.errorhandler(401)
    def unauthorised(e):
        return jsonify({'error': 'Unauthorised'}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({'error': 'Forbidden'}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(422)
    def unprocessable(e):
        import traceback
        print("=== 422 ERROR ===")
        print(str(e))
        print(getattr(e, 'description', ''))
        print(traceback.format_exc())
        return jsonify({'error': str(e), 'description': str(getattr(e, 'description', ''))}), 422

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500