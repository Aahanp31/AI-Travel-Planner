import os
import re
import json
import google.generativeai as genai

genai.configure(api_key=os.getenv('GEMINI_API_KEY', ''))


async def itinerary_agent(country: str, locations: str = None, days: int = 3, origin: str = '', additional_details: str = None) -> dict:
    """
    Generate a travel itinerary using Google Gemini AI.
    Args:
        country: The country to visit (required)
        locations: Optional comma-separated list of specific cities/locations
        days: Number of days for the trip
        origin: Departure city
        additional_details: User preferences and requirements
    """
    # Determine planning mode based on locations parameter
    if locations and locations.strip():
        # User specified locations
        location_list = [loc.strip() for loc in locations.split(',')]
        num_locations = len(location_list)

        if num_locations == 1:
            # Single location mode
            prompt_mode = 'single_city'
            destination = f"{locations}, {country}"
        else:
            # Multi-location mode
            prompt_mode = 'multi_city'
            destination = f"{locations} in {country}"
    else:
        # AI decides cities (country exploration mode)
        prompt_mode = 'country_explore'
        destination = country
        location_list = None

    # Build additional context if user provided preferences
    additional_context = ""
    if additional_details and additional_details.strip():
        additional_context = f"""

IMPORTANT - USER PREFERENCES AND EXISTING PLANS:
The traveler has provided the following details that MUST be incorporated into the itinerary:
{additional_details}

Please carefully read these details and:
1. Include any pre-booked tickets or reservations mentioned on the appropriate days
2. Plan activities around existing commitments
3. Incorporate interests and preferences mentioned (e.g., museums, food, nightlife)
4. Adjust the itinerary to complement what's already planned
5. Avoid scheduling conflicting activities during pre-booked time slots
"""

    if prompt_mode == 'country_explore':
        prompt = f"""Create a {days}-day travel itinerary for {country}.

IMPORTANT - AI CITY SELECTION MODE:
The traveler wants to explore {country} but hasn't specified exact cities.
Please:
1. Select 1-{min(4, (days // 2) + 1)} cities/regions in {country} that best showcase the country
2. Consider the {days}-day duration when choosing number of cities (longer trips = more cities)
3. Plan a logical geographic route minimizing travel time
4. Include major highlights and cultural experiences

MULTI-CITY ITINERARY INSTRUCTIONS:
1. Plan a logical route that minimizes backtracking - organize cities geographically
2. For each location change, include transportation details:
   - Method (train, bus, flight, car rental)
   - Approximate travel time
   - Estimated cost in BOTH local currency AND {origin} currency (with conversion)
3. Format each time period (morning, afternoon, evening) as an ARRAY of 2-3 specific activities
4. Include realistic, well-known attractions for each city
5. Group consecutive days in the same city together

For each day, provide:
- location: The city/area for this day (string)
- morning: Array of 2-3 morning activities
- afternoon: Array of 2-3 afternoon activities
- evening: Array of 2-3 evening activities
- food_recommendation: A specific local dish or restaurant recommendation
- cultural_highlight: One interesting cultural fact or must-see cultural site
- transportation: (ONLY when moving to a new city) Object with: {{ method, duration, cost_local, cost_origin, travel_note }}
  * cost_local should show local currency with proper symbol (e.g., "NZD $150-250")
  * cost_origin should show {origin} currency conversion (e.g., "$95-160 USD")

Return ONLY valid JSON with keys 'day1', 'day2', etc. Example:
{{
  "day1": {{
    "location": "Tokyo",
    "morning": ["Visit Tokyo Skytree", "Explore Senso-ji Temple"],
    "afternoon": ["See Shibuya Crossing", "Visit Meiji Shrine"],
    "evening": ["Dinner in Shinjuku", "Night views from Tokyo Tower"],
    "food_recommendation": "Try authentic ramen at Ichiran",
    "cultural_highlight": "Experience a traditional tea ceremony"
  }},
  "day3": {{
    "location": "Kyoto",
    "transportation": {{
      "method": "Shinkansen (bullet train)",
      "duration": "2 hours 15 minutes",
      "cost_local": "¥13,320",
      "travel_note": "Depart from Tokyo Station to Kyoto Station"
    }},
    "morning": ["Travel to Kyoto", "Check in to hotel"],
    "afternoon": ["Visit Fushimi Inari Shrine", "Explore Gion district"],
    "evening": ["Traditional kaiseki dinner"],
    "food_recommendation": "Try authentic Kyoto-style kaiseki",
    "cultural_highlight": "Geisha culture in Gion district"
  }}
}}{additional_context}"""
    elif prompt_mode == 'multi_city':
        prompt = f"""Create a {days}-day travel itinerary visiting these locations in {country}:
{', '.join(location_list)}

IMPORTANT - MULTI-LOCATION MODE:
The traveler specifically wants to visit: {locations}
Please:
1. Allocate days proportionally based on {days} total days
2. Plan visits in a logical geographic order to minimize travel time
3. Include transportation details between each location
4. Create a comprehensive itinerary that covers all specified locations

MULTI-CITY ITINERARY INSTRUCTIONS:
1. Plan a logical route that minimizes backtracking - organize cities geographically
2. For each location change, include transportation details:
   - Method (train, bus, flight, car rental)
   - Approximate travel time
   - Estimated cost in BOTH local currency AND {origin} currency (with conversion)
3. Format each time period (morning, afternoon, evening) as an ARRAY of 2-3 specific activities
4. Include realistic, well-known attractions for each city
5. Group consecutive days in the same city together

For each day, provide:
- location: The city/area for this day (string)
- morning: Array of 2-3 morning activities
- afternoon: Array of 2-3 afternoon activities
- evening: Array of 2-3 evening activities
- food_recommendation: A specific local dish or restaurant recommendation
- cultural_highlight: One interesting cultural fact or must-see cultural site
- transportation: (ONLY when moving to a new city) Object with: {{ method, duration, cost_local, cost_origin, travel_note }}
  * cost_local should show local currency with proper symbol (e.g., "NZD $150-250")
  * cost_origin should show {origin} currency conversion (e.g., "$95-160 USD")

Return ONLY valid JSON with keys 'day1', 'day2', etc. Example:
{{
  "day1": {{
    "location": "Auckland",
    "morning": ["Visit Sky Tower", "Explore Viaduct Harbour"],
    "afternoon": ["See Auckland Museum", "Walk through Cornwall Park"],
    "evening": ["Dinner at waterfront", "Explore Ponsonby nightlife"],
    "food_recommendation": "Try New Zealand lamb and pavlova",
    "cultural_highlight": "Māori cultural heritage at Auckland Museum"
  }},
  "day3": {{
    "location": "Queenstown",
    "transportation": {{
      "method": "Domestic flight",
      "duration": "1 hour 45 minutes",
      "cost_local": "NZD $150-250",
      "cost_origin": "$95-160 USD",
      "travel_note": "Air New Zealand from Auckland to Queenstown"
    }},
    "morning": ["Travel to Queenstown", "Check in to hotel"],
    "afternoon": ["Ride Skyline Gondola", "Explore Queenstown Gardens"],
    "evening": ["Dinner on Queenstown waterfront"],
    "food_recommendation": "Try fresh venison and local wines",
    "cultural_highlight": "Adventure capital of New Zealand"
  }}
}}{additional_context}"""
    else:  # single_city
        prompt = f"""Create a {days}-day travel itinerary for {destination}.

IMPORTANT INSTRUCTIONS:
1. Focus ONLY on the actual city/destination requested, not nearby areas
2. Include major tourist attractions and landmarks in that specific city
3. Format each time period (morning, afternoon, evening) as an ARRAY of 2-3 specific activities
4. Each activity should be a clear, actionable bullet point (e.g., "Visit the Eiffel Tower")
5. Include realistic, well-known attractions for the destination

For each day, provide:
- morning: Array of 2-3 morning activities
- afternoon: Array of 2-3 afternoon activities
- evening: Array of 2-3 evening activities
- food_recommendation: A specific local dish or restaurant type
- cultural_highlight: One interesting cultural fact or tradition

Return ONLY valid JSON with keys 'day1', 'day2', etc. Example:
{{
  "day1": {{
    "morning": ["Visit the Eiffel Tower", "Walk along the Seine River"],
    "afternoon": ["Explore the Louvre Museum", "See the Arc de Triomphe"],
    "evening": ["Dinner at a Montmartre bistro", "Evening stroll in Le Marais"],
    "food_recommendation": "Try authentic French baguettes and croissants",
    "cultural_highlight": "Paris is known as the City of Light"
  }}
}}{additional_context}"""

    model = genai.GenerativeModel('models/gemini-2.5-flash')
    response = model.generate_content(prompt)
    text = response.text

    # Remove markdown code blocks if present
    text = re.sub(r'```json\n?', '', text)
    text = re.sub(r'```\n?', '', text)
    text = text.strip()

    # Try to parse JSON; fallback to raw text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {'raw': text}
