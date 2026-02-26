# Snowflake-Guided Constraint Planning System

## Overview

Planning a group trip is complex due to:

* Different budget ranges
* Different trip duration preferences
* Different travel styles
* Risk of AI generating unrealistic or unaffordable plans

This project solves that by separating:

* Deterministic constraint computation (Snowflake SQL)
* Structured reasoning and plan generation (Gemini API)

AI does not determine constraints — it operates within them.

---

## System Architecture

Frontend: Streamlit
Backend: FastAPI
Data Layer: Snowflake
AI Layer: Gemini API
Language: Python

### Architecture Flow

1. Users submit travel preferences via Streamlit.
2. FastAPI backend stores preferences in Snowflake.
3. Snowflake computes shared group constraints.
4. Backend retrieves aggregated constraint results.
5. Constraints are passed to Gemini API.
6. AI generates a travel plan aligned with database-calculated limits.
7. Group records can be cleared after plan generation.

---

## Core Design Principle

SQL handles deterministic constraint computation.
AI handles structured reasoning.
Database constraints guide generative output.

This separation ensures:

* Predictable cost boundaries
* Duration harmonization
* Controlled AI output
* Group-level data isolation

---

## Snowflake Components

### Table

**CORE.GROUP_PREFERENCES**

Stores individual user preferences grouped by `GROUP_ID`.

Includes:

* Budget range (minimum and maximum)
* Preferred duration
* Travel style
* Destination preferences (optional)

---

### View

**CORE.GROUP_ANALYTICS**

Computes aggregated group-level constraints:

* Minimum budget boundary
* Maximum budget boundary
* Duration range overlap
* Total participants

This view ensures AI receives validated and computed limits.

---

### Stored Procedure

**CORE.CLEAR_GROUP**

Removes group-specific records after plan generation.

Used for:

* Data lifecycle management
* Session-based planning
* Clean state reset

---

## Key Features

* Multi-user preference aggregation
* Budget boundary enforcement
* Duration range harmonization
* Warehouse-driven constraint logic
* Controlled AI-based plan generation
* Group data isolation via `GROUP_ID`
* Post-plan cleanup using stored procedure

---

## End-to-End Flow

```text
User Input (Streamlit)
        ↓
FastAPI Backend
        ↓
Snowflake Table (GROUP_PREFERENCES)
        ↓
Snowflake View (GROUP_ANALYTICS)
        ↓
Aggregated Constraints
        ↓
Gemini API (Plan Generation)
        ↓
Structured Travel Plan Output
        ↓
Optional: CLEAR_GROUP Procedure
```

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

In Snowflake:

* Create database and schema
* Create `GROUP_PREFERENCES` table
* Create `GROUP_ANALYTICS` view
* Create `CLEAR_GROUP` stored procedure

Ensure warehouse permissions are properly configured.

---

### 4. Run Backend Server

```bash
uvicorn main:app --reload
```

Backend runs at:

```
http://127.0.0.1:8000
```

---

### 5. Launch Streamlit Frontend

```bash
streamlit run app.py
```

---

## How to Use

1. Open the Streamlit interface.
2. Enter group travel preferences.
3. Submit preferences for multiple users under the same `GROUP_ID`.
4. Click "Generate Plan".
5. System computes shared constraints in Snowflake.
6. Gemini generates a plan aligned with computed boundaries.
7. Optionally clear group data using the stored procedure.

---

## Data Isolation Strategy

* Each group is identified using `GROUP_ID`.
* All computations are filtered by `GROUP_ID`.
* No cross-group data leakage.
* Clean lifecycle through stored procedure reset.

---

## Why This Architecture Works

Traditional AI-only travel planners:

* Ignore hard affordability constraints
* Generate unrealistic itineraries
* Lack deterministic control

This system:

* Uses Snowflake for constraint enforcement
* Uses AI only within computed bounds
* Produces realistic, group-aligned travel plans

---

## Future Enhancements

* Destination availability validation
* Flight and hotel price integration
* Real-time budget validation APIs
* User authentication
* Multi-destination optimization
* Cost breakdown visualization

---

