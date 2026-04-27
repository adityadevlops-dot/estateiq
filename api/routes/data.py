"""
Data API Route

GET /api/data endpoint for accessing predictions and aggregated statistics.
Power BI-compatible endpoints for DirectQuery integration.
"""

import logging
import os
import json
import pandas as pd
from flask import Blueprint, request, jsonify
from config import PATHS

logger = logging.getLogger(__name__)

data_bp = Blueprint('data', __name__, url_prefix='/api')

# Cache predictions in memory for performance
_predictions_cache = None
_cache_timestamp = None


def get_predictions_df():
    """
    Load predictions from CSV with caching.
    
    Returns:
        pd.DataFrame: Predictions dataframe
    """
    global _predictions_cache, _cache_timestamp
    
    if _predictions_cache is not None:
        return _predictions_cache
    
    if not os.path.exists(PATHS['predictions_output']):
        logger.warning("Predictions file not found")
        return None
    
    try:
        _predictions_cache = pd.read_csv(PATHS['predictions_output'])
        logger.info(f"Predictions loaded: {len(_predictions_cache)} rows")
        return _predictions_cache
    except Exception as e:
        logger.error(f"Error loading predictions: {str(e)}")
        return None


@data_bp.route('/data', methods=['GET'])
def get_data():
    """
    Get prediction records with optional filtering and pagination.
    
    Query Parameters:
        location (str): Filter by location
        min_price (float): Minimum actual price filter
        max_price (float): Maximum actual price filter
        page (int): Page number (default 1)
        per_page (int): Records per page (default 50)
    
    Returns:
        JSON with records array and pagination metadata
    """
    try:
        # Load predictions
        df = get_predictions_df()
        if df is None:
            return jsonify({
                "success": False,
                "error": "Predictions not available. Run train.py first."
            }), 503
        
        # Apply filters
        location_filter = request.args.get('location')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        
        if location_filter:
            df = df[df['location'] == location_filter]
        
        if min_price is not None:
            df = df[df['actual_price'] >= min_price]
        
        if max_price is not None:
            df = df[df['actual_price'] <= max_price]
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        total_records = len(df)
        df_page = df.iloc[start_idx:end_idx]
        
        # Convert to list of dicts (Power BI compatible - flat structure)
        records = df_page.to_dict(orient='records')
        
        response = {
            "success": True,
            "data": records,
            "pagination": {
                "current_page": page,
                "per_page": per_page,
                "total_records": total_records,
                "total_pages": (total_records + per_page - 1) // per_page
            }
        }
        
        logger.info(f"Data retrieved: page {page}, {len(records)} records")
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error retrieving data: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to retrieve data"
        }), 500


@data_bp.route('/data/summary', methods=['GET'])
def get_data_summary():
    """
    Get aggregated statistics for Power BI DirectQuery.
    
    Returns flat JSON arrays only (no nesting) for Power BI compatibility.
    Includes average price by location, error statistics, and accuracy metrics.
    
    Returns:
        JSON with flat arrays of summary statistics
    """
    try:
        df = get_predictions_df()
        if df is None:
            return jsonify({
                "success": False,
                "error": "Predictions not available. Run train.py first."
            }), 503
        
        # Summary by location
        by_location = df.groupby('location').agg({
            'property_id': 'count',
            'actual_price': ['mean', 'min', 'max'],
            'predicted_price': 'mean',
            'absolute_error': 'mean',
            'percentage_error': 'mean',
            'within_10pct': 'mean'
        }).reset_index()
        
        # Flatten column names
        by_location.columns = ['location', 'count', 'avg_actual_price', 'min_price', 'max_price',
                               'avg_predicted_price', 'avg_error', 'avg_error_pct', 'accuracy_rate']
        
        # Overall statistics
        total_predictions = len(df)
        avg_actual_price = float(df['actual_price'].mean())
        avg_predicted_price = float(df['predicted_price'].mean())
        avg_error = float(df['absolute_error'].mean())
        avg_error_pct = float(df['percentage_error'].mean())
        accuracy_rate = float(df['within_10pct'].mean())
        
        response = {
            "success": True,
            "data": {
                "overall": {
                    "total_predictions": total_predictions,
                    "avg_actual_price": avg_actual_price,
                    "avg_predicted_price": avg_predicted_price,
                    "avg_absolute_error": avg_error,
                    "avg_error_percentage": avg_error_pct,
                    "accuracy_rate_10pct": accuracy_rate
                },
                "by_location": by_location.to_dict(orient='records')
            }
        }
        
        logger.info(f"Summary retrieved: {total_predictions} predictions, {accuracy_rate*100:.1f}% accuracy")
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error retrieving summary: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to retrieve summary"
        }), 500


@data_bp.route('/data/schema', methods=['GET'])
def get_data_schema():
    """
    Get schema information for Power BI DirectQuery connector.
    
    Returns column names and types in Power BI-compatible format.
    
    Returns:
        JSON with column definitions
    """
    try:
        schema = {
            "success": True,
            "data": {
                "columns": [
                    {"name": "property_id", "type": "Int64"},
                    {"name": "location", "type": "Text"},
                    {"name": "area_sqft", "type": "Decimal.Type"},
                    {"name": "bedrooms", "type": "Int64"},
                    {"name": "actual_price", "type": "Decimal.Type"},
                    {"name": "predicted_price", "type": "Decimal.Type"},
                    {"name": "absolute_error", "type": "Decimal.Type"},
                    {"name": "percentage_error", "type": "Decimal.Type"},
                    {"name": "within_10pct", "type": "Int64"},
                    {"name": "price_band", "type": "Text"}
                ]
            }
        }
        
        logger.info("Schema retrieved")
        return jsonify(schema), 200
    
    except Exception as e:
        logger.error(f"Error retrieving schema: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to retrieve schema"
        }), 500
