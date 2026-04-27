"""
Data Loading and Validation Module

Responsible for loading raw CSV data, validating schema, and generating synthetic data if needed.
"""

import os
import logging
import numpy as np
import pandas as pd
from config import (
    PATHS, REQUIRED_COLUMNS, SYNTHETIC_DATA_SIZE, BEDROOM_DIST, 
    FURNISHING_DIST, LOCATION_MULTIPLIERS, FURNISHING_PREMIUMS, VALID_LOCATIONS
)

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Loads and validates housing dataset from CSV or generates synthetic data.
    
    Attributes:
        filepath (str): Path to the raw CSV file
        df (pd.DataFrame): Loaded dataframe
    """
    
    def __init__(self, filepath: str):
        """
        Initialize DataLoader with filepath.
        
        Args:
            filepath (str): Path to raw CSV file
        """
        self.filepath = filepath
        self.df = None
        logger.info(f"DataLoader initialized with filepath: {filepath}")
    
    def load(self) -> pd.DataFrame:
        """
        Load CSV data from disk or generate synthetic data if file doesn't exist.
        
        Returns:
            pd.DataFrame: Loaded or generated dataframe
            
        Raises:
            Exception: If data cannot be loaded or generated
        """
        try:
            if os.path.exists(self.filepath):
                logger.info(f"Loading data from {self.filepath}")
                self.df = pd.read_csv(self.filepath)
                logger.info(f"Data loaded successfully. Shape: {self.df.shape}")
            else:
                logger.warning(f"File {self.filepath} not found. Generating synthetic data...")
                self.df = self._generate_synthetic_data()
                logger.info(f"Synthetic data generated. Shape: {self.df.shape}")
                # Save synthetic data
                os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
                self.df.to_csv(self.filepath, index=False)
                logger.info(f"Synthetic data saved to {self.filepath}")
            
            # Validate schema
            if not self.validate_schema(self.df):
                raise ValueError("Data schema validation failed")
            
            logger.info(f"Data dtypes:\n{self.df.dtypes}")
            return self.df
        
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def _generate_synthetic_data(self) -> pd.DataFrame:
        """
        Generate synthetic housing dataset with realistic distributions and pricing.
        
        Returns:
            pd.DataFrame: Synthetic dataset with 5000 rows
        """
        logger.info("Starting synthetic data generation...")
        
        np.random.seed(42)
        
        n_samples = SYNTHETIC_DATA_SIZE
        
        # Generate features
        area_sqft = np.random.randint(400, 5000, size=n_samples)
        bedrooms = np.random.choice(
            BEDROOM_DIST['values'], 
            size=n_samples, 
            p=BEDROOM_DIST['probabilities']
        )
        bathrooms = np.maximum(bedrooms - np.random.randint(0, 2, size=n_samples), 1)
        location = np.random.choice(VALID_LOCATIONS, size=n_samples)
        age_years = np.random.randint(0, 40, size=n_samples)
        floor = np.random.randint(0, 30, size=n_samples)
        furnishing = np.random.choice(
            FURNISHING_DIST['values'],
            size=n_samples,
            p=FURNISHING_DIST['probabilities']
        )
        parking = np.random.randint(0, 2, size=n_samples)
        
        # Calculate price using realistic formula
        price = []
        for i in range(n_samples):
            base_price_per_sqft = LOCATION_MULTIPLIERS[location[i]]
            bedroom_bonus = bedrooms[i] * 200000
            furnishing_premium = FURNISHING_PREMIUMS[furnishing[i]]
            age_discount = age_years[i] * 15000
            floor_premium = floor[i] * 8000
            parking_bonus = parking[i] * 100000
            noise = np.random.normal(0, 200000)
            
            total_price = (base_price_per_sqft * area_sqft[i] + 
                          bedroom_bonus + furnishing_premium - 
                          age_discount + floor_premium + parking_bonus + noise)
            
            # Clip to minimum
            total_price = max(total_price, 500000)
            price.append(total_price)
        
        # Create DataFrame
        df = pd.DataFrame({
            'area_sqft': area_sqft,
            'location': location,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'age_years': age_years,
            'floor': floor,
            'furnishing': furnishing,
            'parking': parking,
            'price': price
        })
        
        logger.info(f"Synthetic data generated: {df.shape[0]} rows, {df.shape[1]} columns")
        return df
    
    def validate_schema(self, df: pd.DataFrame) -> bool:
        """
        Validate that dataframe has all required columns.
        
        Args:
            df (pd.DataFrame): Dataframe to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)
        
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False
        
        logger.info(f"Schema validation passed. All {len(REQUIRED_COLUMNS)} required columns present.")
        return True
    
    def get_summary(self, df: pd.DataFrame) -> dict:
        """
        Generate summary statistics for the dataset.
        
        Args:
            df (pd.DataFrame): Dataframe to summarize
            
        Returns:
            dict: Summary containing row count, null counts, dtypes, and price stats
        """
        summary = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'null_counts': df.isnull().sum().to_dict(),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'price_statistics': {
                'min': float(df['price'].min()),
                'max': float(df['price'].max()),
                'mean': float(df['price'].mean()),
                'std': float(df['price'].std()),
                'median': float(df['price'].median())
            },
            'numeric_summary': {
                col: {
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'mean': float(df[col].mean())
                }
                for col in df.select_dtypes(include=[np.number]).columns
            }
        }
        
        logger.info(f"Dataset Summary:")
        logger.info(f"  Rows: {summary['row_count']}, Columns: {summary['column_count']}")
        logger.info(f"  Null counts: {summary['null_counts']}")
        logger.info(f"  Price range: Rs {summary['price_statistics']['min']:,.0f} - Rs {summary['price_statistics']['max']:,.0f}")
        
        return summary
