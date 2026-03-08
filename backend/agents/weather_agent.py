import traceback

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


async def weather_agent(country: str, locations: str = None, days: int = 3) -> dict:
    """
    Fetch weather forecast for the destination using Open-Meteo API (completely free, no API key needed).
    Uses a single aiohttp session for both geocoding and forecast requests.
    """
    weather_location = f"{locations.split(',')[0].strip()}, {country}" if locations and locations.strip() else country

    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Step 1: Geocode
            geo_params = {'name': weather_location, 'count': 1, 'language': 'en', 'format': 'json'}
            async with session.get('https://geocoding-api.open-meteo.com/v1/search', params=geo_params) as geo_resp:
                geo_data = await geo_resp.json()

            if not geo_data.get('results'):
                print(f'Could not geocode destination: {weather_location}')
                return None

            result = geo_data['results'][0]
            latitude, longitude, location_name = result['latitude'], result['longitude'], result.get('name', weather_location)

            # Step 2: Fetch forecast
            forecast_days = min(days, 16)
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weathercode,windspeed_10m_max',
                'timezone': 'auto',
                'forecast_days': forecast_days,
                'temperature_unit': 'celsius'
            }
            async with session.get('https://api.open-meteo.com/v1/forecast', params=params) as resp:
                data = await resp.json()

        if 'daily' not in data:
            print(f'No weather data available for {weather_location}')
            return None

        daily = data['daily']
        weather_data = {
            'location': location_name,
            'latitude': latitude,
            'longitude': longitude,
            'timezone': data.get('timezone', 'UTC'),
            'forecast': []
        }

        for i in range(len(daily['time'])):
            weather_code = daily['weathercode'][i]
            condition_text, condition_icon = WEATHER_CODES.get(weather_code, ("Unknown", "❓"))
            weather_data['forecast'].append({
                'date': daily['time'][i],
                'maxtemp_c': round(daily['temperature_2m_max'][i], 1),
                'mintemp_c': round(daily['temperature_2m_min'][i], 1),
                'maxtemp_f': round(daily['temperature_2m_max'][i] * 9/5 + 32, 1),
                'mintemp_f': round(daily['temperature_2m_min'][i] * 9/5 + 32, 1),
                'precipitation_sum': round(daily['precipitation_sum'][i], 1),
                'precipitation_probability': daily['precipitation_probability_max'][i],
                'wind_speed_max': round(daily['windspeed_10m_max'][i], 1),
                'weather_code': weather_code,
                'condition': {'text': condition_text, 'icon': condition_icon}
            })

        print(f'✓ Fetched {forecast_days}-day weather forecast for {location_name}')
        return weather_data

    except Exception as error:
        print(f'Error fetching weather for {weather_location}: {error}')
        traceback.print_exc()
        return None
