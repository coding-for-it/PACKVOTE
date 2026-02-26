import os
import json
import re
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_group_trip_plan(analytics: dict):
    """
    Generates a structured trip plan using Gemini 2.5 Flash.
    Enforces minimum budget as hard constraint.
    Returns validated structured JSON.
    """

    # Extract analytics safely
    total_users = analytics.get("total_users", 0)
    min_budget = analytics.get("min_budget", 0)
    max_budget = analytics.get("max_budget", 0)
    min_duration = analytics.get("min_duration", 0)
    max_duration = analytics.get("max_duration", 0)
    users = analytics.get("users", [])

    prompt = f"""
You are a professional group travel optimization system.

You must behave like a constraint-based planner, not a generic recommender.

HARD CONSTRAINTS:

1. The TOTAL per person trip cost MUST NOT exceed {min_budget}.
   This is non-negotiable.
   Do not exceed this budget under any circumstance.

2. Do NOT use average budget for decision making.

3. Destination must be selected ONLY after:
   - Analyzing ALL individual preferences
   - Counting majority travel_style patterns
   - Checking duration overlaps
   - Checking shopping_interest patterns

4. Do NOT default to popular destinations unless supported by majority logic.

5. Base plan must be affordable for EVERY member.

6. Higher budget members may receive OPTIONAL add-ons,
   but base itinerary must remain within {min_budget}.

---------------------------------------

GROUP DATA

Total Members: {total_users}
Budget Range: {min_budget} to {max_budget}
Duration Range: {min_duration} to {max_duration}

Individual Member Preferences:
{users}

---------------------------------------

OUTPUT REQUIREMENTS

Return ONLY valid JSON.
No markdown.
No explanation outside JSON.
No code blocks.

JSON STRUCTURE:

{{
    "destination": "",
    "reason": "",
    "fairness_explanation": "",
    "itinerary": "",
    "optional_addons": "",
    "budget_breakdown": {{
        "per_person_total": 0,
        "transport": 0,
        "accommodation": 0,
        "food": 0,
        "activities": 0,
        "miscellaneous": 0
    }},
    "activities": "",
    "food_suggestions": "",
    "travel_tips": ""
}}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        raw_text = response.text.strip()

        # Try direct JSON parse
        try:
            plan_json = json.loads(raw_text)
        except json.JSONDecodeError:
            # Fallback: extract JSON object from response
            json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if not json_match:
                return {"error": "Invalid JSON format received from AI"}

            json_text = json_match.group()

            # Fix common trailing comma issues
            json_text = re.sub(r",\s*}", "}", json_text)
            json_text = re.sub(r",\s*]", "]", json_text)

            plan_json = json.loads(json_text)

        # Validate required top-level keys
        required_keys = [
            "destination",
            "reason",
            "fairness_explanation",
            "itinerary",
            "optional_addons",
            "budget_breakdown",
            "activities",
            "food_suggestions",
            "travel_tips"
        ]

        for key in required_keys:
            if key not in plan_json:
                return {"error": f"Missing required field: {key}"}

        # Validate budget constraint strictly
        budget_info = plan_json.get("budget_breakdown", {})
        per_person_total = budget_info.get("per_person_total", 0)

        if per_person_total > min_budget:
            return {
                "error": f"Generated plan exceeds minimum budget constraint ({min_budget})"
            }

        return plan_json

    except Exception as e:
        return {"error": str(e)}
