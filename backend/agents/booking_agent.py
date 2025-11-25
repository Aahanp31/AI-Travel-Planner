async def booking_agent(country: str, locations: str = None, days: int = 3, origin: str = 'LAX') -> dict:
    """
    Return mock booking data.
    In production, replace with real API calls to Amadeus, Hotels.com, etc.
    """
    # For flights, use first location or country
    if locations and locations.strip():
        primary_destination = locations.split(',')[0].strip()
    else:
        primary_destination = country

    return {
        'hotels': [
            {
                'name': 'Booking.com',
                'description': 'Compare prices from major hotel chains and independent properties',
                'link': 'https://www.booking.com/',
                'search_query': 'hotels'
            },
            {
                'name': 'Hotels.com',
                'description': 'Earn rewards and get special member pricing',
                'link': 'https://www.hotels.com/',
                'search_query': 'hotels'
            },
            {
                'name': 'Expedia',
                'description': 'Bundle hotels with flights for additional savings',
                'link': 'https://www.expedia.com/',
                'search_query': 'hotels'
            }
        ],
        'flights': [
            {
                'origin': origin,
                'destination': primary_destination,
                'price': 0,
                'airline': 'Google Flights',
                'link': 'https://www.google.com/travel/flights',
                'search_query': 'flights'
            },
            {
                'origin': origin,
                'destination': primary_destination,
                'price': 0,
                'airline': 'Kayak',
                'link': 'https://www.kayak.com/flights',
                'search_query': 'flights'
            },
            {
                'origin': origin,
                'destination': primary_destination,
                'price': 0,
                'airline': 'Skyscanner',
                'link': 'https://www.skyscanner.com/flights',
                'search_query': 'flights'
            }
        ]
    }
