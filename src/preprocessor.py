"""
Data Preprocessing Module

Handles missing value imputation, outlier removal, categorical encoding, and feature scaling.
"""

import logging
import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder, OrdinalEncoder

logger = logging.getLogger(__name__)


class Preprocessor:
    """
    Preprocesses raw housing data for model training.
    
    Handles missing values, outlier removal, categorical encoding, and scaling.
    
    Attributes:
        location_encoder (LabelEncoder): Encoder for location column
        furnishing_encoder (OrdinalEncoder): Encoder for furnishing column
        scaler (StandardScaler): Scaler for numeric features
    """
    
    def __init__(self):
        """Initialize preprocessor with empty encoders and scaler."""
        self.location_encoder = None
        self.furnishing_encoder = None
        self.scaler = None
        logger.info("Preprocessor initialized")
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values by filling with median (numeric) or mode (categorical).
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            pd.DataFrame: Dataframe with missing values handled
        """
        logger.info("Handling missing values...")
        df = df.copy()
        
        # Track null counts
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            logger.info(f"Found null values:\n{null_counts[null_counts > 0]}")
        else:
            logger.info("No missing values found")
            return df
        
        # Fill numeric columns with median
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().any():
                median_val = df[col].median()
                df[col].fillna(median_val, inplace=True)
                logger.info(f"Filled {col} with median: {median_val}")
        
        # Fill categorical columns with mode
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if df[col].isnull().any():
                mode_val = df[col].mode()[0] if not df[col].mode().empty else "Unknown"
                df[col].fillna(mode_val, inplace=True)
                logger.info(f"Filled {col} with mode: {mode_val}")
        
        logger.info("Missing value handling completed")
        return df
    
    def remove_outliers(self, df: pd.DataFrame, column: str = 'price') -> pd.DataFrame:
        """
        Remove outliers using Interquartile Range (IQR) method.
        
        Removes rows where value < Q1 - 1.5*IQR or > Q3 + 1.5*IQR
        
        Args:
            df (pd.DataFrame): Input dataframe
            column (str): Column to apply outlier detection on. Default: 'price'
            
        Returns:
            pd.DataFrame: Dataframe with outliers removed
        """
        logger.info(f"Removing outliers from {column} using IQR method...")
        df = df.copy()
        
        initial_count = len(df)
        
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Remove outliers
        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
        
        removed_count = initial_count - len(df)
        logger.info(f"Removed {removed_count} outliers from {column}")
        logger.info(f"Bounds: [{lower_bound:,.0f}, {upper_bound:,.0f}]")
        logger.info(f"Remaining rows: {len(df)}")
        
        return df
    
    def encode_categoricals(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """
        Encode categorical columns: location and furnishing.
        
        location: LabelEncoder (0 to n_classes-1)
        furnishing: OrdinalEncoder with order ['Unfurnished', 'Semi-Furnished', 'Fully Furnished'] → [0, 1, 2]
        
        Args:
            df (pd.DataFrame): Input dataframe
            fit (bool): Whether to fit encoders (True for training, False for inference)
            
        Returns:
            pd.DataFrame: Dataframe with encoded categorical columns
        """
        logger.info(f"Encoding categoricals (fit={fit})...")
        df = df.copy()
        
        # Encode location with LabelEncoder
        if fit:
            self.location_encoder = LabelEncoder()
            df['location_encoded'] = self.location_encoder.fit_transform(df['location'])
            logger.info(f"Location LabelEncoder fitted with classes: {self.location_encoder.classes_.tolist()}")
        else:
            df['location_encoded'] = self.location_encoder.transform(df['location'])
            logger.info("Location encoded using saved LabelEncoder")
        
        # Encode furnishing with OrdinalEncoder
        furnishing_categories = [['Unfurnished', 'Semi-Furnished', 'Fully Furnished']]
        if fit:
            self.furnishing_encoder = OrdinalEncoder(categories=furnishing_categories, dtype=int)
            df['furnishing_encoded'] = self.furnishing_encoder.fit_transform(df[['furnishing']])
            logger.info("Furnishing OrdinalEncoder fitted: Unfurnished=0, Semi-Furnished=1, Fully Furnished=2")
        else:
            df['furnishing_encoded'] = self.furnishing_encoder.transform(df[['furnishing']])
            logger.info("Furnishing encoded using saved OrdinalEncoder")
        
        # Drop original categorical columns
        df.drop(['location', 'furnishing'], axis=1, inplace=True)
        
        logger.info("Categorical encoding completed")
        return df
    
    def scale_features(self, X: pd.DataFrame, fit: bool = True) -> np.ndarray:
        """
        Scale numeric features using StandardScaler.
        
        Scales: area_sqft, age_years, floor
        
        Args:
            X (pd.DataFrame): Input feature dataframe
            fit (bool): Whether to fit scaler (True for training, False for inference)
            
        Returns:
            np.ndarray: Scaled features
        """
        logger.info(f"Scaling features (fit={fit})...")
        X = X.copy()
        
        # Columns to scale
        scale_columns = ['area_sqft', 'age_years', 'floor']
        
        if fit:
            self.scaler = StandardScaler()
            X[scale_columns] = self.scaler.fit_transform(X[scale_columns])
            logger.info(f"StandardScaler fitted on columns: {scale_columns}")
        else:
            X[scale_columns] = self.scaler.transform(X[scale_columns])
            logger.info(f"Features scaled using saved StandardScaler")
        
        logger.info("Feature scaling completed")
        return X.values
    
    def save_encoders(self, path: str):
        """
        Save encoders and scaler to disk using pickle.
        
        Args:
            path (str): Path to save encoders pickle file
        """
        try:
            encoders_dict = {
                'location_encoder': self.location_encoder,
                'furnishing_encoder': self.furnishing_encoder,
                'scaler': self.scaler
            }
            
            with open(path, 'wb') as f:
                pickle.dump(encoders_dict, f)
            
            logger.info(f"Encoders and scaler saved to {path}")
        except Exception as e:
            logger.error(f"Error saving encoders: {str(e)}")
            raise
    
    def load_encoders(self, path: str):
        """
        Load encoders and scaler from disk using pickle.
        
        Args:
            path (str): Path to load encoders pickle file
        """
        try:
            with open(path, 'rb') as f:
                encoders_dict = pickle.load(f)
            
            self.location_encoder = encoders_dict['location_encoder']
            self.furnishing_encoder = encoders_dict['furnishing_encoder']
            self.scaler = encoders_dict['scaler']
            
            logger.info(f"Encoders and scaler loaded from {path}")
        except Exception as e:
            logger.error(f"Error loading encoders: {str(e)}")
            raise
    
    def get_feature_columns(self) -> list:
        """
        Get ordered list of feature column names after preprocessing.
        
        Returns:
            list: Feature column names
        """
        from config import FEATURE_COLUMNS
        return FEATURE_COLUMNS
