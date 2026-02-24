from google import genai
from backend.config import GEMINI_API_KEY

# Initialize client
client = genai.Client(api_key=GEMINI_API_KEY)

def generate_itinerary(data):

    prompt = f"""
    Create a detailed {data['duration']}-day travel itinerary for {data['destination']}.
    Budget per person: {data['budget']} INR.
    Include:
    - Stay suggestions
    - Daily sightseeing plan
    - Famous local food
    - Shopping places including {", ".join(data['shopping'])}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text