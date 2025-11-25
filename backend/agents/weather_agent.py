import aiohttp


# Weather code to condition mapping for Open-Meteo
WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Foggy", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌧️"),
    61: ("Slight rain", "🌧️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    71: ("Slight snow", "🌨️"),
    73: ("Moderate snow", "❄️"),
    75: ("Heavy snow", "❄️"),
    77: ("Snow grains", "🌨️"),
    80: ("Slight rain showers", "🌦️"),
    81: ("Moderate rain showers", "🌧️"),
    82: ("Violent rain showers", "⛈️"),
    85: ("Slight snow showers", "🌨️"),
    86: ("Heavy snow showers", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with slight hail", "⛈️"),
    99: ("Thunderstorm with heavy hail", "⛈️"),
}


async def geocode_location(location: str) -> tuple:
    """
    Geocode a location to get latitude and longitude using Open-Meteo's geocoding API.
    """
    try:
        url = 'https://geocoding-api.open-meteo.com/v1/search'
        params = {
            'name': location,
            'count': 1,
            'language': 'en',
            'format': 'json'
        }

        timeout = aiohttp.ClientTimeout(total=3)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                data = await response.json()

                if data.get('results') and len(data['results']) > 0:
                    result = data['results'][0]
                    return (result['latitude'], result['longitude'], result.get('name', location))

                return None

    except Exception as error:
        print(f'Error geocoding location {location}: {error}')
        return None


async def weather_agent(country: str, locations: str = None, days: int = 3) -> dict:
    """
    Fetch weather forecast for the destination using Open-Meteo API (completely free, no API key needed).
    """
    try:
        # Determine which location to get weather for
        if locations and locations.strip():
            # Use first specified location
            weather_location = f"{locations.split(',')[0].strip()}, {country}"
        else:
            # Use country (API will determine capital/major city)
            weather_location = country

        # First, geocode the destination to get coordinates
        geocode_result = await geocode_location(weather_location)

        if not geocode_result:
            print(f'Could not geocode destination: {weather_location}')
            return None

        latitude, longitude, location_name = geocode_result

        # Limit forecast to max 16 days (Open-Meteo limit)
        forecast_days = min(days, 16)

        # Fetch weather data from Open-Meteo
        url = 'https://api.open-meteo.com/v1/forecast'
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weathercode,windspeed_10m_max',
            'timezone': 'auto',
            'forecast_days': forecast_days,
            'temperature_unit': 'celsius'
        }

        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                data = await response.json()

                if 'daily' not in data:
                    print(f'No weather data available for {destination}')
                    return None

                daily = data['daily']

                # Build weather forecast
                weather_data = {
                    'location': location_name,
                    'latitude': latitude,
                    'longitude': longitude,
                    'timezone': data.get('timezone', 'UTC'),
                    'forecast': []
                }

                # Process each day
                for i in range(len(daily['time'])):
                    weather_code = daily['weathercode'][i]
                    condition_text, condition_icon = WEATHER_CODES.get(weather_code, ("Unknown", "❓"))

                    day_forecast = {
                        'date': daily['time'][i],
                        'maxtemp_c': round(daily['temperature_2m_max'][i], 1),
                        'mintemp_c': round(daily['temperature_2m_min'][i], 1),
                        'maxtemp_f': round(daily['temperature_2m_max'][i] * 9/5 + 32, 1),
                        'mintemp_f': round(daily['temperature_2m_min'][i] * 9/5 + 32, 1),
                        'precipitation_sum': round(daily['precipitation_sum'][i], 1),
                        'precipitation_probability': daily['precipitation_probability_max'][i],
                        'wind_speed_max': round(daily['windspeed_10m_max'][i], 1),
                        'weather_code': weather_code,
                        'condition': {
                            'text': condition_text,
                            'icon': condition_icon
                        }
                    }

                    weather_data['forecast'].append(day_forecast)

                print(f'✓ Fetched {forecast_days}-day weather forecast for {location_name}')
                return weather_data

    except Exception as error:
        print(f'Error fetching weather for {weather_location}: {error}')
        import traceback
        traceback.print_exc()
        return None
