import asyncio

from agents.booking_agent import booking_agent
from agents.budget_agent import budget_agent
from agents.itinerary_agent import itinerary_agent
from agents.map_agent import map_agent
from agents.news_agent import news_agent
from agents.weather_agent import weather_agent
from agents.wiki_agent import add_wikipedia_links


async def multi_country_agent(countries: list, origin: str, additional_details: str = None, detail_level: str = 'standard') -> dict:
    """
    Generate a multi-country travel plan.
    All countries are processed in parallel for maximum speed.
    """
    if not countries or len(countries) < 2:
        raise ValueError("At least 2 countries required")

    async def process_country(segment: dict, travel_origin: str) -> dict:
        """Process a single country: all agents run in parallel."""
        country = segment['country']
        days = segment['days']

        print(f"Processing {country} for {days} days (origin: {travel_origin})")

        # Phase 1: All data agents in parallel (Gemini calls now use asyncio.to_thread)
        itinerary_raw, budget, bookings, weather, news = await asyncio.gather(
            itinerary_agent(country, None, days, travel_origin, additional_details, detail_level),
            budget_agent(country, None, days, travel_origin, additional_details),
            booking_agent(country, None, days, travel_origin),
            weather_agent(country, None, days),
            news_agent(country, None),
            return_exceptions=True
        )

        # Phase 2: Wikipedia links + map data in parallel
        itinerary_raw = itinerary_raw if not isinstance(itinerary_raw, Exception) else {}
        itinerary, map_data = await asyncio.gather(
            add_wikipedia_links(itinerary_raw),
            map_agent(country, itinerary_raw, None),
            return_exceptions=True
        )

        return {
            'country': country,
            'days': days,
            'itinerary': itinerary if not isinstance(itinerary, Exception) else itinerary_raw,
            'budget': budget if not isinstance(budget, Exception) else {},
            'bookings': bookings if not isinstance(bookings, Exception) else {},
            'weather': weather if not isinstance(weather, Exception) else None,
            'news': news if not isinstance(news, Exception) else [],
            'map_data': map_data if not isinstance(map_data, Exception) else [],
        }

    # Build origins: first country uses user origin, subsequent use previous country
    origins = [origin] + [seg['country'] for seg in countries[:-1]]

    # Process ALL countries in parallel
    results = await asyncio.gather(
        *[process_country(seg, orig) for seg, orig in zip(countries, origins)],
        return_exceptions=True
    )

    # Post-process: renumber days sequentially and add inter-country transport notes
    all_itineraries = {}
    all_budgets = {}
    all_bookings = {}
    all_weather = {}
    all_news = {}
    all_map_data = {}

    current_day = 1
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Error processing country {countries[i]['country']}: {result}")
            current_day += countries[i]['days']
            continue

        country = result['country']
        days = result['days']
        itinerary = result['itinerary'] or {}
        budget = result['budget'] or {}

        # Add transportation note to first day (for countries after the first)
        if i > 0 and isinstance(itinerary, dict):
            prev_country = results[i - 1]['country'] if not isinstance(results[i - 1], Exception) else countries[i - 1]['country']
            first_day = itinerary.get('day1', {})
            if first_day and isinstance(first_day.get('morning'), list):
                first_day['morning'].insert(0, f"Travel from {prev_country} to {country}")
            elif first_day:
                first_day['morning'] = [f"Travel from {prev_country} to {country}"]

        # Renumber days to be sequential across all countries
        for j in range(days):
            old_key = f"day{j + 1}"
            new_key = f"day{current_day + j}"

            if isinstance(itinerary, dict) and old_key in itinerary:
                day_data = itinerary[old_key].copy()
                day_data['country'] = country
                all_itineraries[new_key] = day_data

            if isinstance(budget, dict) and old_key in budget:
                all_budgets[new_key] = budget[old_key]

        all_bookings[country] = result['bookings']
        all_weather[country] = result['weather']
        all_news[country] = result['news']
        all_map_data[country] = result['map_data']

        current_day += days

    return {
        'itinerary': all_itineraries,
        'budget': all_budgets,
        'bookings': all_bookings,
        'mapData': all_map_data,
        'weather': all_weather,
        'news': all_news,
        'countries': countries,
    }
