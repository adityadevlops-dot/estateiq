"""
API Input Validation Schemas

Validates incoming requests using manual validation (no marshmallow dependency).
"""

import logging
from config import VALID_LOCATIONS, VALID_FURNISHING

logger = logging.getLogger(__name__)


class PredictInputSchema:
    """
    Validates prediction request input.
    
    Validates all required and optional fields.
    """
    
    @classmethod
    def validate(cls, data: dict) -> tuple:
        """
        Validate prediction input data.
        
        Args:
            data (dict): Raw input dictionary
            
        Returns:
            tuple: (cleaned_data_dict, list_of_error_strings)
            
        Returns cleaned data with defaults for optional fields,
        and list of validation errors (empty if valid).
        """
        errors = []
        cleaned_data = {}
        
        logger.info("Validating prediction input...")
        
        # Validate area_sqft (required)
        if 'area_sqft' not in data:
            errors.append("area_sqft is required")
        else:
            try:
                area_sqft = float(data['area_sqft'])
                if not (100 <= area_sqft <= 50000):
                    errors.append("area_sqft must be between 100 and 50000")
                else:
                    cleaned_data['area_sqft'] = area_sqft
            except (ValueError, TypeError):
                errors.append("area_sqft must be a valid number")
        
        # Validate location (required)
        if 'location' not in data:
            errors.append("location is required")
        elif data['location'] not in VALID_LOCATIONS:
            errors.append(f"location must be one of: {', '.join(VALID_LOCATIONS)}")
        else:
            cleaned_data['location'] = data['location']
        
        # Validate bedrooms (required)
        if 'bedrooms' not in data:
            errors.append("bedrooms is required")
        else:
            try:
                bedrooms = int(data['bedrooms'])
                if not (1 <= bedrooms <= 10):
                    errors.append("bedrooms must be between 1 and 10")
                else:
                    cleaned_data['bedrooms'] = bedrooms
            except (ValueError, TypeError):
                errors.append("bedrooms must be a valid integer")
        
        # Validate bathrooms (required)
        if 'bathrooms' not in data:
            errors.append("bathrooms is required")
        else:
            try:
                bathrooms = int(data['bathrooms'])
                if not (1 <= bathrooms <= 10):
                    errors.append("bathrooms must be between 1 and 10")
                else:
                    cleaned_data['bathrooms'] = bathrooms
            except (ValueError, TypeError):
                errors.append("bathrooms must be a valid integer")
        
        # Validate age_years (required)
        if 'age_years' not in data:
            errors.append("age_years is required")
        else:
            try:
                age_years = int(data['age_years'])
                if not (0 <= age_years <= 100):
                    errors.append("age_years must be between 0 and 100")
                else:
                    cleaned_data['age_years'] = age_years
            except (ValueError, TypeError):
                errors.append("age_years must be a valid integer")
        
        # Validate floor (optional, default=0)
        if 'floor' in data:
            try:
                floor = int(data['floor'])
                if not (0 <= floor <= 100):
                    errors.append("floor must be between 0 and 100")
                else:
                    cleaned_data['floor'] = floor
            except (ValueError, TypeError):
                errors.append("floor must be a valid integer")
        else:
            cleaned_data['floor'] = 0
        
        # Validate furnishing (optional, default='Unfurnished')
        if 'furnishing' in data:
            if data['furnishing'] not in VALID_FURNISHING:
                errors.append(f"furnishing must be one of: {', '.join(VALID_FURNISHING)}")
            else:
                cleaned_data['furnishing'] = data['furnishing']
        else:
            cleaned_data['furnishing'] = 'Unfurnished'
        
        # Validate parking (optional, default=0)
        if 'parking' in data:
            try:
                parking = int(data['parking'])
                if parking not in [0, 1]:
                    errors.append("parking must be 0 or 1")
                else:
                    cleaned_data['parking'] = parking
            except (ValueError, TypeError):
                errors.append("parking must be 0 or 1")
        else:
            cleaned_data['parking'] = 0
        
        if errors:
            logger.warning(f"Validation errors: {errors}")
        else:
            logger.info("Input validation passed")
        
        return cleaned_data, errors
