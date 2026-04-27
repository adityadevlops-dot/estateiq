"""
Report Generation Module

Generates Power BI-ready prediction reports and model comparison CSVs.
"""

import logging
import numpy as np
import pandas as pd
from config import PRICE_BANDS

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates prediction reports and model comparison outputs for Power BI.
    
    Creates CSV files with detailed predictions and performance metrics.
    """
    
    def __init__(self):
        """Initialize ReportGenerator."""
        logger.info("ReportGenerator initialized")
    
    def generate_prediction_report(
        self, 
        df_test: pd.DataFrame, 
        y_actual: np.ndarray, 
        y_predicted: np.ndarray
    ) -> pd.DataFrame:
        """
        Generate detailed prediction report with error analysis.
        
        Creates a dataframe with predictions, actual prices, errors, and categorizations.
        
        Args:
            df_test (pd.DataFrame): Test dataframe with property details
            y_actual (np.ndarray): Actual prices (inverse log1p applied)
            y_predicted (np.ndarray): Predicted prices (inverse log1p applied)
            
        Returns:
            pd.DataFrame: Report dataframe with columns as specified
        """
        logger.info("Generating prediction report...")
        
        # Create dataframe
        report_df = pd.DataFrame({
            'property_id': range(1001, 1001 + len(df_test)),
            'location': df_test['location_encoded'].values if 'location_encoded' in df_test.columns else ['Unknown'] * len(df_test),
            'area_sqft': df_test['area_sqft'].values,
            'bedrooms': df_test['bedrooms'].values,
            'actual_price': y_actual,
            'predicted_price': y_predicted,
        })
        
        # Calculate errors
        report_df['absolute_error'] = np.abs(report_df['actual_price'] - report_df['predicted_price'])
        report_df['percentage_error'] = (report_df['absolute_error'] / report_df['actual_price'] * 100).round(2)
        report_df['within_10pct'] = (report_df['percentage_error'] <= 10).astype(int)
        
        # Add price bands
        report_df['price_band'] = report_df['actual_price'].apply(self._categorize_price_band)
        
        logger.info(f"Prediction report generated: {len(report_df)} rows")
        logger.info(f"Predictions within 10%: {report_df['within_10pct'].sum()} ({report_df['within_10pct'].mean()*100:.1f}%)")
        
        return report_df
    
    def _categorize_price_band(self, price: float) -> str:
        """
        Categorize price into band.
        
        Bands:
        - less_than_50L: < 50 Lakhs
        - 50L_to_1Cr: 50 Lakhs - 1 Crore
        - 1Cr_to_2Cr: 1-2 Crores
        - 2Cr_to_5Cr: 2-5 Crores
        - 5Cr_plus: > 5 Crores
        
        Args:
            price (float): Price in rupees
            
        Returns:
            str: Price band name
        """
        for band_name, (lower, upper) in PRICE_BANDS.items():
            if lower <= price < upper:
                return band_name
        return '5Cr_plus'
    
    def save_to_csv(self, df: pd.DataFrame, path: str):
        """
        Save dataframe to CSV for Power BI import.
        
        Uses UTF-8 encoding, comma delimiter, no index column.
        
        Args:
            df (pd.DataFrame): Dataframe to save
            path (str): Output path
        """
        try:
            df.to_csv(path, index=False, encoding='utf-8')
            logger.info(f"Prediction report saved to {path}")
        except Exception as e:
            logger.error(f"Error saving report: {str(e)}")
            raise
    
    def generate_summary_by_location_and_band(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate aggregated summary statistics by location and price band.
        
        Useful for Power BI aggregations.
        
        Args:
            df (pd.DataFrame): Prediction report dataframe
            
        Returns:
            pd.DataFrame: Summary statistics
        """
        logger.info("Generating summary by location and price band...")
        
        summary = df.groupby(['location', 'price_band']).agg({
            'property_id': 'count',
            'actual_price': ['mean', 'min', 'max'],
            'predicted_price': 'mean',
            'absolute_error': 'mean',
            'percentage_error': 'mean',
            'within_10pct': 'mean'
        }).reset_index()
        
        # Flatten column names
        summary.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                          for col in summary.columns.values]
        
        logger.info(f"Summary generated with {len(summary)} rows")
        return summary
    
    def generate_model_comparison_csv(self, evaluations: list, path: str):
        """
        Save model comparison table to CSV.
        
        Args:
            evaluations (list): List of evaluation dictionaries
            path (str): Output path
        """
        try:
            df_comparison = pd.DataFrame(evaluations)
            df_comparison.to_csv(path, index=False, encoding='utf-8')
            logger.info(f"Model comparison saved to {path}")
        except Exception as e:
            logger.error(f"Error saving model comparison: {str(e)}")
            raise
