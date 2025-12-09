from sqlalchemy import create_engine

DB_URL = "postgresql://postgres:simple123@localhost:5432/social_book"

engine = create_engine(DB_URL)

try:
    with engine.connect() as conn:
        print("✅ Database connected successfully!")
except Exception as e:
    print("❌ Connection failed:", e)
