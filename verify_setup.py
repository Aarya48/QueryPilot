#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QueryPilot - Complete Setup & Verification Script

This script verifies that:
1. All required files are in place
2. Models load correctly
3. Database connection works
4. All dependencies are installed
"""

import sys
import os
from pathlib import Path

def print_section(title):
    """Print a section header"""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")

def print_success(msg):
    """Print success message"""
    print(f"[OK] {msg}")

def print_error(msg):
    """Print error message"""
    print(f"[ERROR] {msg}")

def print_warning(msg):
    """Print warning message"""
    print(f"[WARN] {msg}")

def check_file_exists(path, description):
    """Check if a file exists"""
    p = Path(path)
    if p.exists():
        print_success(f"{description}: {path}")
        return True
    else:
        print_error(f"{description} NOT FOUND: {path}")
        return False

def main():
    print("\nQueryPilot - Complete Setup Verification\n")

    base_dir = Path(__file__).parent
    checks_passed = 0
    checks_total = 0

    # ==========================================
    # 1. CHECK FILE STRUCTURE
    # ==========================================
    print_section("FILE STRUCTURE VERIFICATION")

    files_to_check = [
        ("backend/app/main.py", "FastAPI main application"),
        ("backend/app/database.py", "Database configuration"),
        ("backend/app/upload_handler.py", "CSV upload handler"),
        ("backend/app/sql_validator.py", "SQL validator"),
        ("backend/app/gemini_sql_generator.py", "Gemini API fallback"),
        ("ml/text_to_sql_generator.py", "Text-to-SQL generator"),
        ("ml/final_text_to_sql_model/model/model.safetensors", "Trained T5 model"),
        ("ml/final_text_to_sql_model/tokenizer/tokenizer.json", "T5 tokenizer"),
        ("ml/spider_train.json", "Training dataset"),
        ("ml/spider_val.json", "Validation dataset"),
        ("ml/spider_test.json", "Test dataset"),
    ]

    for file_path, description in files_to_check:
        checks_total += 1
        if check_file_exists(base_dir / file_path, description):
            checks_passed += 1

    # ==========================================
    # 2. CHECK REDUNDANT FILES REMOVED
    # ==========================================
    print_section("REDUNDANT FILES CLEANUP")

    redundant_files = [
        ("ml/train_text_to_sql.py", "Training script"),
        ("ml/prepare_spider_dataset.py", "Data prep script"),
        ("ml/train_intent.py", "Intent training"),
        ("ml/test_text_to_sql.py", "Test file"),
        ("backend/test_aiven.py", "Test file"),
    ]

    for file_path, description in redundant_files:
        checks_total += 1
        p = base_dir / file_path
        if not p.exists():
            print_success(f"{description} removed")
            checks_passed += 1
        else:
            print_warning(f"{description} still exists: {file_path}")

    # ==========================================
    # 3. CHECK ENVIRONMENT
    # ==========================================
    print_section("ENVIRONMENT CONFIGURATION")

    env_file = base_dir / ".env"
    checks_total += 1
    if env_file.exists():
        print_success(f".env file exists")
        checks_passed += 1
    else:
        print_error(f".env file NOT found")
        print_warning("Please create .env with DATABASE_URL and GEMINI_API_KEY")

    # ==========================================
    # 4. CHECK PYTHON DEPENDENCIES
    # ==========================================
    print_section("PYTHON DEPENDENCIES")

    required_packages = [
        "fastapi",
        "sqlalchemy",
        "pymysql",
        "pandas",
        "torch",
        "transformers",
        "sqlglot",
        "joblib",
        "python-dotenv",
    ]

    for package in required_packages:
        checks_total += 1
        try:
            __import__(package)
            print_success(f"Package installed: {package}")
            checks_passed += 1
        except ImportError:
            print_error(f"Package NOT installed: {package}")

    # ==========================================
    # 5. TEST ML MODEL LOADING
    # ==========================================
    print_section("ML MODEL LOADING TEST")

    try:
        sys.path.insert(0, str(base_dir / "ml"))
        from text_to_sql_generator import TextToSQLGenerator

        checks_total += 1
        print_success("TextToSQLGenerator imported successfully")
        checks_passed += 1

        try:
            print("[INFO] Loading T5 model (this may take a moment)...")
            generator = TextToSQLGenerator()
            checks_total += 1
            print_success("T5 model loaded successfully")
            checks_passed += 1

            # Test generation
            checks_total += 1
            test_schema = {
                "users": [
                    {"name": "id", "type": "int"},
                    {"name": "name", "type": "str"},
                ]
            }
            sql = generator.generate("Show all users", test_schema)
            if sql and "SELECT" in sql.upper():
                print_success(f"Model inference works")
                print(f"  Generated SQL: {sql}")
                checks_passed += 1
            else:
                print_error(f"Model inference produced invalid SQL: {sql}")

        except FileNotFoundError as e:
            print_error(f"Model files not found: {e}")
        except Exception as e:
            print_error(f"Failed to load T5 model: {e}")

    except ImportError as e:
        print_error(f"Failed to import TextToSQLGenerator: {e}")

    # ==========================================
    # 6. TEST DATABASE CONNECTION
    # ==========================================
    print_section("DATABASE CONNECTION TEST")

    try:
        sys.path.insert(0, str(base_dir / "backend"))
        from app.database import engine
        checks_total += 1

        try:
            with engine.connect() as conn:
                print_success("Database connection successful")
                checks_passed += 1
        except Exception as e:
            print_error(f"Database connection failed: {e}")
            print_warning("Check your DATABASE_URL in .env")

    except Exception as e:
        print_error(f"Failed to import database: {e}")

    # ==========================================
    # 7. FINAL SUMMARY
    # ==========================================
    print_section("VERIFICATION SUMMARY")

    percentage = (checks_passed / checks_total * 100) if checks_total > 0 else 0

    print(f"\nTotal Checks: {checks_total}")
    print(f"Passed: {checks_passed}")
    print(f"Failed: {checks_total - checks_passed}")
    print(f"Success Rate: {percentage:.1f}%")

    if checks_passed == checks_total:
        print("\n[SUCCESS] All checks passed! Project is ready to run.")
        print("\nNext steps:")
        print("1. cd backend")
        print("2. uvicorn app.main:app --reload")
        print("3. Open http://localhost:8000/docs in browser")
        return 0
    else:
        print(f"\n[ALERT] {checks_total - checks_passed} check(s) failed. Fix them above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
