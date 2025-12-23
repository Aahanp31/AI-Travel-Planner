from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, SavedTrip
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os
import json

auth_bp = Blueprint('auth', __name__)

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user with email and password"""
    try:
        data = request.get_json()
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        if not email or not username or not password:
            return jsonify({'error': 'Email, username, and password are required'}), 400

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already taken'}), 400

        # Create new user
        user = User(email=email, username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # Create access token
        access_token = create_access_token(identity=user.id)

        return jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f'Signup error: {e}')
        return jsonify({'error': 'Failed to create user'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login with email and password"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Find user
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401

        # Create access token
        access_token = create_access_token(identity=user.id)

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        print(f'Login error: {e}')
        return jsonify({'error': 'Failed to login'}), 500


@auth_bp.route('/google-auth', methods=['POST'])
def google_auth():
    """Authenticate with Google OAuth"""
    try:
        data = request.get_json()
        token = data.get('token')

        if not token:
            return jsonify({'error': 'Google token is required'}), 400

        # Verify Google token
        try:
            idinfo = id_token.verify_oauth2_token(
                token, google_requests.Request(), GOOGLE_CLIENT_ID
            )

            # Get user info from token
            google_id = idinfo['sub']
            email = idinfo.get('email')
            username = idinfo.get('name', email.split('@')[0])
            profile_picture = idinfo.get('picture')

            # Check if user exists
            user = User.query.filter_by(google_id=google_id).first()

            if not user:
                # Check if email is already used
                existing_user = User.query.filter_by(email=email).first()
                if existing_user:
                    return jsonify({'error': 'Email already registered with password login'}), 400

                # Create new user
                user = User(
                    email=email,
                    username=username,
                    google_id=google_id,
                    profile_picture=profile_picture
                )
                db.session.add(user)
                db.session.commit()

            # Create access token
            access_token = create_access_token(identity=user.id)

            return jsonify({
                'message': 'Google authentication successful',
                'access_token': access_token,
                'user': user.to_dict()
            }), 200

        except ValueError as e:
            print(f'Invalid Google token: {e}')
            return jsonify({'error': 'Invalid Google token'}), 401

    except Exception as e:
        db.session.rollback()
        print(f'Google auth error: {e}')
        return jsonify({'error': 'Failed to authenticate with Google'}), 500


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user's profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({'user': user.to_dict()}), 200

    except Exception as e:
        print(f'Get profile error: {e}')
        return jsonify({'error': 'Failed to get profile'}), 500


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        # Update username if provided
        if 'username' in data:
            new_username = data['username']
            if new_username != user.username:
                # Check if username is taken
                if User.query.filter_by(username=new_username).first():
                    return jsonify({'error': 'Username already taken'}), 400
                user.username = new_username

        # Update email if provided
        if 'email' in data:
            new_email = data['email']
            if new_email != user.email:
                # Check if email is taken
                if User.query.filter_by(email=new_email).first():
                    return jsonify({'error': 'Email already registered'}), 400
                user.email = new_email

        # Update password if provided
        if 'password' in data and data['password']:
            user.set_password(data['password'])

        # Update profile picture if provided
        if 'profile_picture' in data:
            user.profile_picture = data['profile_picture']

        db.session.commit()

        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f'Update profile error: {e}')
        return jsonify({'error': 'Failed to update profile'}), 500


@auth_bp.route('/save-trip', methods=['POST'])
@jwt_required()
def save_trip():
    """Save a trip to user's account"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Required fields
        trip_name = data.get('trip_name')
        country = data.get('country')
        days = data.get('days')

        if not trip_name or not country or not days:
            return jsonify({'error': 'Trip name, country, and days are required'}), 400

        # Create saved trip
        trip = SavedTrip(
            user_id=user_id,
            trip_name=trip_name,
            country=country,
            locations=data.get('locations'),
            days=days,
            origin=data.get('origin'),
            start_date=data.get('start_date'),
            trip_pace=data.get('trip_pace'),
            itinerary=json.dumps(data.get('itinerary')) if data.get('itinerary') else None,
            budget=json.dumps(data.get('budget')) if data.get('budget') else None,
            bookings=json.dumps(data.get('bookings')) if data.get('bookings') else None,
            map_data=json.dumps(data.get('mapData')) if data.get('mapData') else None,
            weather=json.dumps(data.get('weather')) if data.get('weather') else None,
            news=json.dumps(data.get('news')) if data.get('news') else None,
            notes=data.get('notes')
        )

        db.session.add(trip)
        db.session.commit()

        return jsonify({
            'message': 'Trip saved successfully',
            'trip': trip.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f'Save trip error: {e}')
        return jsonify({'error': 'Failed to save trip'}), 500


@auth_bp.route('/trips', methods=['GET'])
@jwt_required()
def get_trips():
    """Get all saved trips for current user"""
    try:
        user_id = get_jwt_identity()

        # Get trips ordered by most recent
        trips = SavedTrip.query.filter_by(user_id=user_id).order_by(
            SavedTrip.is_favorite.desc(),
            SavedTrip.updated_at.desc()
        ).all()

        return jsonify({
            'trips': [trip.to_dict() for trip in trips]
        }), 200

    except Exception as e:
        print(f'Get trips error: {e}')
        return jsonify({'error': 'Failed to get trips'}), 500


@auth_bp.route('/trips/<int:trip_id>', methods=['GET'])
@jwt_required()
def get_trip(trip_id):
    """Get a specific trip with full data"""
    try:
        user_id = get_jwt_identity()

        trip = SavedTrip.query.filter_by(id=trip_id, user_id=user_id).first()

        if not trip:
            return jsonify({'error': 'Trip not found'}), 404

        return jsonify({
            'trip': trip.to_dict(include_data=True)
        }), 200

    except Exception as e:
        print(f'Get trip error: {e}')
        return jsonify({'error': 'Failed to get trip'}), 500


@auth_bp.route('/trips/<int:trip_id>', methods=['PUT'])
@jwt_required()
def update_trip(trip_id):
    """Update a saved trip"""
    try:
        user_id = get_jwt_identity()
        trip = SavedTrip.query.filter_by(id=trip_id, user_id=user_id).first()

        if not trip:
            return jsonify({'error': 'Trip not found'}), 404

        data = request.get_json()

        # Update fields if provided
        if 'trip_name' in data:
            trip.trip_name = data['trip_name']
        if 'notes' in data:
            trip.notes = data['notes']
        if 'is_favorite' in data:
            trip.is_favorite = data['is_favorite']

        db.session.commit()

        return jsonify({
            'message': 'Trip updated successfully',
            'trip': trip.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f'Update trip error: {e}')
        return jsonify({'error': 'Failed to update trip'}), 500


@auth_bp.route('/trips/<int:trip_id>', methods=['DELETE'])
@jwt_required()
def delete_trip(trip_id):
    """Delete a saved trip"""
    try:
        user_id = get_jwt_identity()
        trip = SavedTrip.query.filter_by(id=trip_id, user_id=user_id).first()

        if not trip:
            return jsonify({'error': 'Trip not found'}), 404

        db.session.delete(trip)
        db.session.commit()

        return jsonify({'message': 'Trip deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        print(f'Delete trip error: {e}')
        return jsonify({'error': 'Failed to delete trip'}), 500
