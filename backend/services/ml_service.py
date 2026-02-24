from backend.db import get_connection
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def analyze_group_preferences():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM GROUP_PREFERENCES", conn)
    conn.close()

    if len(df) < 3:
        return None

    # ML clustering on Budget + Duration
    scaler = StandardScaler()
    features = scaler.fit_transform(df[["BUDGET", "DURATION"]])

    model = KMeans(n_clusters=3, random_state=42, n_init=10)
    df["CLUSTER"] = model.fit_predict(features)

    # Aggregation for balanced decision
    final_budget = df["BUDGET"].mean()
    final_duration = int(df["DURATION"].median())
    final_destination = df["DESTINATION"].mode()[0]

    shopping_list = df["SHOPPING_INTEREST"].unique().tolist()

    return {
        "budget": round(final_budget, 2),
        "duration": final_duration,
        "destination": final_destination,
        "shopping": shopping_list
    }