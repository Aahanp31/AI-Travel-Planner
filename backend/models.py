from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for Google OAuth users
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    profile_picture = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    trips = db.relationship('SavedTrip', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password matches hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'profile_picture': self.profile_picture,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'trip_count': len(self.trips)
        }


class SavedTrip(db.Model):
    __tablename__ = 'saved_trips'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Trip metadata
    trip_name = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    locations = db.Column(db.String(200), nullable=True)
    days = db.Column(db.Integer, nullable=False)
    origin = db.Column(db.String(100), nullable=True)
    start_date = db.Column(db.String(50), nullable=True)
    trip_pace = db.Column(db.String(50), nullable=True)

    # Trip data (stored as JSON)
    itinerary = db.Column(db.Text, nullable=True)
    budget = db.Column(db.Text, nullable=True)
    bookings = db.Column(db.Text, nullable=True)
    map_data = db.Column(db.Text, nullable=True)
    weather = db.Column(db.Text, nullable=True)
    news = db.Column(db.Text, nullable=True)

    # Metadata
    notes = db.Column(db.Text, nullable=True)
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, include_data=False):
        """Convert saved trip to dictionary"""
        result = {
            'id': self.id,
            'trip_name': self.trip_name,
            'country': self.country,
            'locations': self.locations,
            'days': self.days,
            'origin': self.origin,
            'start_date': self.start_date,
            'trip_pace': self.trip_pace,
            'notes': self.notes,
            'is_favorite': self.is_favorite,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_data:
            result['data'] = {
                'itinerary': json.loads(self.itinerary) if self.itinerary else None,
                'budget': json.loads(self.budget) if self.budget else None,
                'bookings': json.loads(self.bookings) if self.bookings else None,
                'mapData': json.loads(self.map_data) if self.map_data else None,
                'weather': json.loads(self.weather) if self.weather else None,
                'news': json.loads(self.news) if self.news else None
            }

        return result
