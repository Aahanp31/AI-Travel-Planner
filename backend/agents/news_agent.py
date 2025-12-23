import os
import aiohttp


# Country name to ISO 3166-1 alpha-2 code mapping for NewsData.io API
COUNTRY_CODES = {
    'united states': 'us', 'usa': 'us', 'america': 'us',
    'united kingdom': 'gb', 'uk': 'gb', 'england': 'gb', 'britain': 'gb',
    'canada': 'ca',
    'australia': 'au',
    'new zealand': 'nz',
    'japan': 'jp',
    'china': 'cn',
    'india': 'in',
    'france': 'fr',
    'germany': 'de',
    'italy': 'it',
    'spain': 'es',
    'mexico': 'mx',
    'brazil': 'br',
    'argentina': 'ar',
    'south korea': 'kr', 'korea': 'kr',
    'thailand': 'th',
    'singapore': 'sg',
    'malaysia': 'my',
    'indonesia': 'id',
    'philippines': 'ph',
    'vietnam': 'vn',
    'uae': 'ae', 'united arab emirates': 'ae', 'dubai': 'ae',
    'saudi arabia': 'sa',
    'egypt': 'eg',
    'south africa': 'za',
    'turkey': 'tr',
    'greece': 'gr',
    'portugal': 'pt',
    'netherlands': 'nl',
    'belgium': 'be',
    'switzerland': 'ch',
    'austria': 'at',
    'sweden': 'se',
    'norway': 'no',
    'denmark': 'dk',
    'finland': 'fi',
    'poland': 'pl',
    'russia': 'ru',
    'ireland': 'ie',
    'iceland': 'is',
    'czech republic': 'cz',
    'hungary': 'hu',
    'croatia': 'hr',
    'morocco': 'ma',
    'peru': 'pe',
    'chile': 'cl',
    'colombia': 'co',
    'venezuela': 've',
    'cuba': 'cu',
    'jamaica': 'jm',
    'costa rica': 'cr',
    'panama': 'pa',
}


def get_country_code(country: str) -> str:
    """Convert country name to ISO country code."""
    return COUNTRY_CODES.get(country.lower().strip())


async def news_agent(country: str, locations: str = None) -> list:
    """
    Fetch latest local news articles for a destination using NewsData.io API.
    Filters by country to ensure news is specific to the destination.
    """
    api_key = os.getenv('NEWS_API_KEY', '')

    if not api_key:
        print('NEWS_API_KEY not found in environment variables')
        return []

    # Get country code for filtering
    country_code = get_country_code(country)

    # Build search query for travel-relevant news
    if locations and locations.strip():
        # Focus on specific cities/locations mentioned
        city_list = [loc.strip() for loc in locations.split(',')]
        search_query = ' OR '.join(city_list)
    else:
        # General country news with travel focus
        search_query = f"{country} tourism OR travel OR attractions OR events OR festival"

    try:
        # NewsData.io API endpoint
        url = 'https://newsdata.io/api/1/news'
        params = {
            'apikey': api_key,
            'q': search_query,
            'language': 'en',
            'size': 8,  # Get more articles to have better selection
        }

        # Add country filter if we found a valid country code
        if country_code:
            params['country'] = country_code
            print(f'📰 Fetching news for {country} (country code: {country_code})')
        else:
            # Fallback: include country in search to ensure relevance
            params['q'] = f"{country} {search_query}"
            print(f'📰 Fetching news for {country} (no country code, using search)')

        # Set timeout to 5 seconds (increased slightly for reliability)
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    if data.get('status') == 'success' and data.get('results'):
                        articles = []
                        for article in data['results'][:5]:  # Return top 5
                            # Ensure the article is relevant to the destination
                            title = article.get('title', 'No title')
                            description = article.get('description', 'No description available')

                            articles.append({
                                'title': title,
                                'description': description,
                                'url': article.get('link', ''),
                                'source': article.get('source_id', 'Unknown'),
                                'publishedAt': article.get('pubDate', ''),
                                'imageUrl': article.get('image_url', '')
                            })

                        print(f'✓ Fetched {len(articles)} local news articles for {country}')
                        return articles
                    else:
                        print(f'⚠ No news articles found for {country}')
                        return []
                else:
                    print(f'✗ News API error: Status {response.status}')
                    return []

    except aiohttp.ClientTimeout:
        print(f'✗ News API timeout after 5 seconds')
        return []
    except Exception as e:
        print(f'✗ Error fetching news: {str(e)}')
        return []
