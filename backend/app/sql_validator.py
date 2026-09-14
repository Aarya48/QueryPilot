import re

import sqlglot
from sqlglot import exp


FORBIDDEN_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "RENAME",
    "GRANT",
    "REVOKE",
]


def validate_sql(sql: str, schema: dict) -> tuple[bool, str]:

    if not sql or not sql.strip():
        return False, "Generated SQL is empty."

    sql = sql.strip()
    sql_without_semicolon = sql.rstrip(";").strip()

    # ==========================================
    # 1. ONLY SELECT
    # ==========================================

    if not re.match(
        r"^SELECT\b",
        sql_without_semicolon,
        re.IGNORECASE
    ):
        return False, "Only SELECT queries are allowed."

    # ==========================================
    # 2. FORBIDDEN KEYWORDS
    # ==========================================

    for keyword in FORBIDDEN_KEYWORDS:

        pattern = rf"\b{keyword}\b"

        if re.search(
            pattern,
            sql_without_semicolon,
            re.IGNORECASE
        ):
            return False, f"Forbidden SQL keyword detected: {keyword}"

    # ==========================================
    # 3. PARSE SQL
    # ==========================================

    try:

        parsed = sqlglot.parse_one(
            sql_without_semicolon,
            dialect="mysql"
        )

    except Exception as e:

        return False, f"Invalid SQL syntax: {str(e)}"

    # ==========================================
    # 4. CHECK TABLES
    # ==========================================

    valid_tables = set(schema.keys())

    used_tables = {
        table.name
        for table in parsed.find_all(exp.Table)
    }

    for table in used_tables:

        if table not in valid_tables:

            return False, (
                f"Unknown table referenced: {table}"
            )

    # ==========================================
    # 5. CHECK COLUMNS
    # ==========================================

    table_columns = {
        table: {
            column["name"]
            for column in columns
        }
        for table, columns in schema.items()
    }

    valid_columns = set()

    for columns in table_columns.values():
        valid_columns.update(columns)

    for column in parsed.find_all(exp.Column):

        column_name = column.name

        if column_name == "*":
            continue

        # Allow SQL aliases / generated expressions
        if column_name not in valid_columns:
            return False, (
                f"Unknown column referenced: {column_name}"
            )

    return True, "SQL is valid and matches the database schema."