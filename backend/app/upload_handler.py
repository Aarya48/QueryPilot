import re
import uuid

import pandas as pd
from sqlalchemy import inspect, text

from app.database import engine


MAX_FILES = 5


def create_session_id():
    return uuid.uuid4().hex[:8]


def create_table_name(session_id: str, filename: str):
    """
    Creates a clean table name for the uploaded CSV.
    Example: session_a81f92_customers (no extra suffixes)
    """
    # Remove extension
    name = filename.rsplit(".", 1)[0]

    # Keep only safe characters (lowercase for consistency)
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name).lower()

    # Remove trailing underscores
    name = name.rstrip("_")

    return f"session_{session_id}_{name}"


def detect_relationships(table_names: list, engine) -> dict:
    """
    Detect potential foreign key relationships between tables.
    Returns dict of {table: [related_tables]}
    """
    inspector = inspect(engine)
    relationships = {}

    # Get all columns from all tables
    table_columns = {}
    for table_name in table_names:
        if not inspector.has_table(table_name):
            continue
        columns = inspector.get_columns(table_name)
        table_columns[table_name] = {col["name"]: str(col["type"]) for col in columns}

    # Infer relationships based on naming patterns
    for table1 in table_names:
        if table1 not in table_columns:
            continue

        relationships[table1] = []
        cols1 = table_columns[table1]

        for table2 in table_names:
            if table2 == table1 or table2 not in table_columns:
                continue

            cols2 = table_columns[table2]

            # Check for foreign key patterns
            # Pattern 1: table2_id in table1 -> links to table2
            table2_singular = table2.rstrip("s")  # customers -> customer

            for col_name in cols1.keys():
                if col_name in [f"{table2}_id", f"{table2_singular}_id"]:
                    relationships[table1].append({
                        "table": table2,
                        "join_key": col_name
                    })
                    break

    return relationships


def csv_to_table(file_path: str, table_name: str):
    """
    Read CSV and create a new MySQL table with optimizations for large files.
    Uses chunked reading and batch inserts.
    """
    try:
        # Read CSV with memory optimization
        df = pd.read_csv(
            file_path,
            dtype_backend='numpy_nullable',  # Better memory usage
            low_memory=False  # Avoid mixed type warnings
        )

        if df.empty:
            raise ValueError("CSV file is empty.")

        # Clean column names (remove special chars, lowercase)
        df.columns = [
            col.lower().replace(" ", "_").replace("-", "_")
            for col in df.columns
        ]

        # Convert data types intelligently
        df = df.infer_objects()

        # Create table
        df.to_sql(
            table_name,
            con=engine,
            if_exists="fail",
            index=False,
            chunksize=5000,
            method='multi'
        )

        # Add indexes on key columns (async-friendly)
        inspector = inspect(engine)
        columns = {col["name"]: col for col in inspector.get_columns(table_name)}

        with engine.connect() as conn:
            # Index ID columns for faster joins
            for col_name in columns.keys():
                if col_name.endswith("_id") or col_name == "id":
                    try:
                        index_name = f"idx_{table_name}_{col_name}"
                        conn.execute(text(f"CREATE INDEX {index_name} ON {table_name}({col_name})"))
                        conn.commit()
                    except Exception:
                        pass  # Index might already exist

        return len(df), list(df.columns)

    except Exception as e:
        raise ValueError(f"Error processing CSV: {str(e)}")


def get_table_schema(table_names):
    """
    Get schema for uploaded tables with relationship info.
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


def get_relationships_info(table_names):
    """
    Get relationship information between tables.
    """
    return detect_relationships(table_names, engine)
