from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import inspect, text
from app.sql_validator import validate_sql
from app.database import engine
from app.sql_generator import generate_sql
from app.gemini_sql_generator import generate_sql_with_gemini

# ==========================================
# PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "ml" / "intent_classifier.pkl"


# ==========================================
# LOAD ML MODEL
# ==========================================

intent_model = joblib.load(MODEL_PATH)


# ==========================================
# FASTAPI APP
# ==========================================

app = FastAPI(
    title="QueryPilot API",
    description="AI-powered Text-to-SQL and Classification Engine",
    version="1.0.0"
)


# ==========================================
# REQUEST MODEL
# ==========================================

class QueryRequest(BaseModel):
    question: str


# ==========================================
# ROOT
# ==========================================

@app.get("/")
def root():
    return {
        "message": "QueryPilot API is running 🚀"
    }


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# ==========================================
# INTENT PREDICTION
# ==========================================

@app.post("/predict-intent")
def predict_intent(request: QueryRequest):

    question = request.question.strip()

    if not question:
        return {
            "error": "Question cannot be empty."
        }

    intent = intent_model.predict([question])[0]

    confidence = intent_model.predict_proba([question]).max()

    return {
        "question": question,
        "intent": intent,
        "confidence": round(float(confidence), 4)
    }


# ==========================================
# DATABASE SCHEMA
# ==========================================

@app.get("/schema")
def get_schema():

    inspector = inspect(engine)

    tables = inspector.get_table_names()

    schema = {}

    for table in tables:

        columns = inspector.get_columns(table)

        schema[table] = [
            {
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column["nullable"]
            }
            for column in columns
        ]

    return {
        "tables": schema
    }


# ==========================================
# TEXT TO SQL
# ==========================================

# ==========================================
# TEXT TO SQL
# ==========================================

@app.post("/generate-sql")
def generate_sql_endpoint(request: QueryRequest):

    question = request.question.strip()

    if not question:
        return {
            "error": "Question cannot be empty."
        }

    # 1. Predict intent
    intent = intent_model.predict([question])[0]

    confidence = intent_model.predict_proba([question]).max()

    # 2. Get real database schema
    inspector = inspect(engine)

    schema = {}

    for table in inspector.get_table_names():

        columns = inspector.get_columns(table)

        schema[table] = [
            {
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column["nullable"]
            }
            for column in columns
        ]

    # 3. Generate SQL using Gemini
    sql = generate_sql_with_gemini(
        question=question,
        intent=intent,
        schema=schema
    )

    # 4. Validate generated SQL
    is_valid, validation_message = validate_sql(
    sql,
    schema
)

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=validation_message
        )

    # 5. Return result
    return {
        "question": question,
        "intent": intent,
        "confidence": round(float(confidence), 4),
        "sql": sql,
        "validation": validation_message
    }
    # ==========================================
# EXECUTE QUERY
# ==========================================

@app.post("/query")
def execute_query(request: QueryRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # 1. Predict intent
    intent = intent_model.predict([question])[0]

    confidence = intent_model.predict_proba([question]).max()

    # 2. Get real database schema
    inspector = inspect(engine)

    schema = {}

    for table in inspector.get_table_names():

        columns = inspector.get_columns(table)

        schema[table] = [
            {
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column["nullable"]
            }
            for column in columns
        ]

    # 3. Generate SQL using Gemini
    sql = generate_sql_with_gemini(
        question=question,
        intent=intent,
        schema=schema
    )

    # 4. Validate SQL
    is_valid, validation_message = validate_sql(
    sql,
    schema
)

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=validation_message
        )

    # 5. Execute SQL
    try:

        with engine.connect() as connection:

            result = connection.execute(text(sql))

            rows = result.fetchmany(100)

            columns = list(result.keys())

        data = [
            dict(zip(columns, row))
            for row in rows
        ]

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=f"SQL execution failed: {str(e)}"
        )

    # 6. Return result
    return {
        "question": question,
        "intent": intent,
        "confidence": round(float(confidence), 4),
        "sql": sql,
        "validation": validation_message,
        "row_count": len(data),
        "data": data
    }