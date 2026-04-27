"""
Flask Application Initialization

Sets up Flask app, registers blueprints, configures CORS, middleware, and error handlers.
"""

import logging
import time
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import setup_logging

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
    
    app.register_blueprint(predict_bp)
    app.register_blueprint(metrics_bp)
    app.register_blueprint(data_bp)
    
    logger.info("All blueprints registered")
    
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
