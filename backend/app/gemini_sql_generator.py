import os
from functools import lru_cache
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in .env")

client = genai.Client(api_key=GEMINI_API_KEY)


def _format_schema_with_relationships(schema: dict, relationships: dict = None) -> str:
    """Format schema efficiently with relationship hints for the prompt."""
    lines = []

    for table, columns in schema.items():
        lines.append(f"TABLE: {table}")
        for column in columns:
            lines.append(f"  - {column['name']} ({column['type']})")

        # Add relationship hints
        if relationships and table in relationships:
            rels = relationships[table]
            if rels:
                lines.append(f"  RELATIONSHIPS:")
                for rel in rels:
                    lines.append(f"    - {rel.get('join_key')} → {rel.get('table')}")

        lines.append("")  # Blank line between tables

    return "\n".join(lines)


def generate_sql_with_gemini(
    question: str,
    intent: str,
    schema: dict,
    relationships: dict = None
) -> str:
    """Generate SQL using Gemini API with relationship awareness."""

    schema_text = _format_schema_with_relationships(schema, relationships)

    prompt = f"""You are QueryPilot, an expert MySQL Text-to-SQL engine specializing in multi-table queries.

Convert the user's natural language question into ONE valid MySQL SELECT query.

USER QUESTION:
{question}

DETECTED INTENT:
{intent}

DATABASE SCHEMA:
{schema_text}

STRICT RULES:

1. Return ONLY the SQL query (no markdown, no explanations).
2. Generate SELECT queries only - NEVER INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE.
3. Use ONLY tables and columns present in the schema.
4. For queries involving multiple tables, use appropriate JOINs based on the relationship hints.
5. Use correct column aliases when needed for clarity.
6. Use MySQL syntax (not PostgreSQL or other dialects).
7. Add WHERE clauses to filter results appropriately.
8. Use GROUP BY and aggregations when counting or summarizing.
9. Limit results to 100 rows if not specified.
10. Clean table names in output (remove session prefix if referring to base tables).

IMPORTANT: When multiple tables are available, infer which tables to JOIN based on the question context.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    sql = response.text.strip()

    # Remove accidental markdown fences
    sql = sql.replace("```sql", "").replace("```", "").strip()

    return sql

