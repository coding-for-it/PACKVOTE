import os
import pandas as pd
import tempfile
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE"),
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
        # Ensure correct database & schema
        cursor.execute("USE DATABASE " + os.getenv("SNOWFLAKE_DATABASE"))
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

        # Create temp CSV
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            df.to_csv(tmp.name, index=False)
            file_path = tmp.name

        print("Uploading file:", file_path)

        # PUT file to internal stage
        cursor.execute(
            f"PUT file://{file_path} @PACKVOTE_STAGE OVERWRITE=TRUE"
        )

        print("File uploaded to stage")

        # COPY INTO table
        cursor.execute(
            """
            COPY INTO GROUP_PREFERENCES
            (GROUP_ID, BUDGET, DESTINATION, DURATION, TRAVEL_STYLE, SHOPPING_INTEREST)
            FROM @PACKVOTE_STAGE
            ON_ERROR = 'ABORT_STATEMENT'
            """
        )

        print("Data copied into table")

        # Clean stage
        cursor.execute("REMOVE @PACKVOTE_STAGE")

        conn.commit()
        os.remove(file_path)

        print("Upload completed successfully")

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e

    finally:
        cursor.close()
        conn.close()
