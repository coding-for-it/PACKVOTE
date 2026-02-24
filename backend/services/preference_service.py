from backend.db import get_connection
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def analyze_group_preferences():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM GROUP_PREFERENCES", conn)
    conn.close()

    if df.empty:
        return None

    total_members = len(df)

    # Case 1: Single person
    if total_members == 1:
        row = df.iloc[0]
        return {
            "budget": row["BUDGET"],
            "duration": row["DURATION"],
            "destination": row["DESTINATION"],
            "shopping": [row["SHOPPING_INTEREST"]]
        }

    # Case 2: Two members (simple aggregation)
    if total_members == 2:
        return {
            "budget": round(df["BUDGET"].mean(), 2),
            "duration": int(df["DURATION"].median()),
            "destination": df["DESTINATION"].mode()[0],
            "shopping": df["SHOPPING_INTEREST"].unique().tolist()
        }

    # Case 3: 3+ members → Apply ML
    scaler = StandardScaler()
    features = scaler.fit_transform(df[["BUDGET", "DURATION"]])

    model = KMeans(n_clusters=3, random_state=42, n_init=10)
    df["CLUSTER"] = model.fit_predict(features)

    return {
        "budget": round(df["BUDGET"].mean(), 2),
        "duration": int(df["DURATION"].median()),
        "destination": df["DESTINATION"].mode()[0],
        "shopping": df["SHOPPING_INTEREST"].unique().tolist()
    }

def save_preference(pref):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO GROUP_PREFERENCES 
        (BUDGET, DESTINATION, DURATION, TRAVEL_STYLE, SHOPPING_INTEREST)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            pref.budget,
            pref.destination,
            pref.duration,
            pref.travel_style,
            pref.shopping_interest
        )
    )

    conn.commit()
    cursor.close()
    conn.close()