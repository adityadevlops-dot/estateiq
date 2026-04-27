"""
Feature Engineering Module

Creates advanced features for improved model performance.
"""

import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Performs feature engineering on housing dataset.
    
    Creates derived features including ratios, categories, and interaction terms.
    """
    
    def __init__(self):
        """Initialize FeatureEngineer."""
        logger.info("FeatureEngineer initialized")
    
    def add_price_per_sqft_estimate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add estimated price per square foot feature.
        
        NOTE: This feature is only used during training pipeline, not during inference.
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            pd.DataFrame: Dataframe with est_ppsf column
        """
        if 'price' in df.columns and 'area_sqft' in df.columns:
            df['est_ppsf'] = df['price'] / df['area_sqft']
            logger.info("Added est_ppsf feature")
        else:
            logger.warning("price or area_sqft column not found; skipping est_ppsf")
        
        return df
    
    def add_room_ratio(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add bathroom to bedroom ratio feature.
        
        Handles division by zero by clipping to [0, 1] range.
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            pd.DataFrame: Dataframe with bath_bed_ratio column
        """
        df['bath_bed_ratio'] = (df['bathrooms'] / df['bedrooms']).clip(0, 1)
        logger.info("Added bath_bed_ratio feature")
        return df
    
    def add_property_size_category(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add property size category based on area_sqft.
        
        Categories:
        - 0: Compact (< 600 sqft)
        - 1: Mid (600-1200 sqft)
        - 2: Large (1200-2400 sqft)
        - 3: Luxury (> 2400 sqft)
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            pd.DataFrame: Dataframe with size_category column
        """
        def categorize_size(area):
            if area < 600:
                return 0
            elif area < 1200:
                return 1
            elif area < 2400:
                return 2
            else:
                return 3
        
        df['size_category'] = df['area_sqft'].apply(categorize_size)
        logger.info("Added size_category feature")
        return df
    
    def add_age_category(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add property age category.
        
        Categories:
        - 3: New (0-5 years)
        - 2: Recent (6-15 years)
        - 1: Old (16-30 years)
        - 0: Very Old (> 30 years)
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            pd.DataFrame: Dataframe with age_category column
        """
        def categorize_age(age):
            if age <= 5:
                return 3
            elif age <= 15:
                return 2
            elif age <= 30:
                return 1
            else:
                return 0
        
        df['age_category'] = df['age_years'].apply(categorize_age)
        logger.info("Added age_category feature")
        return df
    
    def add_total_rooms(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add total rooms feature (bedrooms + bathrooms).
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            pd.DataFrame: Dataframe with total_rooms column
        """
        df['total_rooms'] = df['bedrooms'] + df['bathrooms']
        logger.info("Added total_rooms feature")
        return df
    
    def add_floor_premium_flag(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add high floor flag feature.
        
        high_floor = 1 if floor > 10 else 0
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            pd.DataFrame: Dataframe with high_floor column
        """
        df['high_floor'] = (df['floor'] > 10).astype(int)
        logger.info("Added high_floor feature")
        return df
    
    def run_all(self, df: pd.DataFrame, is_training: bool = True) -> pd.DataFrame:
        """
        Run all feature engineering steps in sequence.
        
        Args:
            df (pd.DataFrame): Input dataframe
            is_training (bool): Whether this is training data (includes price-based features)
            
        Returns:
            pd.DataFrame: Feature-engineered dataframe
        """
        logger.info(f"Running feature engineering (is_training={is_training})...")
        df = df.copy()
        
        # Only add price-based features during training
        if is_training:
            df = self.add_price_per_sqft_estimate(df)
        
        df = self.add_room_ratio(df)
        df = self.add_property_size_category(df)
        df = self.add_age_category(df)
        df = self.add_total_rooms(df)
        df = self.add_floor_premium_flag(df)
        
        logger.info("Feature engineering completed")
        return df
