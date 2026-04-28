# ============================================================================
# DATABASE MODELS
# ============================================================================

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    predictions = db.relationship('Prediction', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class Prediction(db.Model):
    """Prediction history model"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    
    # Input features
    area_sqft = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    age_years = db.Column(db.Integer, nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    furnishing = db.Column(db.String(50), nullable=False)
    parking = db.Column(db.Integer, nullable=False)
    
    # Prediction output
    predicted_price = db.Column(db.Float, nullable=False)
    confidence = db.Column(db.Float)
    min_price = db.Column(db.Float)
    max_price = db.Column(db.Float)
    
    # Metadata
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    model_version = db.Column(db.String(20), default='1.0')
    
    def to_dict(self):
        """Convert prediction to dictionary"""
        return {
            'id': self.id,
            'area_sqft': self.area_sqft,
            'location': self.location,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'age_years': self.age_years,
            'floor': self.floor,
            'furnishing': self.furnishing,
            'parking': self.parking,
            'predicted_price': self.predicted_price,
            'confidence': self.confidence,
            'min_price': self.min_price,
            'max_price': self.max_price,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Prediction {self.id}>'
