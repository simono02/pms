# Unified WSGI for Project Management System
import os
import sys
from pathlib import Path

# Add current directory to Python path
CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))

from app import create_app, db
from flask import send_from_directory, render_template_string

# Create the Flask application
app = create_app(os.getenv('FLASK_ENV', 'development'))

# Set Flask static folder to React build's static directory
app.static_folder = str(CURRENT_DIR / 'static' / 'public' / 'static')
app.static_url_path = '/static'

# Serve React frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve React frontend for non-API routes"""
    # If it's an API route, let Flask handle it
    if path.startswith('api/'):
        return None
    
    # Serve index.html for all other routes (React Router)
    index_file = CURRENT_DIR / 'static' / 'public' / 'index.html'
    if index_file.exists():
        return send_from_directory(str(CURRENT_DIR / 'static' / 'public'), 'index.html')
    
    # Fallback message if frontend not built
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Project Management System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
            .container { max-width: 600px; margin: 0 auto; }
            .api-info { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }
            .endpoint { background: #e3f2fd; padding: 10px; margin: 5px 0; border-radius: 4px; font-family: monospace; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Project Management System</h1>
            <p>Backend API is running! Frontend needs to be built.</p>
            
            <div class="api-info">
                <h3>📡 Available API Endpoints:</h3>
                <div class="endpoint">GET /api/health - Health Check</div>
                <div class="endpoint">GET /api - API Root</div>
                <div class="endpoint">GET /api/models - Database Models</div>
            </div>
            
            <h3>🔧 To build the frontend:</h3>
            <p>Run: <code>npm install && npm run build</code></p>
            <p>Then the React app will be served here.</p>
        </div>
    </body>
    </html>
    ''')

@app.shell_context_processor
def make_shell_context():
    """Make database available in Flask shell"""
    return {'db': db}

if __name__ == "__main__":
    print("\n🚀 Project Management System Starting...")
    print("📡 Backend API: http://localhost:5000/api")
    print("🌐 Frontend: http://localhost:5000")
    print("\n Press CTRL+C to stop the server\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
