import re


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


def validate_sql(sql: str) -> tuple[bool, str]:

    if not sql or not sql.strip():
        return False, "Generated SQL is empty."

    sql = sql.strip()

    # Remove trailing semicolon
    sql_without_semicolon = sql.rstrip(";").strip()

    # Only SELECT queries are allowed
    if not re.match(r"^SELECT\b", sql_without_semicolon, re.IGNORECASE):
        return False, "Only SELECT queries are allowed."

    # Check dangerous SQL keywords
    for keyword in FORBIDDEN_KEYWORDS:

        pattern = rf"\b{keyword}\b"

        if re.search(pattern, sql_without_semicolon, re.IGNORECASE):
            return False, f"Forbidden SQL keyword detected: {keyword}"

    return True, "SQL is valid."