"""
Simple script to connect to a local PostgreSQL database using SQLAlchemy,
list public tables and show up to 10 rows from `accounts_uploadedfile` (if present).

It reads DB connection from the environment variable `DATABASE_URL`.
If not set, it will use sensible defaults matching the dashboard screenshot:
  postgresql+psycopg2://social_user:your_password@localhost:5432/social_book_pg

Run with the project's Python interpreter, for example:
  C:/Users/Jaineel/Desktop/coding/Markytrics.ai/social_book/env/Scripts/python.exe scripts/fetch_postgres_via_sqlalchemy.py

The script prints results and any connection errors.
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

DEFAULT_DB_URL = (
    os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://social_user:your_password@localhost:5432/social_book_pg",
    )
)

QUERY_LIST_TABLES = """
SELECT schemaname, tablename
FROM pg_catalog.pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY schemaname, tablename
LIMIT 200;
"""

# Try to query a common app table (UploadedFile) if it exists
SAMPLE_TABLE = "accounts_uploadedfile"
QUERY_SAMPLE = f"SELECT * FROM {SAMPLE_TABLE} LIMIT 10;"


def main():
    db_url = DEFAULT_DB_URL
    print(f"Using DB URL: {db_url}")

    try:
        engine = create_engine(db_url, future=True)
    except Exception as e:
        print("Failed to create SQLAlchemy engine:", e, file=sys.stderr)
        sys.exit(2)

    try:
        with engine.connect() as conn:
            print("Connected to DB. Listing tables (public schemas)...")
            tables = conn.execute(text(QUERY_LIST_TABLES)).fetchall()
            if tables:
                for row in tables:
                    print("-", row[0], ".", row[1])
            else:
                print("No user tables found (public schemas).")

            # Try sample table
            print(f"\nTrying to fetch sample rows from '{SAMPLE_TABLE}' (if exists)...")
            try:
                rows = conn.execute(text(QUERY_SAMPLE)).fetchall()
                if rows:
                    print(f"Found {len(rows)} rows in {SAMPLE_TABLE}:")
                    # Print header limited to first 6 columns
                    for r in rows:
                        print(r)
                else:
                    print(f"Table '{SAMPLE_TABLE}' exists but has no rows (or query returned empty).")
            except SQLAlchemyError as se:
                # Likely table doesn't exist — show the error message but continue
                print(f"Could not query {SAMPLE_TABLE}: {se}")

    except SQLAlchemyError as err:
        print("Database query error:", err, file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
