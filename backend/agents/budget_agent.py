import os
import re
import json
import google.generativeai as genai

genai.configure(api_key=os.getenv('GEMINI_API_KEY', ''))


async def budget_agent(country: str, locations: str = None, days: int = 3, origin: str = 'United States') -> dict:
    """
    Generate a travel budget estimate using Google Gemini AI.
    First calculates costs in destination currency, then converts to origin currency.
    """
    # Determine destination for budgeting
    if locations and locations.strip():
        budget_location = f"{locations} in {country}"
        multi_location_note = f"\n\nMULTI-LOCATION NOTE: Average costs across these locations: {locations}"
    else:
        budget_location = country
        multi_location_note = ""

    prompt = f"""You are a travel budget expert. Create a detailed budget estimate for traveling to {budget_location} for {days} days.
The traveler is coming from {origin}.{multi_location_note}

STEP 1: Determine the local currency used in {budget_location}
STEP 2: Calculate realistic costs in the LOCAL currency of {budget_location} based on current 2024-2025 prices
STEP 3: Determine the currency used in {origin}
STEP 4: Convert all amounts from {budget_location}'s currency to {origin}'s currency using current exchange rates

Return ONLY a valid JSON object with this exact structure:
{{
  "city": "{budget_location}",
  "days": {days},
  "destination_currency_code": "THREE_LETTER_CODE",
  "destination_symbol": "SYMBOL",
  "origin_currency_code": "THREE_LETTER_CODE",
  "origin_symbol": "SYMBOL",
  "exchange_rate": 1.23,
  "hotel_per_night": {{
    "min": 100,
    "max": 200,
    "note": "¥15,000-30,000 → $100-200 USD"
  }},
  "food_per_day": {{
    "min": 40,
    "max": 80,
    "note": "¥6,000-12,000 → $40-80 USD"
  }},
  "transport_total": {{
    "min": 50,
    "max": 100,
    "note": "¥7,500-15,000 → $50-100 USD"
  }},
  "activities_total": {{
    "min": 100,
    "max": 200,
    "note": "¥15,000-30,000 → $100-200 USD"
  }},
  "disclaimer": "Prices are estimates and may vary. Exchange rate: 1 USD = X LOCAL_CURRENCY",
  "currency": "$",
  "total_budget": {{
    "min": 500,
    "max": 1000,
    "note": "¥75,000-150,000 → $500-1000 USD"
  }}
}}

CRITICAL INSTRUCTIONS:
- Research actual current prices for {budget_location}
- Use the correct local currency for {budget_location} (e.g., JPY for Japan, EUR for France, GBP for UK)
- Use the correct currency for {origin}
- Apply accurate current exchange rates (as of 2024-2025)
- The "min" and "max" fields should be NUMBERS in the origin currency
- The "note" field should show the conversion: "LOCAL_AMOUNT → ORIGIN_AMOUNT ORIGIN_CODE"
- Include proper currency symbols (¥, €, £, ₹, etc.) in the note
- The "currency" field should be the origin currency symbol
- Be realistic with pricing based on {budget_location}'s cost of living
- CALCULATE total_budget by summing: (hotel_per_night × {days}) + (food_per_day × {days}) + transport_total + activities_total
- The total_budget should also include both the local currency calculation and origin currency conversion in the note
- Return ONLY the JSON object, no markdown formatting, no code blocks"""

    model = genai.GenerativeModel('models/gemini-2.5-flash')
    response = model.generate_content(prompt)
    text = response.text

    # Remove markdown code blocks if present
    text = re.sub(r'```json\n?', '', text)
    text = re.sub(r'```\n?', '', text)
    text = text.strip()

    try:
        budget_data = json.loads(text)
        print(f"✅ Budget data generated successfully for {budget_location}")
        return budget_data
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        print(f"Raw response: {text}")
        return {
            'raw': text
        }
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return {
            'raw': str(e)
        }
