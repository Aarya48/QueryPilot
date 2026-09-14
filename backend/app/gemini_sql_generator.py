import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in .env")

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_sql_with_gemini(
    question: str,
    intent: str,
    schema: dict
) -> str:

    schema_text = ""

    for table, columns in schema.items():

        schema_text += f"\nTABLE: {table}\n"

        for column in columns:
            schema_text += (
                f"  - {column['name']} "
                f"({column['type']})"
            )

    prompt = f"""
You are QueryPilot, an expert MySQL Text-to-SQL engine.

Convert the user's natural language question into ONE valid
MySQL SELECT query.

USER QUESTION:
{question}

DETECTED INTENT:
{intent}

DATABASE SCHEMA:
{schema_text}

STRICT RULES:

1. Return ONLY the SQL query.
2. Generate SELECT queries only.
3. Never generate INSERT, UPDATE, DELETE, DROP, ALTER,
   TRUNCATE, CREATE, or other destructive statements.
4. Use ONLY tables and columns present in the provided schema.
5. Use correct JOIN conditions based on the schema.
6. Do not invent tables or columns.
7. Use MySQL syntax.
8. Do not wrap the SQL in markdown code fences.
9. Do not add explanations.
"""

    response = client.models.generate_content(
       model="gemini-2.5-flash",
        contents=prompt
    )

    sql = response.text.strip()

    # Remove accidental markdown fences
    sql = sql.replace("```sql", "").replace("```", "").strip()

    return sql