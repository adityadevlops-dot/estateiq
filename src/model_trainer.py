"""
Model Training Module

Trains multiple regression models, evaluates them, and selects the best performer.
"""

import logging
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Trains multiple regression models for price prediction.
    
    Supports: Linear Regression, Random Forest, Gradient Boosting
    
    Attributes:
        config (dict): Model hyperparameters
        models (dict): Trained model instances
        evaluations (list): Evaluation results for all models
    """
    
    def __init__(self, config: dict):
        """
        Initialize ModelTrainer with configuration.
        
        Args:
            config (dict): Dictionary containing model hyperparameters
        """
        self.config = config
        self.models = {}
        self.evaluations = []
        logger.info("ModelTrainer initialized")
    
    def prepare_data(self, df: pd.DataFrame) -> tuple:
        """
        Prepare data for model training.
        
        Separates features and target, applies log transform to target, and splits data.
        
        Args:
            df (pd.DataFrame): Complete dataframe with features and target
            
        Returns:
            tuple: (X_train, X_test, y_train, y_test) as numpy arrays
        """
        logger.info("Preparing data for training...")
        
        from config import FEATURE_COLUMNS
        
        # Separate features and target
        X = df[FEATURE_COLUMNS].values
        y = df['price'].values
        
        # Apply log transform to target for better distribution
        y_log = np.log1p(y)
        
        logger.info(f"Features shape: {X.shape}")
        logger.info(f"Target shape: {y_log.shape}")
        logger.info(f"Price range (original): Rs {y.min():,.0f} - Rs {y.max():,.0f}")
        
        # Train/test split 80/20
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_log, test_size=0.2, random_state=42
        )
        
        logger.info(f"Train set: {X_train.shape[0]} samples")
        logger.info(f"Test set: {X_test.shape[0]} samples")
        
        return X_train, X_test, y_train, y_test
    
    def train_linear_regression(self, X_train: np.ndarray, y_train: np.ndarray) -> LinearRegression:
        """
        Train Linear Regression model.
        
        Args:
            X_train (np.ndarray): Training features
            y_train (np.ndarray): Training target (log-transformed)
            
        Returns:
            LinearRegression: Trained model
        """
        logger.info("Training Linear Regression...")
        model = LinearRegression(fit_intercept=True)
        model.fit(X_train, y_train)
        logger.info("Linear Regression training completed")
        return model
    
    def train_random_forest(self, X_train: np.ndarray, y_train: np.ndarray) -> RandomForestRegressor:
        """
        Train Random Forest Regressor model.
        
        Args:
            X_train (np.ndarray): Training features
            y_train (np.ndarray): Training target (log-transformed)
            
        Returns:
            RandomForestRegressor: Trained model
        """
        logger.info("Training Random Forest Regressor...")
        config = self.config['random_forest']
        model = RandomForestRegressor(**config)
        model.fit(X_train, y_train)
        logger.info("Random Forest training completed")
        return model
    
    def train_gradient_boosting(self, X_train: np.ndarray, y_train: np.ndarray) -> GradientBoostingRegressor:
        """
        Train Gradient Boosting Regressor model.
        
        Args:
            X_train (np.ndarray): Training features
            y_train (np.ndarray): Training target (log-transformed)
            
        Returns:
            GradientBoostingRegressor: Trained model
        """
        logger.info("Training Gradient Boosting Regressor...")
        config = self.config['gradient_boosting']
        model = GradientBoostingRegressor(**config)
        model.fit(X_train, y_train)
        logger.info("Gradient Boosting training completed")
        return model
    
    def evaluate_model(self, model, X_test: np.ndarray, y_test: np.ndarray, model_name: str) -> dict:
        """
        Evaluate model on test set.
        
        Computes R², MAE, RMSE, MAPE metrics on original price scale.
        
        Args:
            model: Trained model instance
            X_test (np.ndarray): Test features
            y_test (np.ndarray): Test target (log-transformed)
            model_name (str): Name of the model
            
        Returns:
            dict: Evaluation metrics including model name and all scores
        """
        logger.info(f"Evaluating {model_name}...")
        
        # Make predictions
        y_pred_log = model.predict(X_test)
        
        # Inverse log transform to get actual prices
        y_pred_actual = np.expm1(y_pred_log)
        y_test_actual = np.expm1(y_test)
        
        # Calculate metrics
        r2 = r2_score(y_test_actual, y_pred_actual)
        mae = mean_absolute_error(y_test_actual, y_pred_actual)
        rmse = np.sqrt(mean_squared_error(y_test_actual, y_pred_actual))
        
        # MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((y_test_actual - y_pred_actual) / y_test_actual)) * 100
        
        # Create evaluation dict
        evaluation = {
            'model_name': model_name,
            'r2': float(r2),
            'mae': float(mae),
            'rmse': float(rmse),
            'mape': float(mape)
        }
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Model: {model_name}")
        logger.info(f"R² Score:     {r2:.4f}")
        logger.info(f"MAE:          Rs {mae:,.0f}")
        logger.info(f"RMSE:         Rs {rmse:,.0f}")
        logger.info(f"MAPE:         {mape:.2f}%")
        logger.info(f"{'='*60}\n")
        
        return evaluation
    
    def select_best_model(self, evaluations: list) -> str:
        """
        Select best model based on R² score.
        
        Args:
            evaluations (list): List of evaluation dictionaries
            
        Returns:
            str: Name of best performing model
        """
        best_model = max(evaluations, key=lambda x: x['r2'])
        best_model_name = best_model['model_name']
        
        logger.info(f"Best model selected: {best_model_name} (R²: {best_model['r2']:.4f})")
        return best_model_name
    
    def get_feature_importances(self, model, feature_names: list) -> dict:
        """
        Extract feature importances from model.
        
        For tree-based models: use feature_importances_
        For linear models: use normalized absolute coefficients
        
        Args:
            model: Trained model instance
            feature_names (list): Feature column names
            
        Returns:
            dict: Feature importances sorted descending
        """
        logger.info("Extracting feature importances...")
        
        if hasattr(model, 'feature_importances_'):
            # Tree-based models
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            # Linear models
            importances = np.abs(model.coef_)
            importances = importances / importances.sum()  # Normalize
        else:
            logger.warning("Model does not support feature importances")
            return {}
        
        # Create importance dictionary
        importance_dict = {name: float(imp) for name, imp in zip(feature_names, importances)}
        
        # Sort by importance descending
        importance_dict = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
        
        logger.info("Top 5 features:")
        for i, (feature, importance) in enumerate(list(importance_dict.items())[:5], 1):
            logger.info(f"  {i}. {feature}: {importance:.4f}")
        
        return importance_dict
    
    def save_model(self, model, path: str):
        """
        Save trained model to disk using joblib.
        
        Args:
            model: Trained model instance
            path (str): Path to save model file
        """
        try:
            joblib.dump(model, path)
            logger.info(f"Model saved to {path}")
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise
    
    def load_model(self, path: str):
        """
        Load trained model from disk using joblib.
        
        Args:
            path (str): Path to load model file
            
        Returns:
            Trained model instance
        """
        try:
            model = joblib.load(path)
            logger.info(f"Model loaded from {path}")
            return model
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def save_evaluation_report(self, evaluations: list, path: str):
        """
        Save evaluation report to JSON file.
        
        Args:
            evaluations (list): List of evaluation dictionaries
            path (str): Path to save report
        """
        try:
            with open(path, 'w') as f:
                json.dump(evaluations, f, indent=2)
            logger.info(f"Evaluation report saved to {path}")
        except Exception as e:
            logger.error(f"Error saving evaluation report: {str(e)}")
            raise
    
    def load_evaluation_report(self, path: str) -> list:
        """
        Load evaluation report from JSON file.
        
        Args:
            path (str): Path to load report
            
        Returns:
            list: Evaluation results
        """
        try:
            with open(path, 'r') as f:
                evaluations = json.load(f)
            logger.info(f"Evaluation report loaded from {path}")
            return evaluations
        except Exception as e:
            logger.error(f"Error loading evaluation report: {str(e)}")
            raise
