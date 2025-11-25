import aiohttp
import asyncio
import re
from agents.wiki_agent import get_wikipedia_link


async def map_agent(country: str, itinerary: dict, locations: str = None) -> list:
    """
    Generate map data by geocoding attractions from the itinerary.
    Optimized for speed with concurrent requests.
    """
    # Extract attraction names from itinerary recommendations
    attraction_names = extract_attractions(itinerary)

    if not attraction_names:
        print('No attractions found in itinerary')
        return []

    print(f'Geocoding {len(attraction_names)} attractions from itinerary...')

    # Build geocoding context
    if locations and locations.strip():
        geocode_context = f"{locations.split(',')[0].strip()}, {country}"
    else:
        geocode_context = country

    async def geocode_single(session, name):
        """Geocode a single attraction with rate limiting."""
        try:
            # Search for the attraction with country context
            search_query = f'{name}, {geocode_context}'
            geocode_url = f'https://nominatim.openstreetmap.org/search?q={search_query}&format=json&limit=1'

            headers = {'User-Agent': 'AI-Travel-Planner/1.0'}

            # Small delay before request to respect rate limits
            await asyncio.sleep(0.15)

            async with session.get(geocode_url, headers=headers) as response:
                data = await response.json()

                if data and len(data) > 0:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])

                    # Generate Wikipedia link for this attraction
                    wiki_link = get_wikipedia_link(name)

                    print(f'✓ Geocoded: {name}')
                    return {
                        'name': name,
                        'type': 'attraction',
                        'location': {
                            'lat': lat,
                            'lng': lon
                        },
                        'wiki': wiki_link
                    }
                else:
                    print(f'✗ Could not geocode: {name}')
                    return None

        except Exception as e:
            print(f'Error geocoding {name}: {str(e)}')
            return None

    # Run all geocoding requests concurrently with timeout
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [geocode_single(session, name) for name in attraction_names]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out None results and exceptions
        attractions = [r for r in results if r is not None and not isinstance(r, Exception)]

    print(f'Successfully geocoded {len(attractions)} attractions')
    return attractions


def extract_attractions(itinerary: dict) -> list:
    """
    Extract attraction/place names from itinerary activities.
    """
    attractions = set()

    # If raw format, return empty
    if 'raw' in itinerary:
        return []

    # Extract from each day's activities
    for day_key, day in itinerary.items():
        if day_key == 'raw':
            continue

        # Add location if specified for the day
        if 'location' in day and isinstance(day['location'], str) and day['location'].strip():
            attractions.add(day['location'].strip())

        # Process morning, afternoon, evening arrays
        activities = []
        if 'morning' in day and isinstance(day['morning'], list):
            activities.extend(day['morning'])
        if 'afternoon' in day and isinstance(day['afternoon'], list):
            activities.extend(day['afternoon'])
        if 'evening' in day and isinstance(day['evening'], list):
            activities.extend(day['evening'])

        for activity in activities:
            # Handle activity as dict (with wiki links) or string
            activity_text = activity['text'] if isinstance(activity, dict) and 'text' in activity else activity
            if isinstance(activity_text, str):
                extracted = extract_place_name(activity_text)
                if extracted:
                    attractions.add(extracted)

    print(f'📍 Extracted {len(attractions)} unique attractions: {", ".join(list(attractions)[:10])}{"..." if len(attractions) > 10 else ""}')

    # Clean up any remaining action verbs from attraction names before geocoding
    cleaned_attractions = []
    for attraction in attractions:
        # Remove action verbs at the start
        cleaned = re.sub(r'^(?:Visit|Explore|See|Browse|Stroll through|Witness|Ascend|Experience|Enjoy)\s+(?:the\s+)?', '', attraction, flags=re.IGNORECASE)
        cleaned = re.sub(r'^(?:iconic|serene|tranquil)\s+', '', cleaned, flags=re.IGNORECASE)
        cleaned_attractions.append(cleaned)

    # Limit to top 8 attractions for faster geocoding (prevents delays)
    # Prioritize: keep unique landmarks, remove generic activities
    if len(cleaned_attractions) > 8:
        print(f'⚡ Limiting to top 8 attractions for faster response time')
        cleaned_attractions = cleaned_attractions[:8]

    return cleaned_attractions


def extract_place_name(activity: str) -> str:
    """
    Extract actual place name from activity description.
    Focuses on finding proper nouns that are landmarks.
    """
    # Pattern 0: Look for "of/in [Place]" patterns first
    context_pattern = r'(?:of|in|at|from|to)\s+([A-Z][\w-]+(?:\s+[A-Z][\w-]+)?(?:\s+[A-Z][\w-]+)?)'
    context_match = re.search(context_pattern, activity)
    if context_match:
        place = context_match.group(1).strip()
        # Remove common non-place endings
        place = re.sub(r'\s+(?:area|region)$', '', place, flags=re.IGNORECASE)
        # Check if it looks like a place name
        if len(place) > 3 and len(place) < 30 and place not in ['Japan', 'Tokyo', 'Emperor', 'Empress']:
            # Only return if it's at least 2 capitalized words or a single short word
            words = place.split()
            if len(words) >= 1 and (len(words) > 1 or len(place) < 15):
                return place

    # Remove common action phrases at the start
    cleaned = re.sub(r'^(?:Visit|Explore|Tour|See|Discover|Walk through|Stroll through|Stroll and shop along|Wander through|Browse|Admire|Experience|Ascend|Descend|Relax and stroll through|Take a photo (?:with|of|at)|Take photos of|Enjoy|Immerse yourself in|Find tranquility at|Witness|Dive into the world of)\s+(?:the\s+)?', '', activity, flags=re.IGNORECASE)

    # Remove adjectives at the start
    cleaned = re.sub(r'^(?:beautiful|peaceful|iconic|world-famous|trendy|lively|unique|vibrant|majestic|historic|upscale|traditional|contemporary|quirky|famous|serene|life-sized|multi-story)\s+(?:and\s+\w+\s+)?', '', cleaned, flags=re.IGNORECASE)

    # Pattern 1: Match landmark names with specific suffixes
    landmark_pattern = r'^([A-Z][\w\s-]+?(?:Temple|Shrine|Museum|Tower|Palace|Castle|Park|Garden|Gardens|Square|Market|Building|Hills|Observatory|Crossing|Street|Gate|Hall|Center|Centre|District|Skytree|Bridge|River|Station|Memorial|Statue))'
    match = re.search(landmark_pattern, cleaned)
    if match:
        place = match.group(1).strip()
        # Clean up
        place = re.sub(r',.*$', '', place)  # Remove everything after comma
        place = re.sub(r'\s+(?:dedicated to|featuring|known for|offering|including|home to|one of).+$', '', place, flags=re.IGNORECASE)
        if 4 < len(place) < 60:
            return place

    # Pattern 2: Match proper noun phrases (2-6 capitalized words)
    proper_noun_pattern = r'^([A-Z][\w-]+(?:\s+[A-Z][\w-]+){1,5})'
    match = re.search(proper_noun_pattern, cleaned)
    if match:
        place = match.group(1).strip()
        # Remove common trailing words that aren't part of place names
        place = re.sub(r'\s+(?:area|from|come|at|for|in|near|and).*$', '', place, flags=re.IGNORECASE)
        place = re.sub(r',.*$', '', place)

        # Filter out verb phrases and non-places
        action_verbs = ['Take', 'Visit', 'Explore', 'Enjoy', 'Experience', 'Discover', 'Wander', 'Stroll', 'Ascend', 'Relax', 'Browse', 'Witness', 'Find', 'Dive', 'Immerse']
        if place.split()[0] not in action_verbs and 5 < len(place) < 60:
            words = place.split()
            # Require at least 2 words for a proper place name
            if len(words) >= 2:
                return place

    return None
