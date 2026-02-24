import streamlit as st
import requests

st.title("PackVote - AI Powered Trip Planner")

st.header("Enter Your Travel Preference")

budget = st.number_input("Budget (INR)", min_value=1000)
destination = st.text_input("Preferred Destination")
duration = st.number_input("Trip Duration (days)", min_value=1)
travel_style = st.selectbox("Travel Style", ["Relaxation", "Adventure", "Cultural", "Luxury"])
shopping = st.text_input("Shopping Interest")

if st.button("Submit Preference"):
    response = requests.post(
        "http://127.0.0.1:8000/submit",
        json=[{
            "budget": budget,
            "destination": destination,
            "duration": duration,
            "travel_style": travel_style,
            "shopping_interest": shopping
        }]
    )
    st.success("Preference Submitted!")

if st.button("Generate Trip Plan"):
    response = requests.get("http://127.0.0.1:8000/generate-plan")
    result = response.json()

    if "itinerary" in result:
        st.subheader("Final Decision")
        st.json(result["final_decision"])
        st.subheader("Generated Itinerary")
        st.write(result["itinerary"])
    else:
        st.warning(result["message"])