import streamlit as st
import requests

st.title("PackVote - AI Powered Group Trip Planner")

st.header("Enter Your Travel Preference")

budget = st.number_input("Budget (INR)", min_value=1000, key="budget")
destination = st.text_input("Preferred Destination", key="destination")
duration = st.number_input("Trip Duration (days)", min_value=1, key="duration")
travel_style = st.selectbox(
    "Travel Style",
    ["Relaxation", "Adventure", "Cultural", "Luxury"],
    key="travel_style"
)
shopping = st.text_input("Shopping Interest", key="shopping")

# -------------------- SUBMIT --------------------

if st.button("Submit Preference", key="submit_btn"):
    response = requests.post(
        "http://127.0.0.1:8000/submit",
        json={
            "budget": budget,
            "destination": destination,
            "duration": duration,
            "travel_style": travel_style,
            "shopping_interest": shopping
        }
    )

    if response.status_code == 200:
        st.success("Preference Submitted Successfully!")
    else:
        st.error(f"Backend Error: {response.status_code}")

# -------------------- GENERATE PLAN --------------------

if st.button("Generate Trip Plan", key="generate_btn"):
    response = requests.get("http://127.0.0.1:8000/generate-plan")

    if response.status_code == 200:
        result = response.json()

        if "message" in result:
            st.warning(result["message"])
        else:
            st.success("Trip Recommendation Generated!")
            st.write(result["group_recommendation"])

    else:
        st.error(f"Backend Error: {response.status_code}")