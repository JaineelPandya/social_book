from sqlalchemy import create_engine, text

DB_USER = "postgres"
DB_PASSWORD = "Jhp@45678"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "postgres"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print("✅ Using DB URL:", DATABASE_URL)

engine = create_engine(DATABASE_URL)

with engine.connect() as connection:
    print("✅ Connected to PostgreSQL successfully")

    query = text("SELECT datname FROM pg_database;")
    result = connection.execute(query)

    print("\n✅ Databases found:\n")
    for row in result:
        print(row[0])
