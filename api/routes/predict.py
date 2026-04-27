"""
Prediction API Route

POST /api/predict endpoint for making price predictions.
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from api.schemas import PredictInputSchema

logger = logging.getLogger(__name__)

predict_bp = Blueprint('predict', __name__, url_prefix='/api')


@predict_bp.route('/predict', methods=['POST'])
def predict():
    """
    Make a price prediction for given housing inputs.
    
    Request JSON:
        {
            "area_sqft": float,
            "location": str,
            "bedrooms": int,
            "bathrooms": int,
            "age_years": int,
            "floor": int (optional),
            "furnishing": str (optional),
            "parking": int (optional)
        }
    
    Returns:
        JSON with predicted price, confidence range, and feature importances
    """
    try:
        # Parse JSON
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "errors": ["Request body must be valid JSON"]
            }), 400
        
        # Validate input
        cleaned_data, errors = PredictInputSchema.validate(data)
        
        if errors:
            logger.warning(f"Validation failed: {errors}")
            return jsonify({
                "success": False,
                "errors": errors
            }), 400
        
        # Make prediction
        from src.predictor import Predictor
        try:
            predictor = Predictor()
            prediction = predictor.predict(cleaned_data)
        except FileNotFoundError as e:
            logger.error(f"Model not found: {str(e)}")
            return jsonify({
                "success": False,
                "error": "Model not trained yet. Run train.py first."
            }), 503
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return jsonify({
                "success": False,
                "error": f"Prediction failed: {str(e)}"
            }), 500
        
        # Build response
        response = {
            "success": True,
            "data": {
                "predicted_price": prediction['predicted_price'],
                "predicted_price_formatted": prediction['predicted_price_formatted'],
                "predicted_price_crore": prediction['predicted_price_crore'],
                "confidence_range": prediction['confidence_range'],
                "feature_importances": prediction['feature_importances'],
                "input_summary": cleaned_data
            },
            "meta": {
                "model_used": predictor.model_name if hasattr(predictor, 'model_name') else "Unknown",
                "model_accuracy": f"{(predictor.evaluations[0]['r2'] * 100):.1f}%" if predictor.evaluations else "N/A",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
        
        logger.info(f"Prediction successful: ₹{prediction['predicted_price']:,.0f}")
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Unhandled error in /predict: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500
