import asyncio
from agents.itinerary_agent import itinerary_agent
from agents.budget_agent import budget_agent
from agents.booking_agent import booking_agent
from agents.weather_agent import weather_agent
from agents.news_agent import news_agent
from agents.wiki_agent import add_wikipedia_links
from agents.map_agent import map_agent


async def multi_country_agent(countries: list, origin: str, additional_details: str = None, detail_level: str = 'standard') -> dict:
    """
    Generate a multi-country travel plan
    Args:
        countries: List of dicts with 'country' and 'days' keys
        origin: Departure city
        additional_details: User preferences
        detail_level: Level of detail
    """
    
    # Validate input
    if not countries or len(countries) < 2:
        raise ValueError("At least 2 countries required")
    
    # Prepare results structure
    all_itineraries = {}
    all_budgets = {}
    all_bookings = {}
    all_weather = {}
    all_news = {}
    all_map_data = {}
    
    # Process each country in sequence (to maintain order)
    current_day = 1
    previous_country = None
    
    for segment in countries:
        country = segment['country']
        days = segment['days']
        
        print(f"Processing {country} for {days} days (starting day {current_day})")
        
        # Generate all data for this country in parallel
        itinerary_raw, budget, bookings, weather, news = await asyncio.gather(
            itinerary_agent(country, None, days, origin if not previous_country else previous_country, additional_details, detail_level),
            budget_agent(country, None, days, origin if not previous_country else previous_country, additional_details),
            booking_agent(country, None, days, origin if not previous_country else previous_country),
            weather_agent(country, None, days),
            news_agent(country, None)
        )
        
        # Add Wikipedia links and map data
        itinerary, map_data = await asyncio.gather(
            add_wikipedia_links(itinerary_raw),
            map_agent(country, itinerary_raw, None)
        )
        
        # Add transportation info for days after first country
        if previous_country:
            # Add transportation note to first day of this country
            first_day_key = f"day{current_day}"
            if first_day_key in itinerary:
                # Add transportation from previous country
                transport_note = f"Travel from {previous_country} to {country}"
                if 'morning' in itinerary[first_day_key]:
                    if isinstance(itinerary[first_day_key]['morning'], list):
                        itinerary[first_day_key]['morning'].insert(0, transport_note)
                    else:
                        itinerary[first_day_key]['morning'] = [transport_note]
        
        # Renumber days to be sequential across all countries
        for i in range(days):
            old_key = f"day{i + 1}"
            new_key = f"day{current_day + i}"
            
            if old_key in itinerary:
                day_data = itinerary[old_key].copy()
                day_data['country'] = country  # Add country identifier
                all_itineraries[new_key] = day_data
            
            if old_key in budget:
                all_budgets[new_key] = budget[old_key]
        
        # Store other data with country identifier
        all_bookings[country] = bookings
        all_weather[country] = weather
        all_news[country] = news
        all_map_data[country] = map_data
        
        current_day += days
        previous_country = country
    
    # Combine all data
    result = {
        'itinerary': all_itineraries,
        'budget': all_budgets,
        'bookings': all_bookings,
        'mapData': all_map_data,
        'weather': all_weather,
        'news': all_news,
        'countries': countries  # Include country breakdown for reference
    }
    
    return result
