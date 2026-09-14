from pathlib import Path
import pandas as pd


# Project ke database/data folder ka path
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "database" / "data"


def inspect_csv(file_path):
    print("\n" + "=" * 70)
    print(f"FILE: {file_path.name}")
    print("=" * 70)

    try:
        df = pd.read_csv(file_path)

        print(f"Rows    : {df.shape[0]:,}")
        print(f"Columns : {df.shape[1]}")

        print("\nColumns:")
        for column in df.columns:
            print(f"  - {column}")

        print("\nData Types:")
        print(df.dtypes)

        print("\nMissing Values:")
        missing = df.isnull().sum()
        print(missing[missing > 0])

        print("\nFirst 3 Rows:")
        print(df.head(3).to_string(index=False))

    except Exception as e:
        print(f"ERROR: {e}")


def main():
    print("=" * 70)
    print("QUERY PILOT - DATASET INSPECTOR")
    print("=" * 70)

    if not DATA_DIR.exists():
        print(f"\nData folder not found:")
        print(DATA_DIR)
        return

    csv_files = list(DATA_DIR.glob("*.csv"))

    if not csv_files:
        print("\nNo CSV files found!")
        return

    print(f"\nFound {len(csv_files)} CSV files.")

    for file_path in sorted(csv_files):
        inspect_csv(file_path)


if __name__ == "__main__":
    main()