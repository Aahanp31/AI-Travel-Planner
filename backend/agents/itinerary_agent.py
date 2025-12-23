import os
import re
import json
import google.generativeai as genai

genai.configure(api_key=os.getenv('GEMINI_API_KEY', ''))


async def itinerary_agent(country: str, locations: str = None, days: int = 3, origin: str = '', additional_details: str = None, detail_level: str = 'standard') -> dict:
    """
    Generate a travel itinerary using Google Gemini AI.
    Args:
        country: The country to visit (required)
        locations: Optional comma-separated list of specific cities/locations
        days: Number of days for the trip
        origin: Departure city
        additional_details: User preferences and requirements
        detail_level: Level of detail - 'quick', 'standard', or 'comprehensive'
    """
    # Determine activity count and detail based on detail_level
    if detail_level == 'quick':
        activities_per_period = "2 activities"
        detail_instruction = "Focus on top highlights only. Keep descriptions concise (1 sentence per activity)."
    elif detail_level == 'comprehensive':
        activities_per_period = "3-4 activities with alternatives"
        detail_instruction = "Provide detailed descriptions and suggest backup options for weather/closure."
    else:  # standard
        activities_per_period = "2-3 activities"
        detail_instruction = "Provide balanced detail with engaging descriptions."

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

CRITICAL - USER HAS EXISTING RESERVATIONS AND SCHEDULE:
The traveler has already made bookings and has scheduled activities. You MUST build the itinerary around these:
{additional_details}

MANDATORY INSTRUCTIONS - BE SMART ABOUT EXISTING PLANS:

1. IDENTIFY logistics and time-sensitive activities:
   - Look for ANY activity with a specific time (flights, tours, reservations, rentals)
   - Identify check-ins, check-outs, pickups, returns, departures, arrivals
   - Note what requires location changes or transportation

2. INCLUDE all user's scheduled activities IN THE ITINERARY:
   - Don't ignore or skip their pre-booked items
   - Add them to the appropriate time slot with realistic duration estimates
   - Mark pre-booked items by making them **bold** using markdown (e.g., "Pick up rental car from **Budget**")
   - DON'T add labels like "pre-booked" or booking source details - just bold the item itself

3. THINK ABOUT LOGISTICS FLOW:

   Transportation changes (car pickup/return, arriving/departing):
   - BEFORE: Plan activities near that location, allow travel time
   - AFTER: Consider new transportation situation (now have car, or lost car, or at new location)

   Flights/trains/buses:
   - BEFORE: Wind down activities 2-4 hours early, allow airport/station travel time
   - AFTER arriving: Allow time for baggage, customs, getting to accommodation

   Check-ins/Check-outs:
   - Factor in luggage - don't suggest hiking with suitcases
   - Allow time for the process itself (15-30 min)

   Pre-booked tours/activities:
   - Respect the timing and location
   - Only suggest complementary activities nearby if time permits

4. REALISTIC TIME BUDGETING:
   - Be honest about how long activities take
   - Include travel time between locations
   - Don't overpack - leave breathing room
   - If a time slot is mostly occupied by logistics, DON'T squeeze in major attractions

5. FILL ONLY FREE TIME INTELLIGENTLY:
   - Look for actual gaps in the schedule
   - Suggest activities appropriate to available time and location
   - Consider energy levels (don't schedule intense activity after red-eye flight)

6. PRACTICAL CONSTRAINTS:
   - Without a car: activities must be walkable or include transportation method
   - With a car: can suggest farther destinations, but include driving time
   - Late check-out: can suggest morning activities in that city
   - Early check-in: plan for potential luggage storage if arriving before check-in time

7. For days with pre-booked stays, use that location as the base
8. DO NOT suggest booking what they already have
9. DO NOT include booking source information (e.g., "booking via Expedia", "reserved through Booking.com")
10. Make activities descriptive and engaging, keeping pre-booked items natural looking
"""

    # Activity balancing instructions (shared across all modes)
    activity_balance_instructions = f"""
ACTIVITY BALANCING - CREATE A WELL-PACED DAY:

1. VARY INTENSITY across time periods:
   - DON'T schedule 2+ intense/tiring activities in the same period
   - Mix heavy attractions (museums, theme parks) with lighter ones (cafes, markets, short walks)
   - Examples of HEAVY activities: Theme parks, large museums, long hikes, adventure sports
   - Examples of LIGHT activities: Cafes, viewpoints, markets, short walks, gardens

2. REALISTIC ENERGY FLOW:
   - Morning: Can be more intense (people are fresh)
   - Afternoon: Mix of activities, factor in lunch and potential fatigue
   - Evening: Lighter activities, dining, relaxation, night views

3. AVOID OVERLOADING:
   - If morning has a major museum (2-3 hours), afternoon should be lighter
   - If afternoon includes intense activity, keep evening relaxed
   - Don't schedule back-to-back indoor/sitting activities (boring)
   - Don't schedule back-to-back outdoor/walking activities (exhausting)

4. LOGICAL GROUPING:
   - Group nearby attractions together in the same time period
   - Include travel time between distant locations
   - Consider opening hours (some places close early)

5. DETAIL LEVEL: {detail_level}
   - Include {activities_per_period} per time period
   - {detail_instruction}
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

{activity_balance_instructions}

MULTI-CITY ITINERARY INSTRUCTIONS:
1. Plan a logical route that minimizes backtracking - organize cities geographically
2. For each location change, include transportation details:
   - Method (train, bus, flight, car rental)
   - Approximate travel time
   - Estimated cost in BOTH local currency AND {origin} currency (with conversion)
3. Format each time period (morning, afternoon, evening) as an ARRAY of activities
4. Each activity should be descriptive and actionable (e.g., "Visit the Sky Tower observation deck for 360-degree city views")
5. Include realistic, well-known attractions for each city
6. Group consecutive days in the same city together

For each day, provide:
- location: The city/area for this day (string)
- morning: Array of 2-3 detailed morning activities
- afternoon: Array of 2-3 detailed afternoon activities
- evening: Array of 2-3 detailed evening activities
- food_recommendation: A specific local dish or restaurant recommendation with brief description
- cultural_highlight: An interesting cultural fact, tradition, or must-see cultural site with context
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

{activity_balance_instructions}

MULTI-CITY ITINERARY INSTRUCTIONS:
1. Plan a logical route that minimizes backtracking - organize cities geographically
2. For each location change, include transportation details:
   - Method (train, bus, flight, car rental)
   - Approximate travel time
   - Estimated cost in BOTH local currency AND {origin} currency (with conversion)
3. Format each time period (morning, afternoon, evening) as an ARRAY of 2-3 specific activities
4. Each activity should be descriptive and actionable (e.g., "Visit the Sky Tower observation deck for 360-degree city views")
5. Include realistic, well-known attractions for each city
6. Group consecutive days in the same city together

For each day, provide:
- location: The city/area for this day (string)
- morning: Array of 2-3 detailed morning activities
- afternoon: Array of 2-3 detailed afternoon activities
- evening: Array of 2-3 detailed evening activities
- food_recommendation: A specific local dish or restaurant recommendation with brief description
- cultural_highlight: An interesting cultural fact, tradition, or must-see cultural site with context
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
3. Format each time period (morning, afternoon, evening) as an ARRAY of activities
4. Each activity should be clear and descriptive (e.g., "Visit the Eiffel Tower observation deck for panoramic views of Paris")
5. Include realistic, well-known attractions for the destination

{activity_balance_instructions}

For each day, provide:
- morning: Array of 2-3 detailed morning activities
- afternoon: Array of 2-3 detailed afternoon activities
- evening: Array of 2-3 detailed evening activities
- food_recommendation: A specific local dish or restaurant type with brief description
- cultural_highlight: An interesting cultural fact, tradition, or attraction with context

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

    # Configure model for faster response with reasonable quality
    # For large custom itineraries, we need more tokens
    generation_config = genai.types.GenerationConfig(
        temperature=0.7,
        max_output_tokens=8192,  # Increased for detailed multi-day itineraries with custom preferences
    )

    model = genai.GenerativeModel(
        'models/gemini-2.5-flash',
        generation_config=generation_config
    )

    response = model.generate_content(prompt)
    text = response.text

    # Remove markdown code blocks if present
    text = re.sub(r'```json\n?', '', text)
    text = re.sub(r'```\n?', '', text)
    text = text.strip()

    # Try to parse JSON; fallback to raw text
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Response length: {len(text)} characters")

        # Check if response was likely truncated
        if len(text) > 7000 and not text.rstrip().endswith('}'):
            print("WARNING: Response appears to be truncated. Consider increasing max_output_tokens.")

        # Try to find where valid JSON ends
        # Sometimes we can salvage partial JSON
        try:
            # Find the last complete day entry
            last_day_match = re.search(r'"day\d+":\s*\{[^}]*\}', text)
            if last_day_match:
                # Try to construct valid JSON from what we have
                truncated_point = last_day_match.end()
                salvaged_text = text[:truncated_point] + '\n}'
                return json.loads(salvaged_text)
        except:
            pass

        print(f"Could not parse response. First 500 chars: {text[:500]}")
        return {'raw': text, 'error': 'Failed to parse itinerary response'}
