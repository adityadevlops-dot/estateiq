"""
Metrics API Route

GET /api/metrics endpoint for model performance metrics.
"""

import logging
import json
import os
from flask import Blueprint, jsonify
from config import PATHS

logger = logging.getLogger(__name__)

metrics_bp = Blueprint('metrics', __name__, url_prefix='/api')


@metrics_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """
    Get model training metrics and performance statistics.
    
    Returns:
        JSON with best model info, all model metrics, and training statistics
    """
    try:
        # Load evaluation report
        if not os.path.exists(PATHS['evaluation_report']):
            logger.warning("Evaluation report not found")
            return jsonify({
                "success": False,
                "error": "Model metrics not available. Run train.py first."
            }), 503
        
        with open(PATHS['evaluation_report'], 'r') as f:
            evaluations = json.load(f)
        
        # Find best model
        best_model = max(evaluations, key=lambda x: x['r2'])
        
        # Calculate training statistics
        num_models = len(evaluations)
        num_test_samples = 1000  # 20% of 5000
        num_train_samples = 4000  # 80% of 5000
        num_features = 13  # From config.FEATURE_COLUMNS
        
        # Build response
        response = {
            "success": True,
            "data": {
                "best_model": best_model['model_name'],
                "model_r2_score": best_model['r2'],
                "model_mae": best_model['mae'],
                "model_rmse": best_model['rmse'],
                "model_mape": best_model['mape'],
                "metrics": {
                    "r2": best_model['r2'],
                    "mae": best_model['mae'],
                    "rmse": best_model['rmse'],
                    "mape": best_model['mape']
                },
                "all_models": evaluations,
                "training_samples": num_train_samples,
                "test_samples": num_test_samples,
                "feature_count": num_features
            }
        }
        
        logger.info(f"Metrics retrieved. Best model: {best_model['model_name']} (R²: {best_model['r2']:.4f})")
        return jsonify(response), 200
    
    except json.JSONDecodeError:
        logger.error("Invalid evaluation report JSON")
        return jsonify({
            "success": False,
            "error": "Invalid evaluation report"
        }), 500
    
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to retrieve metrics"
        }), 500
