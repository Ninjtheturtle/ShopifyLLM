# A/B Testing Database Models
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    return db

class Experiment(db.Model):
    """A/B Testing Experiment Model"""
    __tablename__ = 'experiments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    experiment_type = db.Column(db.String(50), nullable=False)  # 'product_description', 'product_title', 'cta_button'
    status = db.Column(db.String(20), default='draft', nullable=False)  # 'draft', 'running', 'stopped', 'completed'
    config = db.Column(db.JSON)  # Additional configuration
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    variants = db.relationship('Variant', backref='experiment', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Experiment {self.name}>'

class Variant(db.Model):
    """A/B Testing Variant Model"""
    __tablename__ = 'variants'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    experiment_id = db.Column(db.String(36), db.ForeignKey('experiments.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    variant_type = db.Column(db.String(20), nullable=False)  # 'control', 'treatment'
    config = db.Column(db.JSON)  # Variant configuration and content
    traffic_allocation = db.Column(db.Float, default=50.0, nullable=False)  # Percentage of traffic
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    assignments = db.relationship('Assignment', backref='variant', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Variant {self.name}>'

class Assignment(db.Model):
    """User Assignment to Variant Model"""
    __tablename__ = 'assignments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    user_id = db.Column(db.String(255), nullable=False)
    experiment_id = db.Column(db.String(36), db.ForeignKey('experiments.id'), nullable=False)
    variant_id = db.Column(db.String(36), db.ForeignKey('variants.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    events = db.relationship('Event', backref='assignment', lazy=True, cascade='all, delete-orphan')
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_user_experiment', 'user_id', 'experiment_id'),
        db.Index('idx_experiment_variant', 'experiment_id', 'variant_id'),
        db.UniqueConstraint('user_id', 'experiment_id', name='uq_user_experiment')
    )
    
    def __repr__(self):
        return f'<Assignment {self.user_id} -> {self.variant_id}>'

class Event(db.Model):
    """Event Tracking Model"""
    __tablename__ = 'events'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    assignment_id = db.Column(db.String(36), db.ForeignKey('assignments.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # 'view', 'click', 'add_to_cart', 'purchase', 'signup'
    event_data = db.Column(db.JSON)  # Additional event data
    revenue = db.Column(db.Float)  # Revenue for purchase events
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_assignment_event_type', 'assignment_id', 'event_type'),
        db.Index('idx_event_timestamp', 'timestamp'),
        db.Index('idx_event_type_timestamp', 'event_type', 'timestamp')
    )
    
    def __repr__(self):
        return f'<Event {self.event_type} at {self.timestamp}>'
