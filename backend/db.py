import os
import pandas as pd
import tempfile
import snowflake.connector

from backend.config import SNOWFLAKE_CONFIG


def get_connection():
    return snowflake.connector.connect(
        user=SNOWFLAKE_CONFIG["user"],
        password=SNOWFLAKE_CONFIG["password"],
        account=SNOWFLAKE_CONFIG["account"],
        warehouse=SNOWFLAKE_CONFIG["warehouse"],
        database=SNOWFLAKE_CONFIG["database"],
        schema=SNOWFLAKE_CONFIG["schema"],
        client_session_keep_alive=True
    )


def clear_group(group_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM CORE.GROUP_PREFERENCES WHERE GROUP_ID = %s",
            (group_id,)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def insert_preference(data: dict, group_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            INSERT INTO CORE.GROUP_PREFERENCES
            (GROUP_ID, BUDGET, DESTINATION, DURATION, TRAVEL_STYLE, SHOPPING_INTEREST)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            group_id,
            data.get("budget"),
            data.get("destination"),
            data.get("duration"),
            data.get("travel_style"),
            data.get("shopping_interest")
        )

        cursor.execute(query, values)
        conn.commit()

    finally:
        cursor.close()
        conn.close()


def get_group_analytics(group_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT
                GROUP_ID,
                COUNT(*) AS TOTAL_USERS,
                AVG(BUDGET) AS AVG_BUDGET,
                MIN(BUDGET) AS MIN_BUDGET,
                MAX(BUDGET) AS MAX_BUDGET,
                MAX(DURATION) AS MAX_DURATION,
                MIN(DURATION) AS MIN_DURATION
            FROM CORE.GROUP_PREFERENCES
            WHERE GROUP_ID = %s
            GROUP BY GROUP_ID
        """

        cursor.execute(query, (group_id,))
        result = cursor.fetchone()

        if not result:
            return None

        columns = [col[0].lower() for col in cursor.description]
        return dict(zip(columns, result))

    finally:
        cursor.close()
        conn.close()


def upload_preferences_via_stage(data_list, group_id):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("USE DATABASE " + SNOWFLAKE_CONFIG["database"])
        cursor.execute("USE SCHEMA CORE")

        df = pd.DataFrame(data_list)
        df["GROUP_ID"] = group_id

        df = df[
            [
                "GROUP_ID",
                "budget",
                "destination",
                "duration",
                "travel_style",
                "shopping_interest",
            ]
        ]

        df.columns = [
            "GROUP_ID",
            "BUDGET",
            "DESTINATION",
            "DURATION",
            "TRAVEL_STYLE",
            "SHOPPING_INTEREST",
        ]

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            df.to_csv(tmp.name, index=False)
            file_path = tmp.name

        cursor.execute(
            f"PUT file://{file_path} @PACKVOTE_STAGE OVERWRITE=TRUE"
        )

        cursor.execute(
            """
            COPY INTO GROUP_PREFERENCES
            (GROUP_ID, BUDGET, DESTINATION, DURATION, TRAVEL_STYLE, SHOPPING_INTEREST)
            FROM @PACKVOTE_STAGE
            ON_ERROR = 'ABORT_STATEMENT'
            """
        )

        cursor.execute("REMOVE @PACKVOTE_STAGE")

        conn.commit()
        os.remove(file_path)

    finally:
        cursor.close()
        conn.close()
