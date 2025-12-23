import re
import spacy
import urllib.parse
import aiohttp
import asyncio

# Load spaCy model for POS tagging
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    # Fallback if model not installed
    nlp = None


async def verify_wikipedia_link(url: str, session: aiohttp.ClientSession) -> bool:
    """
    Verify that a Wikipedia URL actually exists and is not a 404 page.
    Returns True if the page exists, False otherwise.
    """
    try:
        headers = {
            'User-Agent': 'AI-Travel-Planner/1.0 (Educational Project)'
        }
        async with session.head(url, headers=headers, timeout=aiohttp.ClientTimeout(total=2), allow_redirects=True) as response:
            return response.status == 200
    except:
        return False


async def get_wikipedia_link(location: str, session: aiohttp.ClientSession) -> str:
    """
    Construct a Wikipedia URL from the location name and verify it exists.
    Returns the URL only if the page actually exists, None otherwise.
    """
    if not location or len(location) < 3:
        return None

    # Replace spaces with underscores for Wikipedia URL format
    formatted_topic = location.replace(' ', '_')

    # URL encode special characters
    formatted_topic = urllib.parse.quote(formatted_topic, safe='_')

    # Construct Wikipedia URL
    wiki_url = f'https://en.wikipedia.org/wiki/{formatted_topic}'

    # Verify the link actually works
    if await verify_wikipedia_link(wiki_url, session):
        return wiki_url

    # Try with first letter capitalized variant
    if location and location[0].islower():
        capitalized = location[0].upper() + location[1:]
        formatted_topic = urllib.parse.quote(capitalized.replace(' ', '_'), safe='_')
        alt_url = f'https://en.wikipedia.org/wiki/{formatted_topic}'
        if await verify_wikipedia_link(alt_url, session):
            return alt_url

    return None


def extract_attraction_name(activity: str) -> str:
    """
    Extract attraction name from activity description using spaCy NER to capture full entity names.
    """
    # Skip common company/service provider names that shouldn't be hyperlinked
    skip_companies = {
        'budget', 'hertz', 'avis', 'enterprise', 'thrifty', 'national', 'alamo', 'dollar', 'sixt',
        'marriott', 'hilton', 'hyatt', 'sheraton', 'holiday inn', 'best western', 'radisson',
        'airbnb', 'booking.com', 'expedia', 'hotels.com', 'tripadvisor',
        'uber', 'lyft', 'grab', 'ola', 'bolt',
        'mcdonald', 'starbucks', 'kfc', 'subway', 'pizza hut', 'domino',
        'walmart', 'target', 'costco', 'tesco', 'carrefour'
    }

    if not nlp:
        # Fallback to regex if spaCy not available
        return extract_attraction_name_regex(activity)

    doc = nlp(activity)

    # First, try to find named entities (GPE, LOC, FAC, ORG)
    # These are proper nouns that spaCy recognizes as places/landmarks
    candidates = []

    for ent in doc.ents:
        # Look for location-related entities
        if ent.label_ in ['GPE', 'LOC', 'FAC', 'ORG', 'PERSON']:
            text = ent.text.strip()
            # Skip if it's a known company/service provider
            if text.lower() in skip_companies:
                continue
            # Filter out common non-landmark words
            if len(text) > 3 and len(text) < 60:
                # Skip if it's just a time or date
                if ent.label_ not in ['DATE', 'TIME', 'CARDINAL', 'ORDINAL']:
                    candidates.append((text, ent.start_char, ent.label_))

    # If we found entities, prefer FAC > LOC > GPE > ORG
    if candidates:
        # Sort by priority (FAC first, then LOC, GPE, ORG, PERSON last)
        priority = {'FAC': 0, 'LOC': 1, 'GPE': 2, 'ORG': 3, 'PERSON': 4}
        candidates.sort(key=lambda x: (priority.get(x[2], 10), x[1]))
        return candidates[0][0]

    # If no entities found, look for consecutive proper nouns
    # This catches cases like "Hell's Kitchen" that might not be recognized as entities
    proper_nouns = []
    current_phrase = []

    for token in doc:
        if token.pos_ == 'PROPN':
            current_phrase.append(token.text)
        else:
            if current_phrase:
                phrase = ' '.join(current_phrase)
                # Skip if it's a known company/service provider
                if phrase.lower() in skip_companies:
                    current_phrase = []
                    continue
                # Skip action verbs at the start
                action_verbs = ['Take', 'Visit', 'Explore', 'Enjoy', 'Experience', 'Discover',
                               'Wander', 'Stroll', 'Ascend', 'Relax', 'Browse', 'Witness',
                               'Find', 'Dive', 'Immerse', 'Have', 'Walk']
                if phrase not in action_verbs and len(phrase) > 3:
                    proper_nouns.append(phrase)
                current_phrase = []

    # Don't forget the last phrase if sentence ends with proper nouns
    if current_phrase:
        phrase = ' '.join(current_phrase)
        if len(phrase) > 3:
            proper_nouns.append(phrase)

    # Return the first valid proper noun phrase
    if proper_nouns:
        return proper_nouns[0]

    # Final fallback to regex-based extraction
    return extract_attraction_name_regex(activity)


def extract_attraction_name_regex(activity: str) -> str:
    """
    Fallback regex-based extraction when spaCy is not available or doesn't find entities.
    """
    # Pattern 1: Look for landmark names with specific suffixes
    landmark_pattern = r'(?:the\s+)?([A-Z][\w\'\s-]+?(?:Temple|Shrine|Museum|Tower|Palace|Castle|Park|Garden|Gardens|Square|Market|Building|Hills|Observatory|Crossing|Street|Gate|Hall|Center|Centre|District|Skytree|Bridge|River|Station|Memorial|Statue|Theatre|Island|Kitchen))'
    match = re.search(landmark_pattern, activity)
    if match:
        place = match.group(1).strip()
        place = re.sub(r',.*$', '', place)
        if 4 < len(place) < 60:
            return place

    # Pattern 2: Look for "of/in/at/to [Place]" patterns
    context_pattern = r'(?:of|in|at|from|to)\s+(?:the\s+)?([A-Z][\w\'\s-]+(?:\s+(?:and|&)\s+[A-Z][\w\'\s-]+)?)'
    context_match = re.search(context_pattern, activity)
    if context_match:
        place = context_match.group(1).strip()
        # Clean up trailing words
        place = re.sub(r'\s+(?:and\s+[a-z].*|area|region)$', '', place, flags=re.IGNORECASE)
        if len(place) > 3 and len(place) < 60:
            return place

    # Pattern 3: Match proper noun phrases (2-5 capitalized words, including apostrophes)
    proper_noun_pattern = r'([A-Z][\w\']+(?:\s+[A-Z][\w\']+){1,4})'
    matches = re.findall(proper_noun_pattern, activity)
    if matches:
        for place in matches:
            place = place.strip()
            # Filter out verb phrases
            action_verbs = ['Take', 'Visit', 'Explore', 'Enjoy', 'Experience', 'Discover',
                           'Wander', 'Stroll', 'Ascend', 'Relax', 'Browse', 'Witness',
                           'Find', 'Dive', 'Immerse', 'Have', 'Walk']
            if place.split()[0] not in action_verbs and 5 < len(place) < 60:
                return place

    return None


async def process_activities(activities, session: aiohttp.ClientSession):
    """
    Process activities to add Wikipedia links.
    """
    if not activities:
        return activities

    # If it's a string, return as is
    if isinstance(activities, str):
        return activities

    # If it's an array of strings, convert to activity objects with Wikipedia links
    if isinstance(activities, list):
        processed_activities = []

        for activity in activities:
            if isinstance(activity, str):
                attraction_name = extract_attraction_name(activity)

                # Only create Wikipedia link if we successfully extracted an attraction name
                if attraction_name and len(attraction_name) > 4:
                    wiki_link = await get_wikipedia_link(attraction_name, session)

                    if wiki_link:
                        print(f'✓ Verified Wikipedia link for "{attraction_name}": {wiki_link}')
                        processed_activities.append({'text': activity, 'wiki': wiki_link, 'attractionName': attraction_name})
                    else:
                        print(f'✗ No valid Wikipedia page found for "{attraction_name}"')
                        processed_activities.append({'text': activity})
                else:
                    # Couldn't extract a good attraction name, skip Wikipedia link
                    processed_activities.append({'text': activity})
            else:
                # Already an object, keep as is
                processed_activities.append(activity)

        return processed_activities

    return activities


async def add_wikipedia_links(itinerary: dict) -> dict:
    """
    Add Wikipedia links to locations and attractions in the itinerary.
    Uses async HTTP requests for faster processing.
    """
    # If raw format, return as is
    if 'raw' in itinerary:
        return itinerary

    updated_itinerary = {}

    # Create a single aiohttp session for all requests (connection pooling)
    timeout = aiohttp.ClientTimeout(total=30)  # Overall timeout for all wiki requests
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for day_key, day in itinerary.items():
            updated_itinerary[day_key] = {**day}

            # If this day has a location, create Wikipedia link
            if 'location' in day and day['location']:
                wiki_link = await get_wikipedia_link(day['location'], session)
                if wiki_link:
                    updated_itinerary[day_key]['location_wiki'] = wiki_link
                    print(f'✓ Verified Wikipedia link for {day["location"]}: {wiki_link}')
                else:
                    print(f'✗ No valid Wikipedia page found for location "{day["location"]}"')

            # Process activities for morning, afternoon, and evening
            if 'morning' in day:
                updated_itinerary[day_key]['morning'] = await process_activities(day['morning'], session)
            if 'afternoon' in day:
                updated_itinerary[day_key]['afternoon'] = await process_activities(day['afternoon'], session)
            if 'evening' in day:
                updated_itinerary[day_key]['evening'] = await process_activities(day['evening'], session)

    return updated_itinerary
