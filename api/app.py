"""
Flask Application Initialization

Sets up Flask app, registers blueprints, configures CORS, middleware, and error handlers.
"""

import logging
import time
import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import setup_logging
from api.models import db

# Configure logging
logger = setup_logging()


def create_app():
    """
    Create and configure Flask application.
    
    Returns:
        Flask: Configured Flask app instance
    """
    app = Flask(__name__)
    
    logger.info("Creating Flask application...")
    
    # ========================================================================
    # DATABASE Configuration
    # ========================================================================
    database_path = os.path.join(os.path.dirname(__file__), '..', 'estateiq.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    logger.info("Database configured")
    
    # ========================================================================
    # JWT Configuration
    # ========================================================================
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'estateiq-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
    
    jwt = JWTManager(app)
    logger.info("JWT configured")
    
    # ========================================================================
    # CORS Configuration
    # ========================================================================
    CORS(app)
    logger.info("CORS enabled")
    
    # ========================================================================
    # Register Blueprints
    # ========================================================================
    from api.routes.predict import predict_bp
    from api.routes.metrics import metrics_bp
    from api.routes.data import data_bp
    from api.routes.auth import auth_bp
    
    app.register_blueprint(predict_bp)
    app.register_blueprint(metrics_bp)
    app.register_blueprint(data_bp)
    app.register_blueprint(auth_bp)
    
    logger.info("All blueprints registered")
    
    # ========================================================================
    # Database Initialization
    # ========================================================================
    with app.app_context():
        db.create_all()
        logger.info("Database tables created/verified")
    
    # ========================================================================
    # Request Logging Middleware
    # ========================================================================
    @app.before_request
    def log_request_start():
        """Log incoming request details."""
        request.start_time = time.time()
    
    @app.after_request
    def log_request_end(response):
        """Log response details and request duration."""
        duration_ms = (time.time() - request.start_time) * 1000
        
        logger.info(
            f"[{datetime.utcnow().isoformat()}] "
            f"{request.method} {request.path} - "
            f"Status: {response.status_code}, "
            f"Duration: {duration_ms:.2f}ms"
        )
        
        return response
    
    # ========================================================================
    # Global Error Handlers
    # ========================================================================
    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle 400 Bad Request errors."""
        logger.warning(f"Bad request: {str(error)}")
        return jsonify({
            "success": False,
            "error": "Bad request",
            "status": 400
        }), 400
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 Not Found errors."""
        logger.warning(f"Not found: {request.path}")
        return jsonify({
            "success": False,
            "error": "Endpoint not found",
            "status": 404
        }), 404
    
    @app.errorhandler(500)
    def handle_server_error(error):
        """Handle 500 Internal Server errors."""
        logger.error(f"Server error: {str(error)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "status": 500
        }), 500
    
    # ========================================================================
    # JWT Error Handlers
    # ========================================================================
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Handle expired JWT tokens"""
        return jsonify({
            "success": False,
            "error": "Token has expired",
            "status": 401
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Handle invalid JWT tokens"""
        return jsonify({
            "success": False,
            "error": "Invalid token",
            "status": 401
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Handle missing JWT tokens"""
        return jsonify({
            "success": False,
            "error": "Authorization token missing",
            "status": 401
        }), 401
    
    # ========================================================================
    # Health Check Endpoint
    # ========================================================================
    @app.route('/health', methods=['GET'])
    def health_check():
        """
        Health check endpoint.
        
        Returns:
            JSON with status information
        """
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), 200
    
    logger.info("Flask app created successfully")
    return app


if __name__ == '__main__':
    app = create_app()
    from config import API_CONFIG
    app.run(
        host=API_CONFIG['host'],
        port=API_CONFIG['port'],
        debug=API_CONFIG['debug']
    )
