import re
import uuid

import pandas as pd
from sqlalchemy import inspect

from app.database import engine


MAX_FILES = 5


def create_session_id():
    return uuid.uuid4().hex[:8]


def create_table_name(session_id: str, filename: str):
    """
    Creates a unique table name for the uploaded CSV.
    Example:
    session_a81f92_customers
    """

    name = filename.rsplit(".", 1)[0]

    # Keep only safe characters
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)

    return f"session_{session_id}_{name}"


def csv_to_table(file_path: str, table_name: str):
    """
    Read CSV and create a new MySQL table.
    """

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError("CSV file is empty.")

    df.to_sql(
        table_name,
        con=engine,
        if_exists="fail",
        index=False,
        chunksize=5000
    )

    return len(df), list(df.columns)


def get_table_schema(table_names):
    """
    Get schema for uploaded tables.
    """

    inspector = inspect(engine)

    schema = {}

    for table_name in table_names:

        if not inspector.has_table(table_name):
            continue

        columns = inspector.get_columns(table_name)

        schema[table_name] = [
            {
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column["nullable"]
            }
            for column in columns
        ]

    return schema