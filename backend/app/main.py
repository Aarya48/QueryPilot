import os
from pathlib import Path
import tempfile
import joblib
from typing import List, Annotated
from functools import lru_cache
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import inspect, text
import hashlib

from app.database import engine
from app.gemini_sql_generator import generate_sql_with_gemini
from app.sql_validator import validate_sql
from app.upload_handler import (
    csv_to_table,
    create_session_id,
    create_table_name,
    get_relationships_info
)
from app.upload_handler import get_table_schema

# ==========================================
# PATHS & ML MODEL
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "ml" / "intent_classifier.pkl"

intent_model = joblib.load(MODEL_PATH)

# ==========================================
# CACHING & OPTIMIZATION
# ==========================================

# Cache for generated SQL queries (question_hash -> sql)
_sql_cache = {}
# Cache for schemas (session_id -> schema)
_schema_cache = {}
# Cache TTL in seconds
CACHE_TTL = 3600


# ==========================================
# FASTAPI APP & SCHEMAS
# ==========================================

app = FastAPI(
    title="QueryPilot API",
    description="AI-powered Text-to-SQL and Classification Engine",
    version="1.0.0"
)


# ==========================================
# CACHING UTILITIES
# ==========================================

def _get_cache_key(question: str, session_id: str = None) -> str:
    """Generate a cache key for a question."""
    key_str = f"{question}:{session_id or 'default'}"
    return hashlib.md5(key_str.encode()).hexdigest()


def _get_cached_sql(question: str, session_id: str = None) -> str | None:
    """Retrieve SQL from cache if available."""
    cache_key = _get_cache_key(question, session_id)
    if cache_key in _sql_cache:
        sql, timestamp = _sql_cache[cache_key]
        return sql
    return None


def _set_cached_sql(question: str, sql: str, session_id: str = None) -> None:
    """Store SQL in cache."""
    cache_key = _get_cache_key(question, session_id)
    import time
    _sql_cache[cache_key] = (sql, time.time())


def _get_cached_schema(session_id: str = None) -> dict | None:
    """Retrieve schema from cache if available."""
    key = session_id or 'default'
    if key in _schema_cache:
        schema, timestamp = _schema_cache[key]
        return schema
    return None


def _set_cached_schema(schema: dict, session_id: str = None) -> None:
    """Store schema in cache."""
    import time
    key = session_id or 'default'
    _schema_cache[key] = (schema, time.time())

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
    session_id: str | None = None

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


@app.post("/session-schema")
def get_session_schema(request: QueryRequest):
    """Get the schema for uploaded tables in a session (with clean table names and relationships)."""
    if not request.session_id:
        raise HTTPException(
            status_code=400,
            detail="session_id is required"
        )

    inspector = inspect(engine)
    session_prefix = f"session_{request.session_id}_"
    session_tables = [
        table
        for table in inspector.get_table_names()
        if table.startswith(session_prefix)
    ]

    if not session_tables:
        raise HTTPException(
            status_code=404,
            detail="No uploaded tables found for this session."
        )

    schema = get_table_schema(session_tables)
    relationships = get_relationships_info(session_tables)

    return {
        "session_id": request.session_id,
        "tables": schema,
        "relationships": relationships,
        "table_count": len(session_tables)
    }



@app.post("/generate-sql")
def generate_sql_endpoint(request: QueryRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # ------------------------------------------
    # CHECK CACHE FIRST
    # ------------------------------------------

    cached_sql = _get_cached_sql(question, request.session_id)
    if cached_sql:
        return {
            "question": question,
            "sql": cached_sql,
            "validation": "SQL retrieved from cache",
            "cached": True
        }

    # ------------------------------------------
    # GET SCHEMA (with caching)
    # ------------------------------------------

    schema = _get_cached_schema(request.session_id)
    relationships = None

    if not schema:
        if request.session_id:
            inspector = inspect(engine)
            session_prefix = f"session_{request.session_id}_"
            session_tables = [
                table
                for table in inspector.get_table_names()
                if table.startswith(session_prefix)
            ]

            if not session_tables:
                raise HTTPException(
                    status_code=404,
                    detail="No uploaded tables found for this session."
                )

            schema = get_table_schema(session_tables)
            # Detect relationships between uploaded tables
            relationships = get_relationships_info(session_tables)
        else:
            schema = get_db_schema()

        _set_cached_schema(schema, request.session_id)

    # ------------------------------------------
    # INTENT PREDICTION
    # ------------------------------------------

    intent = intent_model.predict([question])[0]

    # ------------------------------------------
    # GEMINI SQL GENERATION (with relationships)
    # ------------------------------------------

    sql = generate_sql_with_gemini(
        question=question,
        intent=intent,
        schema=schema,
        relationships=relationships
    )

    # ------------------------------------------
    # VALIDATE SQL
    # ------------------------------------------

    is_valid, validation_message = validate_sql(sql, schema)

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=validation_message
        )

    # Cache the result
    _set_cached_sql(question, sql, request.session_id)

    return {
        "question": question,
        "sql": sql,
        "validation": validation_message,
        "cached": False
    }
@app.post("/query")
def execute_query(request: QueryRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # ------------------------------------------
    # CHECK CACHE FIRST
    # ------------------------------------------
    cached_sql = _get_cached_sql(question, request.session_id)
    use_cache = cached_sql is not None

    # ------------------------------------------
    # GET SCHEMA (with caching)
    # ------------------------------------------
    schema = _get_cached_schema(request.session_id)
    relationships = None

    if not schema:
        if request.session_id:
            inspector = inspect(engine)
            session_prefix = f"session_{request.session_id}_"
            session_tables = [
                table
                for table in inspector.get_table_names()
                if table.startswith(session_prefix)
            ]
            if session_tables:
                schema = get_table_schema(session_tables)
                relationships = get_relationships_info(session_tables)
        if not schema:
            schema = get_db_schema()
        _set_cached_schema(schema, request.session_id)

    # ------------------------------------------
    # INTENT PREDICTION
    # ------------------------------------------
    intent = intent_model.predict([question])[0]
    confidence = intent_model.predict_proba([question]).max()

    # ------------------------------------------
    # GET SQL (from cache or generate)
    # ------------------------------------------
    if use_cache:
        sql = cached_sql
    else:
        sql = generate_sql_with_gemini(
            question=question,
            intent=intent,
            schema=schema,
            relationships=relationships
        )
        _set_cached_sql(question, sql, request.session_id)

    # ------------------------------------------
    # VALIDATE SQL
    # ------------------------------------------
    is_valid, validation_message = validate_sql(sql, schema)
    if not is_valid:
        raise HTTPException(status_code=400, detail=validation_message)

    # ------------------------------------------
    # EXECUTE QUERY
    # ------------------------------------------
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
        "data": data,
        "from_cache": use_cache
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