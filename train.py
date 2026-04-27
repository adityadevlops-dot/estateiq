"""
Training Pipeline Entry Point

Trains machine learning models on housing dataset and saves best model.

Usage:
    python train.py
"""

import os
import logging
import numpy as np
import pandas as pd
from config import (
    PATHS, MODEL_CONFIG, setup_logging
)
from src.data_loader import DataLoader
from src.preprocessor import Preprocessor
from src.feature_engineer import FeatureEngineer
from src.model_trainer import ModelTrainer
from src.report_generator import ReportGenerator

# Configure logging
logger = setup_logging()


def main():
    """
    Execute complete training pipeline.
    
    Steps:
    1. Load and validate data
    2. Preprocess data (handle nulls, remove outliers, encode, scale)
    3. Engineer features
    4. Train multiple models
    5. Evaluate and select best
    6. Save model, encoders, and evaluation report
    7. Generate Power BI output
    """
    logger.info("="*80)
    logger.info("STARTING TRAINING PIPELINE")
    logger.info("="*80)
    
    try:
        # ====================================================================
        # STEP 1: LOAD AND VALIDATE DATA
        # ====================================================================
        logger.info("\n[STEP 1] Loading and validating data...")
        data_loader = DataLoader(PATHS['raw_data'])
        df_raw = data_loader.load()
        
        summary = data_loader.get_summary(df_raw)
        logger.info(f"Data Summary: {summary['row_count']} rows, {summary['column_count']} columns")
        
        # ====================================================================
        # STEP 2: PREPROCESS DATA
        # ====================================================================
        logger.info("\n[STEP 2] Preprocessing data...")
        preprocessor = Preprocessor()
        
        df_clean = preprocessor.handle_missing_values(df_raw.copy())
        df_clean = preprocessor.remove_outliers(df_clean)
        df_clean = preprocessor.encode_categoricals(df_clean, fit=True)
        
        logger.info(f"Data after preprocessing: {df_clean.shape}")
        
        # ====================================================================
        # STEP 3: FEATURE ENGINEERING
        # ====================================================================
        logger.info("\n[STEP 3] Engineering features...")
        feature_engineer = FeatureEngineer()
        df_features = feature_engineer.run_all(df_clean, is_training=True)
        
        logger.info(f"Data after feature engineering: {df_features.shape}")
        logger.info(f"Features: {list(df_features.columns)}")
        
        # ====================================================================
        # STEP 4: TRAIN MODELS
        # ====================================================================
        logger.info("\n[STEP 4] Training models...")
        model_trainer = ModelTrainer(MODEL_CONFIG)
        
        X_train, X_test, y_train, y_test = model_trainer.prepare_data(df_features)
        
        # Train Linear Regression
        logger.info("\nTraining Linear Regression...")
        lr_model = model_trainer.train_linear_regression(X_train, y_train)
        
        # Train Random Forest
        logger.info("\nTraining Random Forest...")
        rf_model = model_trainer.train_random_forest(X_train, y_train)
        
        # Train Gradient Boosting
        logger.info("\nTraining Gradient Boosting...")
        gb_model = model_trainer.train_gradient_boosting(X_train, y_train)
        
        # ====================================================================
        # STEP 5: EVALUATE MODELS
        # ====================================================================
        logger.info("\n[STEP 5] Evaluating models...")
        
        eval_lr = model_trainer.evaluate_model(lr_model, X_test, y_test, "LinearRegression")
        eval_rf = model_trainer.evaluate_model(rf_model, X_test, y_test, "RandomForestRegressor")
        eval_gb = model_trainer.evaluate_model(gb_model, X_test, y_test, "GradientBoostingRegressor")
        
        evaluations = [eval_lr, eval_rf, eval_gb]
        
        # ====================================================================
        # STEP 6: SELECT BEST MODEL
        # ====================================================================
        logger.info("\n[STEP 6] Selecting best model...")
        best_model_name = model_trainer.select_best_model(evaluations)
        
        # Get best model object
        if best_model_name == "LinearRegression":
            best_model = lr_model
        elif best_model_name == "RandomForestRegressor":
            best_model = rf_model
        else:
            best_model = gb_model
        
        # ====================================================================
        # STEP 7: SAVE ARTIFACTS
        # ====================================================================
        logger.info("\n[STEP 7] Saving artifacts...")
        
        # Create directories if needed
        os.makedirs(os.path.dirname(PATHS['best_model']), exist_ok=True)
        os.makedirs(os.path.dirname(PATHS['evaluation_report']), exist_ok=True)
        
        # Save model
        model_trainer.save_model(best_model, PATHS['best_model'])
        
        # Save encoders and scaler
        preprocessor.save_encoders(PATHS['encoders'])
        
        # Save evaluation report
        model_trainer.save_evaluation_report(evaluations, PATHS['evaluation_report'])
        
        logger.info("\nAll artifacts saved successfully")
        
        # ====================================================================
        # STEP 8: GENERATE POWER BI OUTPUT
        # ====================================================================
        logger.info("\n[STEP 8] Generating Power BI output...")
        
        # Make predictions on test set
        y_pred_log = best_model.predict(X_test)
        y_pred = np.expm1(y_pred_log)
        y_test_actual = np.expm1(y_test)
        
        # Create test dataframe with original features
        from config import FEATURE_COLUMNS
        
        # Extract test indices
        test_indices = list(range(len(X_train), len(X_train) + len(X_test)))
        df_test_with_originals = df_features.iloc[test_indices].copy()
        
        # Generate report
        report_generator = ReportGenerator()
        df_report = report_generator.generate_prediction_report(df_test_with_originals, y_test_actual, y_pred)
        
        # Save to CSV
        os.makedirs(os.path.dirname(PATHS['predictions_output']), exist_ok=True)
        report_generator.save_to_csv(df_report, PATHS['predictions_output'])
        
        # Save summary
        df_summary = report_generator.generate_summary_by_location_and_band(df_report)
        report_generator.save_to_csv(df_summary, PATHS['predictions_summary'])
        
        # Save model comparison
        report_generator.generate_model_comparison_csv(evaluations, PATHS['model_comparison'])
        
        logger.info(f"Power BI outputs saved to {PATHS['predictions_output']}")
        
        # ====================================================================
        # TRAINING SUMMARY
        # ====================================================================
        logger.info("\n" + "="*80)
        logger.info("TRAINING SUMMARY")
        logger.info("="*80)
        
        # Print evaluation table
        logger.info("\nModel Evaluation Results:")
        logger.info("-" * 80)
        logger.info(f"{'Model':<30} {'R² Score':<15} {'MAE':<15} {'RMSE':<15}")
        logger.info("-" * 80)
        
        for eval_dict in evaluations:
            logger.info(
                f"{eval_dict['model_name']:<30} "
                f"{eval_dict['r2']:<15.4f} "
                f"₹{eval_dict['mae']:<14,.0f} "
                f"₹{eval_dict['rmse']:<14,.0f}"
            )
        
        logger.info("-" * 80)
        logger.info(f"Best Model: {best_model_name}")
        logger.info(f"Best R2 Score: {max([e['r2'] for e in evaluations]):.4f}")
        logger.info(f"Model saved to: {PATHS['best_model']}")
        logger.info(f"Predictions saved to: {PATHS['predictions_output']}")
        logger.info(f"Training completed successfully!\n")
        
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"\nTraining pipeline failed: {str(e)}")
        raise


if __name__ == '__main__':
    main()
