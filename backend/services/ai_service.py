import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file.")

client = genai.Client(api_key=API_KEY)


def generate_group_trip_plan(users, analytics):
    total_users = analytics[0]
    avg_budget = analytics[1]
    min_budget = analytics[2]
    max_budget = analytics[3]
    max_duration = analytics[4]
    min_duration = analytics[5]

    prompt = f"""
    You are a travel planning assistant.

    Group Details:
    - Total Members: {total_users}
    - Budget Range: {min_budget} to {max_budget}
    - Average Budget: {avg_budget}
    - Duration Range: {min_duration} to {max_duration} days

    Individual Preferences:
    {users}

    Generate a group travel plan that:
    1. Stays within the minimum budget so everyone can afford it.
    2. Suggest optional premium add-ons for higher budget members.
    3. Balance duration preferences.
    4. Explain why the plan is fair for all members.

    Provide clear structured output.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        # Safe extraction
        if hasattr(response, "text") and response.text:
            return response.text

        return response.candidates[0].content.parts[0].text

    except Exception as e:
        return f"AI Generation Error: {str(e)}"