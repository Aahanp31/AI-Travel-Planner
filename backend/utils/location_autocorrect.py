import asyncio
import aiohttp


async def validate_cities_in_country(cities: list, country: str) -> tuple:
    """
    Check that every city in the list belongs to the given country.
    Returns (city, actual_country) for the first mismatch, or None if all valid.
    Geocodes each city and compares the returned country name against the target.
    """
    try:
        url = 'https://geocoding-api.open-meteo.com/v1/search'
        timeout = aiohttp.ClientTimeout(total=4)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async def check_city(city: str):
                params = {'name': city, 'count': 5, 'language': 'en', 'format': 'json'}
                try:
                    async with session.get(url, params=params) as resp:
                        data = await resp.json()
                        results = data.get('results', [])
                        if not results:
                            return None  # Can't find city — let it through

                        country_lower = country.lower()
                        for r in results:
                            rc = r.get('country', '').lower()
                            if country_lower in rc or rc in country_lower:
                                return None  # valid — city found in target country

                        # None of the top results are in the target country
                        actual = results[0].get('country', 'another country')
                        return (city, actual)
                except Exception:
                    return None  # Fail open on timeout/error

            results = await asyncio.gather(*[check_city(c) for c in cities])
            for r in results:
                if r is not None:
                    return r
            return None
    except Exception:
        return None


async def autocorrect_location(location: str) -> dict:
    """
    Validate and autocorrect location name using geocoding.
    Returns the corrected location name or original if no match found.

    Args:
        location: The location string to validate/correct

    Returns:
        dict with 'corrected': corrected name, 'original': original name, 'confidence': match quality
    """
    try:
        # Clean up the input
        location_clean = location.strip()

        if not location_clean:
            return {
                'corrected': location,
                'original': location,
                'confidence': 'none'
            }

        # Use Open-Meteo geocoding API (free, no key needed)
        url = 'https://geocoding-api.open-meteo.com/v1/search'
        params = {
            'name': location_clean,
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
                    corrected_name = result.get('name', location)

                    # Add country for cities to make it clearer
                    if 'country' in result and result.get('feature_code') != 'PCLI':
                        # Not a country, add country name
                        corrected_full = f"{corrected_name}, {result['country']}"
                    else:
                        corrected_full = corrected_name

                    # Check if correction was made
                    is_corrected = corrected_name.lower() != location_clean.lower()

                    print(f'📍 Location autocorrect: "{location}" → "{corrected_full}"' +
                          (' (corrected)' if is_corrected else ' (validated)'))

                    return {
                        'corrected': corrected_full,
                        'original': location,
                        'confidence': 'high',
                        'was_corrected': is_corrected,
                        'country': result.get('country', ''),
                        'latitude': result.get('latitude'),
                        'longitude': result.get('longitude')
                    }
                else:
                    # No match found, return original
                    print(f'⚠️  No geocoding match for "{location}", using original')
                    return {
                        'corrected': location,
                        'original': location,
                        'confidence': 'low'
                    }

    except Exception as error:
        print(f'Error autocorrecting location "{location}": {error}')
        # On error, return original
        return {
            'corrected': location,
            'original': location,
            'confidence': 'none',
            'error': str(error)
        }
