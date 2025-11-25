import re
import spacy

# Load spaCy model for POS tagging
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    # Fallback if model not installed
    nlp = None


def get_wikipedia_link(location: str) -> str:
    """
    Construct a Wikipedia URL from the location name.
    Simply replaces spaces with underscores and creates the URL.
    """
    if not location or len(location) < 3:
        return None

    # Replace spaces with underscores for Wikipedia URL format
    formatted_topic = location.replace(' ', '_')

    # URL encode special characters
    import urllib.parse
    formatted_topic = urllib.parse.quote(formatted_topic, safe='_')

    # Construct Wikipedia URL
    wiki_url = f'https://en.wikipedia.org/wiki/{formatted_topic}'

    return wiki_url


def extract_attraction_name(activity: str) -> str:
    """
    Extract attraction name from activity description using spaCy POS tagging and pattern matching.
    """
    # Pattern 1: Look for "of/in/at [Place]" patterns first
    context_pattern = r'(?:of|in|at|from|to)\s+([A-Z][\w-]+(?:\s+[A-Z][\w-]+)?(?:\s+[A-Z][\w-]+)?)'
    context_match = re.search(context_pattern, activity)
    if context_match:
        place = context_match.group(1).strip()
        place = re.sub(r'\s+(?:area|region)$', '', place, flags=re.IGNORECASE)
        if len(place) > 3 and len(place) < 40:
            return place

    # Use spaCy to remove verb phrases at the start
    cleaned = activity
    if nlp:
        doc = nlp(activity)

        # Find the first proper noun (prioritize PROPN over NOUN)
        start_index = 0
        propn_index = None

        for i, token in enumerate(doc):
            # Track the first proper noun we find
            if token.pos_ == 'PROPN' and propn_index is None:
                propn_index = token.idx

            # Skip verbs, auxiliaries, adverbs at the start
            if token.pos_ in ['VERB', 'AUX', 'ADV']:
                continue
            # Skip prepositions and conjunctions at the start
            elif token.pos_ in ['ADP', 'CCONJ'] and i < 5:
                continue
            # Skip "the", "a", "an" determiners
            elif token.pos_ == 'DET':
                continue
            # Skip common verbs disguised as nouns (shop, stroll, etc.)
            elif token.pos_ == 'NOUN' and token.text.lower() in ['shop', 'stroll', 'walk', 'visit', 'photo', 'dinner', 'lunch', 'breakfast']:
                continue
            # Found a proper noun - this is the attraction name
            elif token.pos_ == 'PROPN':
                start_index = token.idx
                break

        # If we found a proper noun, use it; otherwise try the first PROPN we saw
        if start_index > 0:
            cleaned = activity[start_index:].strip()
        elif propn_index is not None and propn_index > 0:
            cleaned = activity[propn_index:].strip()
    else:
        # Fallback to regex if spaCy not available
        cleaned = re.sub(r'^[A-Z][a-z]+(?:\s+(?:and\s+)?[a-z]+)*\s+(?:the\s+)?(?=[A-Z])', '', activity)
        if cleaned == activity:
            cleaned = re.sub(r'^[A-Z][a-z]+(?:\s+(?:and\s+)?[a-z]+)*\s+(?:the\s+)?', '', activity)
            if cleaned and not cleaned[0].isupper():
                cleaned = activity

    # Remove adjectives at the start (including "the" before them)
    cleaned = re.sub(r'^(?:the\s+)?(?:beautiful|peaceful|iconic|world-famous|trendy|lively|unique|vibrant|majestic|historic|upscale|traditional|contemporary|quirky|famous|serene|life-sized|multi-story|tranquil|narrow|vibrant)\s+(?:and\s+\w+\s+)?', '', cleaned, flags=re.IGNORECASE)

    # Pattern 2: Match landmark names with specific suffixes
    landmark_pattern = r'^([A-Z][\w\s-]+?(?:Temple|Shrine|Museum|Tower|Palace|Castle|Park|Garden|Gardens|Square|Market|Building|Hills|Observatory|Crossing|Street|Gate|Hall|Center|Centre|District|Skytree|Bridge|River|Station|Memorial|Statue|Theatre))'
    match = re.search(landmark_pattern, cleaned)
    if match:
        place = match.group(1).strip()
        place = re.sub(r',.*$', '', place)
        place = re.sub(r'\s+(?:dedicated to|featuring|known for|offering|including|home to|one of|a Shinto shrine|a serene oasis|a traditional landscape garden).+$', '', place, flags=re.IGNORECASE)
        if 4 < len(place) < 60:
            return place

    # Pattern 3: Match proper noun phrases (2-5 capitalized words)
    proper_noun_pattern = r'^([A-Z][\w-]+(?:\s+[A-Z][\w-]+){1,4})'
    match = re.search(proper_noun_pattern, cleaned)
    if match:
        place = match.group(1).strip()
        # Remove common trailing words
        place = re.sub(r'\s+(?:area|from|come|at|for|in|near|and|surrounding the|district).*$', '', place, flags=re.IGNORECASE)
        place = re.sub(r',.*$', '', place)

        # Filter out verb phrases and non-places
        action_verbs = ['Take', 'Visit', 'Explore', 'Enjoy', 'Experience', 'Discover', 'Wander', 'Stroll', 'Ascend', 'Relax', 'Browse', 'Witness', 'Find', 'Dive', 'Immerse', 'Have', 'Walk']
        if place.split()[0] not in action_verbs and 5 < len(place) < 50:
            words = place.split()
            if len(words) >= 2:
                return place

    # Fallback: return first capitalized sequence
    fallback_match = re.search(r'([A-Z][\w\s]+?)(?:\s*[,.(]|$)', cleaned)
    if fallback_match:
        place = fallback_match.group(1).strip()
        if 5 < len(place) < 40:
            return place

    return None


async def process_activities(activities):
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
                    wiki_link = get_wikipedia_link(attraction_name)

                    if wiki_link:
                        print(f'✓ Created Wikipedia link for "{attraction_name}": {wiki_link}')
                        processed_activities.append({'text': activity, 'wiki': wiki_link, 'attractionName': attraction_name})
                    else:
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
    """
    # If raw format, return as is
    if 'raw' in itinerary:
        return itinerary

    updated_itinerary = {}

    for day_key, day in itinerary.items():
        updated_itinerary[day_key] = {**day}

        # If this day has a location, create Wikipedia link
        if 'location' in day and day['location']:
            wiki_link = get_wikipedia_link(day['location'])
            if wiki_link:
                updated_itinerary[day_key]['location_wiki'] = wiki_link
                print(f'✓ Created Wikipedia link for {day["location"]}: {wiki_link}')

        # Process activities for morning, afternoon, and evening
        if 'morning' in day:
            updated_itinerary[day_key]['morning'] = await process_activities(day['morning'])
        if 'afternoon' in day:
            updated_itinerary[day_key]['afternoon'] = await process_activities(day['afternoon'])
        if 'evening' in day:
            updated_itinerary[day_key]['evening'] = await process_activities(day['evening'])

    return updated_itinerary
