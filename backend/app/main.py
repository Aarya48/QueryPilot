import os
from pathlib import Path
import tempfile
import joblib
from typing import List, Annotated
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import inspect, text

from app.database import engine
from app.gemini_sql_generator import generate_sql_with_gemini
from app.sql_validator import validate_sql
from app.upload_handler import (
    csv_to_table,
    create_session_id,
    create_table_name
)

# ==========================================
# PATHS & ML MODEL
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "ml" / "intent_classifier.pkl"

intent_model = joblib.load(MODEL_PATH)


# ==========================================
# FASTAPI APP & SCHEMAS
# ==========================================

app = FastAPI(
    title="QueryPilot API",
    description="AI-powered Text-to-SQL and Classification Engine",
    version="1.0.0"
)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    for schema in openapi_schema.get("components", {}).get("schemas", {}).values():
        for prop in schema.get("properties", {}).values():

            if prop.get("contentMediaType") == "application/octet-stream":
                prop.pop("contentMediaType", None)
                prop["format"] = "binary"

            items = prop.get("items", {})

            if items.get("contentMediaType") == "application/octet-stream":
                items.pop("contentMediaType", None)
                items["format"] = "binary"

    app.openapi_schema = openapi_schema

    return app.openapi_schema


app.openapi = custom_openapi
class QueryRequest(BaseModel):
    question: str


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_db_schema() -> dict:
    """Extracts table and column metadata from the database."""
    inspector = inspect(engine)
    schema = {}
    
    for table in inspector.get_table_names():
        columns = inspector.get_columns(table)
        schema[table] = [
            {
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col["nullable"]
            }
            for col in columns
        ]
    return schema


# ==========================================
# ENDPOINTS
# ==========================================

@app.get("/")
def root():
    return {"message": "QueryPilot API is running 🚀"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/predict-intent")
def predict_intent(request: QueryRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    intent = intent_model.predict([question])[0]
    confidence = intent_model.predict_proba([question]).max()

    return {
        "question": question,
        "intent": intent,
        "confidence": round(float(confidence), 4)
    }


@app.get("/schema")
def get_schema():
    return {"tables": get_db_schema()}


@app.post("/generate-sql")
def generate_sql_endpoint(request: QueryRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    intent = intent_model.predict([question])[0]
    confidence = intent_model.predict_proba([question]).max()
    
    schema = get_db_schema()
    sql = generate_sql_with_gemini(question=question, intent=intent, schema=schema)

    is_valid, validation_message = validate_sql(sql, schema)
    if not is_valid:
        raise HTTPException(status_code=400, detail=validation_message)

    return {
        "question": question,
        "intent": intent,
        "confidence": round(float(confidence), 4),
        "sql": sql,
        "validation": validation_message
    }


@app.post("/query")
def execute_query(request: QueryRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    intent = intent_model.predict([question])[0]
    confidence = intent_model.predict_proba([question]).max()

    schema = get_db_schema()
    sql = generate_sql_with_gemini(question=question, intent=intent, schema=schema)

    is_valid, validation_message = validate_sql(sql, schema)
    if not is_valid:
        raise HTTPException(status_code=400, detail=validation_message)

    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql))
            rows = result.fetchmany(100)
            columns = list(result.keys())

        data = [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"SQL execution failed: {str(e)}"
        )

    return {
        "question": question,
        "intent": intent,
        "confidence": round(float(confidence), 4),
        "sql": sql,
        "validation": validation_message,
        "row_count": len(data),
        "data": data
    }


@app.post("/upload-csv")
async def upload_csv(
    files: Annotated[
        List[UploadFile],
        File(description="Upload up to 5 CSV files")
    ]
):
    if len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="At least one CSV file is required."
        )

    if len(files) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 CSV files are allowed."
        )

    session_id = create_session_id()

    uploaded_tables = []

    try:

        for file in files:

            if not file.filename.lower().endswith(".csv"):
                raise HTTPException(
                    status_code=400,
                    detail=f"{file.filename} is not a CSV file."
                )

            temp_path = None

            try:

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".csv"
                ) as temp_file:

                    content = await file.read()
                    temp_file.write(content)
                    temp_path = temp_file.name

                table_name = create_table_name(
                    session_id,
                    file.filename
                )

                rows, columns = csv_to_table(
                    temp_path,
                    table_name
                )

                uploaded_tables.append({
                    "file": file.filename,
                    "table": table_name,
                    "rows": rows,
                    "columns": columns
                })

            finally:

                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)

        return {
            "success": True,
            "session_id": session_id,
            "tables": uploaded_tables
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing files: {str(e)}"
        )