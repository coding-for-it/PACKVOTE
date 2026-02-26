# Snowflake-Constrained AI Travel Planning System

## Overview

Planning a group trip is difficult because of:

- Different individual budgets  
- Different duration preferences  
- Different travel styles  
- AI tendency to generate unrealistic luxury plans  

PackVote solves this by combining:

- **Deterministic constraint computation (Snowflake SQL)**
- **Structured AI reasoning (Gemini API)**
- **Hard affordability enforcement using minimum group budget**

AI does not invent constraints.  
It operates strictly within database-calculated boundaries.

---

## Core Planning Rule (Updated Logic)

The most important system rule:

> The total per-person cost MUST NOT exceed the group’s minimum budget.

This ensures:

- Every member can afford the base plan
- No luxury bias
- No average-based distortion
- No unrealistic upgrades

Optional premium add-ons may be suggested separately, but the base itinerary always respects the **minimum budget constraint**.

---

## System Architecture

- **Frontend:** Streamlit  
- **Backend:** FastAPI  
- **Data Layer:** Snowflake  
- **AI Layer:** Gemini API (Gemini 2.5 Flash)  
- **Language:** Python  

---

## Architecture Flow

1. Users submit preferences (Single, Group, or Bulk CSV).
2. FastAPI stores preferences in Snowflake under a `GROUP_ID`.
3. Snowflake computes aggregated constraints via a view.
4. Backend retrieves:
   - Minimum budget (hard constraint)
   - Maximum budget
   - Duration range
   - Total users
5. These constraints + individual preferences are sent to Gemini.
6. Gemini returns **structured JSON only**.
7. Backend returns structured plan to frontend.
8. Group data can be cleared after planning.

---

## Deterministic vs Generative Separation

### Snowflake Handles:

- Minimum budget enforcement
- Duration range calculation
- User counting
- Group-level analytics
- Data isolation

### Gemini Handles:

- Destination reasoning
- Preference balancing
- Itinerary creation
- Activity and food suggestions
- Structured JSON output

This ensures AI cannot override financial constraints.

---

## Snowflake Components

### Table: `CORE.GROUP_PREFERENCES`

Stores individual user preferences.

Columns:

- `GROUP_ID`
- `USER_ID` (Auto Increment)
- `BUDGET`
- `DESTINATION`
- `DURATION`
- `TRAVEL_STYLE`
- `SHOPPING_INTEREST`
- `CREATED_AT`

---

### View: `CORE.GROUP_ANALYTICS`

Aggregates group-level constraints:

- `TOTAL_USERS`
- `AVG_BUDGET` (for insight only, not used in constraint)
- `MIN_BUDGET` (hard affordability constraint)
- `MAX_BUDGET`
- `MIN_DURATION`
- `MAX_DURATION`

**Important:**  
AI uses `MIN_BUDGET` only as the affordability ceiling.

---

### Stored Procedure: `CORE.CLEAR_GROUP`

Deletes preferences for a specific `GROUP_ID`.

Used for:

- Resetting session
- Cleaning test data
- Managing lifecycle

---

## Key Features

- Hard minimum budget enforcement
- AI cannot exceed affordability boundary
- No average-based distortion
- Majority preference reasoning (AI-based)
- Structured JSON output from AI
- Multi-member preference aggregation
- CSV bulk upload
- Template download endpoint
- Group data isolation using `GROUP_ID`
- Clean reset mechanism

---

## API Endpoints

### `GET /`
Health check endpoint.

---

### `POST /submit`
Submit single user preference.

---

### `POST /bulk_upload`
Upload CSV file containing multiple users.

Required CSV columns:

- `budget`
- `destination`
- `duration`
- `travel_style`
- `shopping_interest`

---

### `GET /download-template`
Downloads `template.csv` from backend.

Used by Streamlit "Download Template" button.

---

### `GET /generate-plan`

Generates AI-constrained travel plan.

Returns:

```json
{
  "status": "success",
  "plan": {
      "destination": "",
      "reason": "",
      "itinerary": "",
      "optional_addons": "",
      "budget_breakdown": "",
      "activities": "",
      "food_suggestions": "",
      "travel_tips": ""
  }
}
````

AI is forced to return:

* Valid JSON only
* No markdown
* No extra explanation outside JSON

---

## End-to-End Flow

```
User Input (Streamlit)
        ↓
FastAPI Backend
        ↓
Snowflake GROUP_PREFERENCES
        ↓
Snowflake GROUP_ANALYTICS
        ↓
Computed Constraints
        ↓
Gemini API (within hard limits)
        ↓
Structured JSON Plan
        ↓
Frontend Display
```

---

## Constraint Enforcement Strategy

The prompt sent to Gemini includes:

* Hard rule: Total cost ≤ MIN_BUDGET
* Prohibition of average-based decision making
* No defaulting to generic destinations
* Must analyze all preferences
* Must maximize group satisfaction
* Must return valid JSON only

This prevents:

* Generic destination bias
* Luxury drift
* Over-budget plans
* Non-structured outputs

---

## Setup and Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd <project-directory>
```

---

### 2. Configure Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=CORE
```

---

### 3. Create Snowflake Objects

Create:

* Database
* Schema `CORE`
* `GROUP_PREFERENCES` table
* `GROUP_ANALYTICS` view
* `CLEAR_GROUP` stored procedure
* CSV file format
* Internal stage (for bulk uploads)

---

### 4. Run Backend

```bash
uvicorn main:app --reload
```

Backend runs at:

```
http://127.0.0.1:8000
```

---

### 5. Run Frontend

```bash
streamlit run app.py
```

---

## Why This Architecture Is Strong

Traditional AI-only planners:

* Ignore hard affordability
* Use averages incorrectly
* Produce unrealistic itineraries
* Lack structured output control

PackVote:

* Uses Snowflake for constraint enforcement
* Uses AI only within computed limits
* Ensures affordability for all members
* Returns predictable structured output
* Separates deterministic logic from generative reasoning



