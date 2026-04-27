"""
Configuration module for House Price Prediction backend.
Centralizes all constants, paths, and hyperparameters.
"""

import os
import logging
from datetime import datetime

# ============================================================================
# BASE DIRECTORY AND PATHS
# ============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PATHS = {
    "raw_data": os.path.join(BASE_DIR, "data", "raw", "housing.csv"),
    "processed_data": os.path.join(BASE_DIR, "data", "processed", "cleaned.csv"),
    "predictions_output": os.path.join(BASE_DIR, "data", "outputs", "predictions.csv"),
    "predictions_summary": os.path.join(BASE_DIR, "data", "outputs", "predictions_summary.csv"),
    "model_comparison": os.path.join(BASE_DIR, "data", "outputs", "model_comparison.csv"),
    "best_model": os.path.join(BASE_DIR, "models", "trained", "best_model.pkl"),
    "encoders": os.path.join(BASE_DIR, "models", "trained", "encoders.pkl"),
    "evaluation_report": os.path.join(BASE_DIR, "models", "evaluation", "report.json"),
}

# ============================================================================
# MODEL HYPERPARAMETERS
# ============================================================================
MODEL_CONFIG = {
    "random_forest": {
        "n_estimators": 200,
        "max_depth": 12,
        "min_samples_split": 5,
        "min_samples_leaf": 2,
        "n_jobs": -1,
        "random_state": 42
    },
    "gradient_boosting": {
        "n_estimators": 150,
        "learning_rate": 0.08,
        "max_depth": 5,
        "random_state": 42
    },
    "linear_regression": {
        "fit_intercept": True
    }
}

# ============================================================================
# DATA VALIDATION CONSTANTS
# ============================================================================
VALID_LOCATIONS = ['Mumbai', 'Bangalore', 'Delhi', 'Pune', 'Hyderabad', 'Chennai', 'Kolkata', 'Ahmedabad']
VALID_FURNISHING = ['Unfurnished', 'Semi-Furnished', 'Fully Furnished']

# Price multipliers by location for synthetic data generation
LOCATION_MULTIPLIERS = {
    'Mumbai': 12000,
    'Bangalore': 8500,
    'Delhi': 10000,
    'Pune': 6500,
    'Hyderabad': 6000,
    'Chennai': 5500,
    'Kolkata': 5000,
    'Ahmedabad': 5500
}

# Furnishing premiums for price calculation
FURNISHING_PREMIUMS = {
    'Unfurnished': 0,
    'Semi-Furnished': 250000,
    'Fully Furnished': 600000
}

# Required columns in dataset
REQUIRED_COLUMNS = [
    'area_sqft', 'location', 'bedrooms', 'bathrooms', 
    'age_years', 'floor', 'furnishing', 'parking', 'price'
]

# ============================================================================
# FEATURE ENGINEERING CONSTANTS
# ============================================================================
FEATURE_COLUMNS = [
    'area_sqft', 'bedrooms', 'bathrooms', 'age_years', 'floor', 'parking',
    'location_encoded', 'furnishing_encoded', 'bath_bed_ratio',
    'size_category', 'age_category', 'total_rooms', 'high_floor'
]

# Size category thresholds
SIZE_CATEGORIES = {
    'compact': (0, 600),
    'mid': (600, 1200),
    'large': (1200, 2400),
    'luxury': (2400, float('inf'))
}

# Age category thresholds
AGE_CATEGORIES = {
    'very_old': (30, float('inf')),
    'old': (16, 30),
    'recent': (6, 15),
    'new': (0, 5)
}

# ============================================================================
# API CONFIGURATION
# ============================================================================
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": False
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
def setup_logging():
    """
    Configure logging for the entire application.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    log_format = "[%(asctime)s] %(levelname)s %(name)s — %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.join(BASE_DIR, 'app.log'))
        ]
    )
    return logging.getLogger(__name__)

# ============================================================================
# SYNTHETIC DATA GENERATION CONSTANTS
# ============================================================================
SYNTHETIC_DATA_SIZE = 5000

# Bedroom distribution
BEDROOM_DIST = {
    'values': [1, 2, 3, 4, 5],
    'probabilities': [0.1, 0.35, 0.35, 0.15, 0.05]
}

# Furnishing distribution
FURNISHING_DIST = {
    'values': ['Unfurnished', 'Semi-Furnished', 'Fully Furnished'],
    'probabilities': [0.3, 0.45, 0.25]
}

# ============================================================================
# PRICE RANGE BANDS FOR REPORTING
# ============================================================================
PRICE_BANDS = {
    'less_than_50L': (0, 5000000),
    '50L_to_1Cr': (5000000, 10000000),
    '1Cr_to_2Cr': (10000000, 20000000),
    '2Cr_to_5Cr': (20000000, 50000000),
    '5Cr_plus': (50000000, float('inf'))
}
