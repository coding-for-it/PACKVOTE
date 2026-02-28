from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import pandas as pd
from io import BytesIO
from starlette.concurrency import run_in_threadpool

from backend.db import (
    get_group_analytics,
    insert_preference,
    upload_preferences_via_stage,
    clear_group
)

from backend.services.ai_service import generate_group_trip_plan

app = FastAPI()


class Preference(BaseModel):
    budget: float
    destination: str
    duration: int
    travel_style: str
    shopping_interest: str


@app.get("/")
def home():
    return {"message": "PackVote Backend Running"}


# ---------------- SUBMIT PREFERENCE ----------------
@app.post("/submit/{group_id}")
def submit_preference(group_id: str, pref: Preference):

    insert_preference(pref.dict(), group_id)

    return {"status": "success"}


# ---------------- DOWNLOAD CSV TEMPLATE ----------------
@app.get("/download-template")
def download_template():

    file_path = Path(__file__).resolve().parent / "template.csv"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Template file not found")

    return FileResponse(
        path=file_path,
        media_type="text/csv",
        filename="template.csv"
    )


# ---------------- BULK UPLOAD ----------------
@app.post("/bulk_upload/{group_id}")
async def bulk_upload(group_id: str, file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")

    contents = await file.read()

    try:

        df = pd.read_csv(BytesIO(contents))
        df.columns = df.columns.str.strip().str.lower()

        required_columns = [
            "budget",
            "destination",
            "duration",
            "travel_style",
            "shopping_interest"
        ]

        missing_cols = [col for col in required_columns if col not in df.columns]

        if missing_cols:
            raise HTTPException(
                status_code=400,
                detail=f"Missing columns: {missing_cols}. Found: {df.columns.tolist()}"
            )

        clear_group(group_id)

        upload_preferences_via_stage(
            df[required_columns].to_dict(orient="records"),
            group_id
        )

        return {"message": "Bulk preferences uploaded successfully."}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- GENERATE PLAN ----------------
@app.post("/start-plan/{group_id}")
async def start_plan(group_id: str):

    analytics = get_group_analytics(group_id)

    if not analytics:
        return {
            "status": "error",
            "message": "No analytics data found. Upload preferences first."
        }

    result = await run_in_threadpool(
        generate_group_trip_plan,
        analytics
    )

    if "error" in result:
        return {"status": "error", "message": result["error"]}

    return {"status": "success", "plan": result}
