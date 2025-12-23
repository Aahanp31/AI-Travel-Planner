import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
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
import asyncio
from datetime import timedelta

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required. Please set it in your .env file.")

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# JWT configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

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


@app.route('/plan-trip', methods=['POST'])
def plan_trip():
    try:
        data = request.get_json()
        country = data.get('country')
        locations = data.get('locations')  # Optional, comma-separated cities
        days = data.get('days', 3)
        origin = data.get('origin', 'LAX')
        additional_details = data.get('additionalDetails')
        detail_level = data.get('detailLevel', 'standard')  # quick, standard, or comprehensive

        if not country:
            return jsonify({'error': 'Country is required'}), 400

        # Run all agents in parallel using asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # First batch: Run initial agents in parallel
        itinerary_raw, budget, bookings, weather, news = loop.run_until_complete(
            asyncio.gather(
                itinerary_agent(country, locations, days, origin, additional_details, detail_level),
                budget_agent(country, locations, days, origin, additional_details),
                booking_agent(country, locations, days, origin),
                weather_agent(country, locations, days),
                news_agent(country, locations)
            )
        )

        # Second batch: Run Wikipedia links and map data in parallel
        # (both depend on itinerary)
        itinerary, map_data = loop.run_until_complete(
            asyncio.gather(
                add_wikipedia_links(itinerary_raw),
                map_agent(country, itinerary_raw, locations)
            )
        )

        loop.close()

        return jsonify({
            'itinerary': itinerary,
            'budget': budget,
            'bookings': bookings,
            'mapData': map_data,
            'weather': weather,
            'news': news
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
