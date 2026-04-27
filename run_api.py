"""
Flask API Server Entry Point

Starts the House Price Prediction REST API server.

Usage:
    python run_api.py

The API will be available at http://localhost:5000

Endpoints:
    POST /api/predict - Make price predictions
    GET /api/metrics - Get model performance metrics
    GET /api/data - Get prediction data with pagination
    GET /api/data/summary - Get aggregated statistics
    GET /api/data/schema - Get data schema for Power BI
    GET /health - Health check
"""

import logging
from config import setup_logging, API_CONFIG
from api.app import create_app

# Configure logging
logger = setup_logging()


def main():
    """
    Create and run Flask API server.
    """
    logger.info("="*80)
    logger.info("STARTING HOUSE PRICE PREDICTION API")
    logger.info("="*80)
    
    try:
        # Create Flask app
        app = create_app()
        
        logger.info(f"\nAPI Configuration:")
        logger.info(f"  Host: {API_CONFIG['host']}")
        logger.info(f"  Port: {API_CONFIG['port']}")
        logger.info(f"  Debug Mode: {API_CONFIG['debug']}")
        
        logger.info(f"\nStarting server...")
        logger.info(f"API will be available at: http://localhost:{API_CONFIG['port']}")
        logger.info("\nAvailable Endpoints:")
        logger.info("  POST /api/predict - Make predictions")
        logger.info("  GET /api/metrics - Get model metrics")
        logger.info("  GET /api/data - Get prediction data")
        logger.info("  GET /api/data/summary - Get summary statistics")
        logger.info("  GET /api/data/schema - Get schema for Power BI")
        logger.info("  GET /health - Health check")
        logger.info("="*80 + "\n")
        
        # Run server
        app.run(
            host=API_CONFIG['host'],
            port=API_CONFIG['port'],
            debug=API_CONFIG['debug']
        )
    
    except Exception as e:
        logger.error(f"Failed to start API: {str(e)}")
        raise


if __name__ == '__main__':
    main()
