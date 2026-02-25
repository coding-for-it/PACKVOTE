from fastapi import FastAPI
from pydantic import BaseModel
from backend.db import (
    insert_preference,
    fetch_all_preferences,
    fetch_group_analytics,
    clear_group_data,
)
from backend.services.ai_service import generate_group_trip_plan

app = FastAPI()

# For now we keep static group (simple implementation )
GROUP_ID = "G1"


class Preference(BaseModel):
    budget: float
    destination: str
    duration: int
    travel_style: str
    shopping_interest: str


@app.post("/submit")
def submit_preference(pref: Preference):
    insert_preference(pref.dict(), GROUP_ID)
    return {"message": "Preference submitted successfully."}


@app.get("/generate-plan")
def generate_plan():
    try:
        # Fetch raw preferences
        users = fetch_all_preferences(GROUP_ID)

        if not users:
            return {"message": "No preferences submitted yet."}

        # Fetch aggregated analytics from Snowflake VIEW
        analytics = fetch_group_analytics(GROUP_ID)

        # Send both to AI
        ai_response = generate_group_trip_plan(users, analytics)

        # Clear group using Stored Procedure
        clear_group_data(GROUP_ID)

        return {
            "group_recommendation": ai_response
        }

    except Exception as e:
        return {"message": f"Server Error: {str(e)}"}