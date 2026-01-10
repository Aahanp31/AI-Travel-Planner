import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from sqlalchemy import text
from agents.itinerary_agent import itinerary_agent
from agents.budget_agent import budget_agent
from agents.booking_agent import booking_agent
from agents.map_agent import map_agent
from agents.wiki_agent import add_wikipedia_links
from agents.weather_agent import weather_agent
from agents.news_agent import news_agent
from agents.chat_agent import chat_agent
from models import db
from auth_routes import auth_bp
from utils.location_autocorrect import autocorrect_location
import asyncio
from datetime import timedelta

load_dotenv()

app = Flask(__name__)
# Production CORS - only allow Vercel frontend
FRONTEND_URLS = [url.strip() for url in os.getenv('FRONTEND_URLS', 'http://localhost:3000').split(',')]
CORS(app, origins=FRONTEND_URLS, supports_credentials=True)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required. Please set it in your .env file.")

# Strip whitespace and newlines from DATABASE_URL
DATABASE_URL = DATABASE_URL.strip()

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'connect_args': {
        'connect_timeout': 10,
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5,
    }
}

# JWT configuration - require secret key, reduce token lifetime for security
JWT_SECRET = os.getenv('JWT_SECRET_KEY', '').strip()
if not JWT_SECRET or JWT_SECRET == 'your-secret-key-change-in-production':
    raise ValueError("JWT_SECRET_KEY environment variable must be set to a secure value")
app.config['JWT_SECRET_KEY'] = JWT_SECRET
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # Reduced from 30 days to 1 hour

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')

PORT = int(os.getenv('PORT', 4000))

# Create database tables
with app.app_context():
    db.create_all()
    print('✓ Database initialized')


@app.route('/', methods=['GET'])
def root():
    """Root endpoint - API information"""
    return jsonify({
        'service': 'AI Travel Planner API',
        'status': 'running',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'auth': '/auth/*',
            'plan_trip': '/plan-trip',
            'chat': '/chat'
        }
    }), 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render monitoring"""
    try:
        # Check database connection
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'service': 'ai-travel-planner-backend'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500


@app.route('/plan-trip', methods=['POST'])
def plan_trip():
    try:
        data = request.get_json()
        trip_mode = data.get('tripMode', 'single')
        origin = data.get('origin', 'LAX')
        additional_details = data.get('additionalDetails')
        detail_level = data.get('detailLevel', 'standard')

        # Run all agents in parallel using asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        if trip_mode == 'multi':
            # Multi-country mode
            countries = data.get('countries', [])
            if not countries or len(countries) < 2:
                return jsonify({'error': 'At least 2 countries required for multi-country trip'}), 400

            # Autocorrect all country names
            corrected_countries = []
            for country in countries:
                location_result = loop.run_until_complete(autocorrect_location(country))
                corrected_countries.append(location_result.get('corrected', country))

            # Import multi-country agent
            from agents.multi_country_agent import multi_country_agent

            # Generate multi-country itinerary with corrected names
            result = loop.run_until_complete(
                multi_country_agent(corrected_countries, origin, additional_details, detail_level)
            )

            loop.close()
            return jsonify(result)

        else:
            # Single country mode (original logic)
            country = data.get('country')
            locations = data.get('locations')
            days = data.get('days', 3)

            if not country:
                return jsonify({'error': 'Country is required'}), 400

            # Autocorrect the destination name
            location_result = loop.run_until_complete(autocorrect_location(country))
            corrected_country = location_result.get('corrected', country)

            # First batch: Run initial agents in parallel
            itinerary_raw, budget, bookings, weather, news = loop.run_until_complete(
                asyncio.gather(
                    itinerary_agent(corrected_country, locations, days, origin, additional_details, detail_level),
                    budget_agent(corrected_country, locations, days, origin, additional_details),
                    booking_agent(corrected_country, locations, days, origin),
                    weather_agent(corrected_country, locations, days),
                    news_agent(corrected_country, locations)
                )
            )

            # Second batch: Run Wikipedia links and map data in parallel
            itinerary, map_data = loop.run_until_complete(
                asyncio.gather(
                    add_wikipedia_links(itinerary_raw),
                    map_agent(corrected_country, itinerary_raw, locations)
                )
            )

            loop.close()

            return jsonify({
                'itinerary': itinerary,
                'budget': budget,
                'bookings': bookings,
                'mapData': map_data,
                'weather': weather,
                'news': news,
                'correctedDestination': corrected_country,
                'wasAutocorrected': location_result.get('was_corrected', False)
            })

    except Exception as err:
        import traceback
        print(f'Error planning trip: {err}')
        traceback.print_exc()
        return jsonify({'error': 'Failed to plan trip', 'details': str(err)}), 500


@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message')
        current_trip = data.get('currentTrip', {})

        if not user_message:
            return jsonify({'error': 'Message is required'}), 400

        # Run chat agent
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        chat_response = loop.run_until_complete(
            chat_agent(user_message, current_trip)
        )

        loop.close()

        return jsonify(chat_response)

    except Exception as err:
        import traceback
        print(f'Error in chat: {err}')
        traceback.print_exc()
        return jsonify({'error': 'Failed to process chat message', 'details': str(err)}), 500


if __name__ == '__main__':
    print(f'Backend running on http://localhost:{PORT}')
    # Increase timeout for processing large itineraries with detailed preferences
    app.run(host='0.0.0.0', port=PORT, debug=True, threaded=True)
