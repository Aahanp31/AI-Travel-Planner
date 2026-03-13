import asyncio
import json
import os
import re

from google import genai
from google.genai import types

_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY', ''))


async def budget_agent(country: str, locations: str = None, days: int = 3, origin: str = 'United States', additional_details: str = None) -> dict:
    """
    Generate a travel budget estimate using Google Gemini AI.
    First calculates costs in destination currency, then converts to origin currency.
    Incorporates pre-booked activities and custom plans from additional_details.
    """
    # Determine destination for budgeting
    if locations and locations.strip():
        budget_location = f"{locations} in {country}"
        multi_location_note = f"\n\nMULTI-LOCATION NOTE: Average costs across these locations: {locations}"
    else:
        budget_location = country
        multi_location_note = ""

    # Add custom activities/pre-booked items to budget context
    custom_activities_note = ""
    if additional_details and additional_details.strip():
        custom_activities_note = f"\nCustom plans: {additional_details[:200]}"  # Truncate to keep prompt short

    prompt = f"""Budget for {budget_location}, {days} days from {origin}.{multi_location_note}{custom_activities_note}

Return ONLY this JSON (no markdown):
{{
  "city": "{budget_location}",
  "days": {days},
  "destination_currency_code": "CODE",
  "destination_symbol": "$",
  "origin_currency_code": "CODE",
  "origin_symbol": "$",
  "exchange_rate": 0.0,
  "hotel_per_night": {{"min": 0, "max": 0, "note": ""}},
  "food_per_day": {{"min": 0, "max": 0, "note": ""}},
  "transport_total": {{"min": 0, "max": 0, "note": ""}},
  "activities_total": {{"min": 0, "max": 0, "note": ""}},
  "total_budget": {{"min": 0, "max": 0, "note": ""}},
  "currency": "$",
  "disclaimer": ""
}}

Use 2024-2025 prices. Numbers not strings. Brief notes."""

    try:
        response = await asyncio.wait_for(
            _client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=1024),
            ),
            timeout=60.0
        )
    except asyncio.TimeoutError:
        print("WARNING: Gemini budget request timed out after 60s")
        return {'error': 'Budget generation timed out. Please try again.'}
    text = response.text

    # Remove markdown code blocks if present
    text = re.sub(r'```json\s*\n?', '', text)
    text = re.sub(r'```\s*\n?', '', text)
    text = text.strip()

    # Try to extract JSON if there's extra text before/after
    # Look for the JSON object boundaries
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        text = json_match.group(0)

    try:
        budget_data = json.loads(text)

        # Validate that the response has the expected structure
        required_fields = ['city', 'days', 'hotel_per_night', 'food_per_day',
                          'transport_total', 'activities_total', 'total_budget']

        if all(field in budget_data for field in required_fields):
            print(f"✓ Budget data generated successfully for {budget_location}")
            return budget_data
        else:
            print(f"⚠ Budget data missing required fields")
            print(f"Received fields: {list(budget_data.keys())}")
            return {
                'raw': text,
                'error': 'Budget response missing required fields'
            }

    except json.JSONDecodeError as e:
        print(f"✗ JSON decode error: {e}")
        print(f"Raw response (first 500 chars): {text[:500]}")
        return {
            'raw': text,
            'error': f'Failed to parse budget response: {str(e)}'
        }
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return {
            'raw': str(e),
            'error': f'Unexpected error: {str(e)}'
        }
