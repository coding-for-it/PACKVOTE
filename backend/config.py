import os
from dotenv import load_dotenv

load_dotenv()

SNOWFLAKE_CONFIG = {
    "user": os.getenv("SF_USER"),
    "password": os.getenv("SF_PASSWORD"),
    "account": os.getenv("SF_ACCOUNT"),
    "warehouse": "PACKVOTE_WH",
    "database": "PACKVOTE_DB",
    "schema": "CORE"
}

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
