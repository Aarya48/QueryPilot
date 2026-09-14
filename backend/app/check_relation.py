from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "database" / "data"


def get_unique_ids(file_name, column_name, chunksize=100_000):
   
    file_path = DATA_DIR / file_name

    unique_ids = set()

    print(f"Reading {file_name}...")

    for chunk in pd.read_csv(
        file_path,
        usecols=[column_name],
        chunksize=chunksize
    ):
        unique_ids.update(chunk[column_name].dropna().unique())

    print(f"Found {len(unique_ids):,} unique IDs")

    return unique_ids


def check_relationship(
    child_file,
    child_column,
    parent_file,
    parent_column
):
    print("\n" + "=" * 70)
    print(
        f"{child_file}.{child_column} "
        f"→ {parent_file}.{parent_column}"
    )
    print("=" * 70)

    parent_ids = get_unique_ids(parent_file, parent_column)

    child_path = DATA_DIR / child_file

    total_rows = 0
    valid_rows = 0
    invalid_rows = 0

    print(f"\nChecking {child_file}...")

    for chunk in pd.read_csv(
        child_path,
        usecols=[child_column],
        chunksize=100_000
    ):
        total_rows += len(chunk)

        valid_mask = chunk[child_column].isin(parent_ids)

        valid_rows += valid_mask.sum()
        invalid_rows += (~valid_mask).sum()

    valid_percentage = (valid_rows / total_rows) * 100
    invalid_percentage = (invalid_rows / total_rows) * 100

    print(f"\nTotal rows      : {total_rows:,}")
    print(f"Valid references: {valid_rows:,} ({valid_percentage:.2f}%)")
    print(f"Invalid refs    : {invalid_rows:,} ({invalid_percentage:.2f}%)")

    if invalid_rows == 0:
        print("RESULT: ✓ Relationship looks valid")
    else:
        print("RESULT: ⚠ Some references do not exist")


def main():

    print("=" * 70)
    print("QUERY PILOT - RELATIONSHIP CHECKER")
    print("=" * 70)

    # orders → customers
    check_relationship(
        "orders.csv",
        "customer_id",
        "customers.csv",
        "customer_id"
    )

    # order_items → orders
    check_relationship(
        "order_items.csv",
        "order_id",
        "orders.csv",
        "order_id"
    )

    # order_items → products
    check_relationship(
        "order_items.csv",
        "product_id",
        "products.csv",
        "product_id"
    )

    # reviews → products
    check_relationship(
        "product_reviews.csv",
        "product_id",
        "products.csv",
        "product_id"
    )

    # reviews → customers
    check_relationship(
        "product_reviews.csv",
        "customer_id",
        "customers.csv",
        "customer_id"
    )


if __name__ == "__main__":
    main()