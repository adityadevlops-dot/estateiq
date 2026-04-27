"""
Prediction Module

Loads trained models and makes predictions on new inputs.
"""

import os
import logging
import numpy as np
import pandas as pd
from config import PATHS, FEATURE_COLUMNS, VALID_LOCATIONS, VALID_FURNISHING
from src.preprocessor import Preprocessor
from src.feature_engineer import FeatureEngineer
from src.model_trainer import ModelTrainer

logger = logging.getLogger(__name__)


class Predictor:
    """
    Makes predictions on new housing data using trained model.
    
    Loads model, encoders, and performs end-to-end preprocessing and inference.
    
    Attributes:
        model: Trained model instance
        preprocessor (Preprocessor): Preprocessor with fitted encoders
        feature_engineer (FeatureEngineer): Feature engineer instance
        feature_names (list): Feature column names
        model_name (str): Name of the best model
        evaluations (list): Evaluation metrics from training
    """
    
    def __init__(self):
        """
        Initialize Predictor by loading model and encoders from disk.
        
        Raises:
            FileNotFoundError: If model or encoder files don't exist
        """
        logger.info("Initializing Predictor...")
        
        # Check if model exists
        if not os.path.exists(PATHS['best_model']):
            logger.error("Model not found. Run train.py first.")
            raise FileNotFoundError(f"Model not found at {PATHS['best_model']}")
        
        # Load model
        model_trainer = ModelTrainer({})
        self.model = model_trainer.load_model(PATHS['best_model'])
        
        # Load encoders
        self.preprocessor = Preprocessor()
        self.preprocessor.load_encoders(PATHS['encoders'])
        
        # Initialize feature engineer
        self.feature_engineer = FeatureEngineer()
        
        # Get feature names
        self.feature_names = FEATURE_COLUMNS
        
        # Load evaluations
        try:
            import json
            with open(PATHS['evaluation_report'], 'r') as f:
                self.evaluations = json.load(f)
            # Find best model name
            self.model_name = max(self.evaluations, key=lambda x: x['r2'])['model_name']
        except Exception as e:
            logger.warning(f"Could not load evaluation report: {str(e)}")
            self.model_name = "Unknown"
            self.evaluations = []
        
        logger.info(f"Predictor initialized with model: {self.model_name}")
    
    def preprocess_input(self, input_dict: dict) -> np.ndarray:
        """
        Preprocess raw input and return model-ready feature array.
        
        Args:
            input_dict (dict): Raw input with keys like area_sqft, location, bedrooms, etc.
            
        Returns:
            np.ndarray: Preprocessed features of shape (1, n_features)
            
        Raises:
            ValueError: If input validation fails
        """
        logger.info("Preprocessing input...")
        
        # Validate required keys
        required_keys = ['area_sqft', 'location', 'bedrooms', 'bathrooms', 'age_years']
        missing_keys = set(required_keys) - set(input_dict.keys())
        if missing_keys:
            raise ValueError(f"Missing required keys: {missing_keys}")
        
        # Validate location
        if input_dict['location'] not in VALID_LOCATIONS:
            raise ValueError(f"Invalid location. Must be one of: {VALID_LOCATIONS}")
        
        # Validate furnishing
        furnishing = input_dict.get('furnishing', 'Unfurnished')
        if furnishing not in VALID_FURNISHING:
            raise ValueError(f"Invalid furnishing. Must be one of: {VALID_FURNISHING}")
        
        # Create dataframe
        df = pd.DataFrame([input_dict])
        
        # Fill optional fields with defaults
        df['floor'] = df.get('floor', 0) if 'floor' in df.columns else 0
        df['furnishing'] = df.get('furnishing', 'Unfurnished') if 'furnishing' in df.columns else 'Unfurnished'
        df['parking'] = df.get('parking', 0) if 'parking' in df.columns else 0
        
        # Encode categoricals (fit=False, use saved encoders)
        df = self.preprocessor.encode_categoricals(df, fit=False)
        
        # Feature engineering (is_training=False, don't use price-based features)
        df = self.feature_engineer.run_all(df, is_training=False)
        
        # Select features in correct order
        X = df[self.feature_names].values
        
        # Scale features (fit=False, use saved scaler)
        X_scaled = self.preprocessor.scale_features(pd.DataFrame(X, columns=self.feature_names), fit=False)
        
        logger.info(f"Input preprocessed. Shape: {X_scaled.shape}")
        return X_scaled
    
    def predict(self, input_dict: dict) -> dict:
        """
        Make prediction on input and return comprehensive result.
        
        Args:
            input_dict (dict): Raw input data
            
        Returns:
            dict: Prediction result with formatted prices, confidence range, and feature importances
        """
        logger.info("Making prediction...")
        
        try:
            # Preprocess input
            X_preprocessed = self.preprocess_input(input_dict)
            
            # Make prediction (on log scale)
            y_pred_log = self.model.predict(X_preprocessed)[0]
            
            # Inverse log transform
            predicted_price = np.expm1(y_pred_log)
            
            # Ensure positive price
            predicted_price = max(predicted_price, 500000)
            
            logger.info(f"Predicted price: ₹{predicted_price:,.0f}")
            
            # Format currency
            formatted_price = self.format_indian_currency(predicted_price)
            crore_price = f"{predicted_price / 1e7:.2f} Cr"
            
            # Confidence range (±12%)
            confidence_low = predicted_price * 0.88
            confidence_high = predicted_price * 1.12
            
            # Get feature importances
            if self.evaluations and hasattr(self.model, 'feature_importances_'):
                # Extract importances for tree-based models
                importances = self.model.feature_importances_
                feature_importances = {name: float(imp) for name, imp in zip(self.feature_names, importances)}
                feature_importances = dict(sorted(feature_importances.items(), key=lambda x: x[1], reverse=True))
            else:
                feature_importances = {}
            
            # Build result
            result = {
                "predicted_price": float(predicted_price),
                "predicted_price_formatted": formatted_price,
                "predicted_price_crore": crore_price,
                "confidence_range": {
                    "low": float(confidence_low),
                    "high": float(confidence_high)
                },
                "feature_importances": feature_importances
            }
            
            logger.info("Prediction completed successfully")
            return result
        
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise
    
    def format_indian_currency(self, amount: float) -> str:
        """
        Format amount in Indian currency style (lakhs/crores).
        
        Example: 14200000 → "₹ 1,42,00,000"
        
        Args:
            amount (float): Amount in rupees
            
        Returns:
            str: Formatted currency string
        """
        def add_commas(n):
            """Add commas in Indian style (lakhs/crores)."""
            s = str(int(n))
            if len(s) <= 3:
                return s
            
            # Reverse the string
            s_rev = s[::-1]
            
            # Add commas from right: 2 digits, then 2 digits for every group
            parts = []
            parts.append(s_rev[:2])  # Last 2 digits (ones and tens)
            
            for i in range(2, len(s_rev), 2):
                parts.append(s_rev[i:i+2])
            
            # Reverse back
            formatted = ','.join(parts[::-1])
            return formatted
        
        formatted = add_commas(amount)
        return f"₹ {formatted}"
