import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from agents.itinerary_agent import itinerary_agent
from agents.budget_agent import budget_agent
from agents.booking_agent import booking_agent
from agents.map_agent import map_agent
from agents.wiki_agent import add_wikipedia_links
from agents.weather_agent import weather_agent
from agents.news_agent import news_agent
import asyncio

load_dotenv()

app = Flask(__name__)
CORS(app)

PORT = int(os.getenv('PORT', 4000))


@app.route('/plan-trip', methods=['POST'])
def plan_trip():
    try:
        data = request.get_json()
        country = data.get('country')
        locations = data.get('locations')  # Optional, comma-separated cities
        days = data.get('days', 3)
        origin = data.get('origin', 'LAX')
        additional_details = data.get('additionalDetails')

        if not country:
            return jsonify({'error': 'Country is required'}), 400

        # Run all agents in parallel using asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # First batch: Run initial agents in parallel
        itinerary_raw, budget, bookings, weather, news = loop.run_until_complete(
            asyncio.gather(
                itinerary_agent(country, locations, days, origin, additional_details),
                budget_agent(country, locations, days, origin),
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


if __name__ == '__main__':
    print(f'Backend running on http://localhost:{PORT}')
    app.run(host='0.0.0.0', port=PORT, debug=True)
