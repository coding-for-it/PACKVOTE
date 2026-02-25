import snowflake.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_connection():
    return snowflake.connector.connect(
        user=os.getenv("SF_USER"),
        password=os.getenv("SF_PASSWORD"),
        account=os.getenv("SF_ACCOUNT"),
        warehouse="PACKVOTE_WH",
        database="PACKVOTE_DB",
        schema="CORE",
    )


# Insert preference with GROUP_ID
def insert_preference(data, group_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO GROUP_PREFERENCES
        (GROUP_ID, BUDGET, DESTINATION, DURATION, TRAVEL_STYLE, SHOPPING_INTEREST)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            group_id,
            data["budget"],
            data["destination"],
            data["duration"],
            data["travel_style"],
            data["shopping_interest"],
        ),
    )

    conn.commit()
    cursor.close()
    conn.close()


# Fetch preferences by GROUP_ID
def fetch_all_preferences(group_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM GROUP_PREFERENCES WHERE GROUP_ID = %s",
        (group_id,),
    )

    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]

    result = []
    for row in rows:
        result.append(dict(zip(columns, row)))

    cursor.close()
    conn.close()

    return result


# Fetch analytics from Snowflake VIEW
def fetch_group_analytics(group_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT TOTAL_USERS, AVG_BUDGET, MIN_BUDGET, MAX_BUDGET,
               MAX_DURATION, MIN_DURATION
        FROM GROUP_ANALYTICS
        WHERE GROUP_ID = %s
        """,
        (group_id,),
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result

# Call stored procedure instead of deleting directly
def clear_group_data(group_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("CALL CLEAR_GROUP(%s)", (group_id,))
    conn.commit()

    cursor.close()
    conn.close()