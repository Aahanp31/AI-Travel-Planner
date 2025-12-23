import os
import json
import google.generativeai as genai

genai.configure(api_key=os.getenv('GEMINI_API_KEY', ''))


async def chat_agent(user_message: str, current_trip: dict) -> dict:
    """
    Handle chat-based trip modifications based on user feedback.
    Takes user message and current trip data, returns updated trip components.
    """

    # Extract current trip components
    itinerary = current_trip.get('itinerary', {})
    budget = current_trip.get('budget', {})

    # Build context about the current trip
    trip_context = f"""
CURRENT TRIP DETAILS:
Country: {current_trip.get('country', 'Unknown')}
Days: {current_trip.get('days', 0)}
Locations: {current_trip.get('locations', 'Not specified')}

CURRENT ITINERARY SUMMARY:
{json.dumps(itinerary, indent=2)[:1000]}

CURRENT BUDGET:
{json.dumps(budget, indent=2)[:500]}
"""

    prompt = f"""You are a travel planning assistant helping a user modify their trip.

{trip_context}

USER REQUEST: {user_message}

Analyze the user's request and determine what they want to change. Then respond with:

1. A friendly message acknowledging their request
2. The specific changes you'll make (if applicable)

Return ONLY this JSON (no markdown):
{{
  "response": "Your friendly response message here",
  "changes": {{
    "type": "itinerary|budget|general",
    "description": "Brief description of changes",
    "update_itinerary": false,
    "update_budget": false,
    "suggestions": ["Suggestion 1", "Suggestion 2"]
  }}
}}

Examples:
- If they say "remove day 3": type="itinerary", update_itinerary=true
- If they say "make it cheaper": type="budget", update_budget=true
- If they ask a question: type="general", both false

Be conversational and helpful. If unclear, ask for clarification."""

    generation_config = genai.types.GenerationConfig(
        temperature=0.7,
        max_output_tokens=2048,
    )

    model = genai.GenerativeModel(
        'models/gemini-2.5-flash',
        generation_config=generation_config
    )

    response = model.generate_content(prompt)
    text = response.text.strip()

    # Clean markdown if present
    text = text.replace('```json', '').replace('```', '').strip()

    try:
        chat_response = json.loads(text)
        print(f"✓ Chat response generated for: {user_message[:50]}")
        return chat_response
    except json.JSONDecodeError as e:
        print(f"✗ JSON decode error in chat agent: {e}")
        # Return a fallback response
        return {
            'response': "I understand you'd like to make some changes. Could you provide more specific details about what you'd like to modify?",
            'changes': {
                'type': 'general',
                'description': 'Clarification needed',
                'update_itinerary': False,
                'update_budget': False,
                'suggestions': []
            }
        }
