from fastapi import FastAPI
from typing import List
from backend.models import Preference
from backend.services.preference_service import save_preference
from backend.services.ml_service import analyze_group_preferences
from backend.services.ai_service import generate_itinerary

app = FastAPI()

@app.post("/submit")
def submit_preferences(prefs: List[Preference]):
    for pref in prefs:
        save_preference(pref)
    return {"message": "Preferences saved successfully"}

@app.get("/generate-plan")
def generate_plan():
    analysis = analyze_group_preferences()

    if analysis is None:
        return {"message": "Minimum 3 members required"}

    itinerary = generate_itinerary(analysis)

    return {
        "final_decision": analysis,
        "itinerary": itinerary
    }