import asyncio
import re
import urllib.parse

import aiohttp
import spacy

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


async def get_wikipedia_link(location: str, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore) -> str:
    """
    Construct a Wikipedia URL from the location name and verify it exists.
    Returns the URL only if the page actually exists, None otherwise.
    Uses a semaphore to cap concurrent requests.
    """
    if not location or len(location) < 3:
        return None

    async with semaphore:
        formatted_topic = urllib.parse.quote(location.replace(' ', '_'), safe='_')
        wiki_url = f'https://en.wikipedia.org/wiki/{formatted_topic}'

        if await verify_wikipedia_link(wiki_url, session):
            return wiki_url

        # Try with first letter capitalized
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


async def add_wikipedia_links(itinerary: dict) -> dict:
    """
    Add Wikipedia links to locations and attractions in the itinerary.
    All link checks run concurrently (not sequentially) using asyncio.gather.
    A semaphore caps concurrent Wikipedia HEAD requests to avoid overwhelming the API.
    """
    if 'raw' in itinerary:
        return itinerary

    # Limit concurrent HEAD requests to Wikipedia (avoids rate-limiting)
    semaphore = asyncio.Semaphore(10)
    timeout = aiohttp.ClientTimeout(total=20)

    async with aiohttp.ClientSession(timeout=timeout) as session:

        async def get_wiki(location: str) -> str:
            return await get_wikipedia_link(location, session, semaphore)

        async def process_activity(activity) -> dict:
            """Process a single activity: extract name and fetch wiki link concurrently."""
            if isinstance(activity, str):
                attraction_name = extract_attraction_name(activity)
                if attraction_name and len(attraction_name) > 4:
                    wiki_link = await get_wiki(attraction_name)
                    if wiki_link:
                        return {'text': activity, 'wiki': wiki_link, 'attractionName': attraction_name}
                return {'text': activity}
            # Already an object — keep as-is
            return activity

        async def process_period(activities) -> list:
            """Process all activities in a period concurrently."""
            if not activities or isinstance(activities, str):
                return activities
            return list(await asyncio.gather(*[process_activity(a) for a in activities]))

        async def process_day(day_key: str, day: dict):
            """Process a day: location wiki + all periods run in parallel."""
            day_result = {**day}

            # Build all tasks for this day
            period_keys = [p for p in ('morning', 'afternoon', 'evening') if isinstance(day.get(p), list)]
            location = day.get('location') if day.get('location') else None

            # Run location wiki + all periods concurrently
            tasks = []
            task_labels = []

            if location:
                tasks.append(get_wiki(location))
                task_labels.append('__location__')

            for period in period_keys:
                tasks.append(process_period(day[period]))
                task_labels.append(period)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for label, result in zip(task_labels, results):
                if isinstance(result, Exception):
                    continue
                if label == '__location__':
                    if result:
                        day_result['location_wiki'] = result
                else:
                    day_result[label] = result

            return day_key, day_result

        # Process ALL days concurrently
        day_tasks = [process_day(k, v) for k, v in itinerary.items()]
        day_results = await asyncio.gather(*day_tasks, return_exceptions=True)

        updated = {}
        for result in day_results:
            if not isinstance(result, Exception):
                day_key, day_data = result
                updated[day_key] = day_data

        return updated
