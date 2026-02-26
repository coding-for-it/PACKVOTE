import streamlit as st
import requests

st.set_page_config(
    page_title="PackVote",
    layout="wide"
)

BACKEND_URL = "http://127.0.0.1:8000"

if "page" not in st.session_state:
    st.session_state.page = "home"


def go_home():
    st.session_state.page = "home"


def go_single():
    st.session_state.page = "single"


def go_group():
    st.session_state.page = "group"


def go_bulk():
    st.session_state.page = "bulk"


# Updated display function to match backend
def display_plan(plan_response):
    if plan_response.status_code != 200:
        st.error("Failed to generate plan.")
        return

    response_data = plan_response.json()

    if response_data.get("status") != "success":
        st.error(response_data.get("message", "Unknown error"))
        return

    plan = response_data.get("plan")

    if not plan:
        st.error("Invalid plan format received.")
        return

    st.markdown("## 🌍 Group Trip Plan")
    st.markdown("---")

    st.subheader("📍 Destination")
    st.write(plan.get("destination", "Not available"))

    st.subheader("🗓 Itinerary")
    st.write(plan.get("itinerary", "Not available"))

    st.subheader("💰 Budget Breakdown")
    st.write(plan.get("budget_breakdown", "Not available"))

    st.subheader("🎯 Activities")
    st.write(plan.get("activities", "Not available"))

    st.subheader("🍽 Food Suggestions")
    st.write(plan.get("food_suggestions", "Not available"))

    st.subheader("✈ Travel Tips")
    st.write(plan.get("travel_tips", "Not available"))


# ---------------- HOME PAGE ----------------
if st.session_state.page == "home":

    st.markdown("<h1 style='text-align: center;'>PackVote</h1>", unsafe_allow_html=True)
    st.markdown(
        "<h3 style='text-align: center;'>Plan trips together. No arguments. Just smart decisions.</h3>",
        unsafe_allow_html=True
    )

    st.write("")
    st.write("")
    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.button("👤 Single User", use_container_width=True, on_click=go_single)

    with col2:
        st.button("👥 2–5 Members", use_container_width=True, on_click=go_group)

    with col3:
        st.button("📂 Bulk Upload (10+ Members)", use_container_width=True, on_click=go_bulk)


# ---------------- SINGLE USER ----------------
elif st.session_state.page == "single":

    st.button("⬅ Back", on_click=go_home)

    st.header("👤 Single User Trip Preference")

    budget = st.number_input("Budget", min_value=0.0)
    destination = st.text_input("Destination")
    duration = st.number_input("Duration (days)", min_value=1)
    travel_style = st.selectbox("Travel Style", ["Relaxed", "Adventure", "Luxury"])
    shopping_interest = st.selectbox("Shopping Interest", ["Low", "Medium", "High"])

    if st.button("Submit Preference"):

        payload = {
            "budget": budget,
            "destination": destination,
            "duration": duration,
            "travel_style": travel_style,
            "shopping_interest": shopping_interest,
        }

        response = requests.post(f"{BACKEND_URL}/submit", json=payload)

        if response.status_code == 200:
            st.success("Preference submitted successfully!")

            with st.spinner("Generating plan..."):
                plan = requests.get(f"{BACKEND_URL}/generate-plan")

            display_plan(plan)

        else:
            st.error("Something went wrong while submitting preference.")


# ---------------- GROUP (2–5) ----------------
elif st.session_state.page == "group":

    st.button("⬅ Back", on_click=go_home)

    st.header("👥 2–5 Members Trip Preferences")

    budget = st.number_input("Budget", min_value=0.0)
    destination = st.text_input("Destination")
    duration = st.number_input("Duration (days)", min_value=1)
    travel_style = st.selectbox("Travel Style", ["Relaxed", "Adventure", "Luxury"])
    shopping_interest = st.selectbox("Shopping Interest", ["Low", "Medium", "High"])

    if st.button("Add Member Preference"):

        payload = {
            "budget": budget,
            "destination": destination,
            "duration": duration,
            "travel_style": travel_style,
            "shopping_interest": shopping_interest,
        }

        response = requests.post(f"{BACKEND_URL}/submit", json=payload)

        if response.status_code == 200:
            st.success("Member preference added!")
        else:
            st.error("Failed to add member preference.")

    if st.button("Generate Group Plan"):

        with st.spinner("Generating AI group plan..."):
            plan = requests.get(f"{BACKEND_URL}/generate-plan")

        display_plan(plan)


# ---------------- BULK UPLOAD ----------------
elif st.session_state.page == "bulk":

    st.button("⬅ Back", on_click=go_home)

    st.header("📂 Bulk Upload (10+ Members)")

    # Download template from backend
    template_response = requests.get(f"{BACKEND_URL}/download-template")

    if template_response.status_code == 200:
        st.download_button(
            label="Download CSV Template",
            data=template_response.content,
            file_name="template.csv",
            mime="text/csv"
        )
    else:
        st.error("Unable to fetch template file.")

    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

    if uploaded_file is not None:

        response = requests.post(
            f"{BACKEND_URL}/bulk_upload",
            files={"file": uploaded_file}
        )

        if response.status_code == 200:
            st.success("Bulk upload successful!")

            with st.spinner("Generating AI group plan..."):
                plan = requests.get(f"{BACKEND_URL}/generate-plan")

            display_plan(plan)

        else:
            st.error("Bulk upload failed.")
