"""
AI Avatar Flask Application

A Flask web application that integrates with Azure AI Services 
to create interactive text-to-speech avatars.
Follows the Technical Design Document specifications exactly.
"""

import os
import logging
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv

from src.auth.auth_manager import is_authenticated

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory pattern"""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configure Flask
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', '1') == '1'
    app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', '0') == '1'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Enable CORS
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5000').split(',')
    CORS(app, origins=cors_origins, supports_credentials=True)
    
    # Register API routes
    from src.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        """Main application page - requires authentication"""
        if not is_authenticated(session):
            return redirect(url_for('login'))
        return render_template('index.html')
    
    @app.route('/login')
    def login():
        """Login page"""
        if is_authenticated(session):
            return redirect(url_for('index'))
        return render_template('login.html')
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy', 
            'service': 'ai-avatar',
            'version': '1.0.0'
        })
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.before_request
    def log_request_info():
        """Log request information for debugging"""
        if app.config['DEBUG']:
            logger.debug(f"Request: {request.method} {request.url}")
    
    return app

if __name__ == '__main__':
    app = create_app()
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    logger.info(f"Starting AI Avatar application on {host}:{port}")
    logger.info(f"Debug mode: {app.config['DEBUG']}")
    app.run(host=host, port=port, debug=app.config['DEBUG'])
