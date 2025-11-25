import os
import aiohttp


async def news_agent(country: str, locations: str = None) -> list:
    """
    Fetch latest news articles for a destination using NewsData.io API.
    """
    api_key = os.getenv('NEWS_API_KEY', '')

    if not api_key:
        print('⚠️ NEWS_API_KEY not found in environment variables')
        return []

    # Search for news about locations or country
    if locations and locations.strip():
        # Use all locations for comprehensive news
        search_query = f"{locations.replace(',', ' OR ')} {country}"
    else:
        search_query = country

    try:
        # NewsData.io API endpoint
        url = 'https://newsdata.io/api/1/news'
        params = {
            'apikey': api_key,
            'q': search_query,
            'language': 'en',
            'size': 5  # Get top 5 news articles
        }

        # Set timeout to 3 seconds for faster response
        timeout = aiohttp.ClientTimeout(total=3)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    if data.get('status') == 'success' and data.get('results'):
                        articles = []
                        for article in data['results'][:5]:
                            articles.append({
                                'title': article.get('title', 'No title'),
                                'description': article.get('description', 'No description available'),
                                'url': article.get('link', ''),
                                'source': article.get('source_id', 'Unknown'),
                                'publishedAt': article.get('pubDate', ''),
                                'imageUrl': article.get('image_url', '')
                            })

                        print(f'✓ Fetched {len(articles)} news articles for {search_query}')
                        return articles
                    else:
                        print(f'⚠️ No news articles found for {search_query}')
                        return []
                else:
                    print(f'❌ News API error: Status {response.status}')
                    return []

    except Exception as e:
        print(f'Error fetching news: {str(e)}')
        return []
