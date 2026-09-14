import pandas as pd
from pathlib import Path

from app.database import engine


DATA_DIR = Path(__file__).resolve().parents[2] / "database" / "data"


# Development dataset size
CUSTOMERS_LIMIT = 50_000
ORDERS_LIMIT = 200_000
ORDER_ITEMS_LIMIT = 500_000
REVIEWS_LIMIT = 100_000


def import_customers():
    print("\n[1/5] Importing customers...")

    df = pd.read_csv(
        DATA_DIR / "customers.csv",
        nrows=CUSTOMERS_LIMIT
    )

    df.to_sql(
        "customers",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=5000
    )

    print(f"Customers imported: {len(df):,}")


def import_products():
    print("\n[2/5] Importing products...")

    df = pd.read_csv(
        DATA_DIR / "products.csv"
    )

    df.to_sql(
        "products",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=5000
    )

    print(f"Products imported: {len(df):,}")


def import_orders():
    print("\n[3/5] Importing orders...")

    customers = pd.read_sql(
        "SELECT customer_id FROM customers",
        con=engine
    )

    valid_customer_ids = set(customers["customer_id"])

    imported = 0

    for chunk in pd.read_csv(
        DATA_DIR / "orders.csv",
        chunksize=10000
    ):
        chunk = chunk[
            chunk["customer_id"].isin(valid_customer_ids)
        ]

        remaining = ORDERS_LIMIT - imported

        if remaining <= 0:
            break

        chunk = chunk.head(remaining)

        if len(chunk) == 0:
            continue

        chunk.to_sql(
            "orders",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=5000
        )

        imported += len(chunk)

        print(f"Orders imported: {imported:,}")

        if imported >= ORDERS_LIMIT:
            break


def import_order_items():
    print("\n[4/5] Importing order_items...")

    orders = pd.read_sql(
        "SELECT order_id FROM orders",
        con=engine
    )

    valid_order_ids = set(orders["order_id"])

    imported = 0

    for chunk in pd.read_csv(
        DATA_DIR / "order_items.csv",
        chunksize=20000
    ):
        chunk = chunk[
            chunk["order_id"].isin(valid_order_ids)
        ]

        remaining = ORDER_ITEMS_LIMIT - imported

        if remaining <= 0:
            break

        chunk = chunk.head(remaining)

        if len(chunk) == 0:
            continue

        chunk.to_sql(
            "order_items",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=5000
        )

        imported += len(chunk)

        print(f"Order items imported: {imported:,}")

        if imported >= ORDER_ITEMS_LIMIT:
            break


def import_reviews():
    print("\n[5/5] Importing product_reviews...")

    customers = pd.read_sql(
        "SELECT customer_id FROM customers",
        con=engine
    )

    valid_customer_ids = set(customers["customer_id"])

    products = pd.read_sql(
        "SELECT product_id FROM products",
        con=engine
    )

    valid_product_ids = set(products["product_id"])

    imported = 0

    for chunk in pd.read_csv(
        DATA_DIR / "product_reviews.csv",
        chunksize=10000
    ):
        chunk = chunk[
            chunk["customer_id"].isin(valid_customer_ids)
            & chunk["product_id"].isin(valid_product_ids)
        ]

        remaining = REVIEWS_LIMIT - imported

        if remaining <= 0:
            break

        chunk = chunk.head(remaining)

        if len(chunk) == 0:
            continue

        chunk.to_sql(
            "product_reviews",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=5000
        )

        imported += len(chunk)

        print(f"Reviews imported: {imported:,}")

        if imported >= REVIEWS_LIMIT:
            break


def main():
    print("====================================")
    print("       QueryPilot Data Import")
    print("====================================")

    import_customers()
    import_products()
    import_orders()
    import_order_items()
    import_reviews()

    print("\n====================================")
    print("       IMPORT COMPLETED 🚀")
    print("====================================")


if __name__ == "__main__":
    main()