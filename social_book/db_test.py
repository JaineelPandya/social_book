from sqlalchemy import create_engine, text
import urllib.parse

# ✅ Your actual DB credentials
USER = "postgres"
PASSWORD = "Jhp@45678"
HOST = "localhost"
PORT = "5432"
DB_NAME = "social_book"

# ✅ Encode password safely
ENCODED_PASSWORD = urllib.parse.quote_plus(PASSWORD)

DB_URL = f"postgresql://{USER}:{ENCODED_PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

print("✅ Using encoded DB URL (password hidden)")

engine = create_engine(DB_URL)

with engine.connect() as connection:
    print("\n✅ Connected to DB:", DB_NAME)

    # ✅ Show all tables
    result = connection.execute(text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    """))

    tables = [row[0] for row in result]

    print("\n✅ Tables in database:")
    for table in tables:
        print("-", table)

    # ✅ Fetch users from correct Django custom user table
    if "accounts_customuser" in tables:
        print("\n✅ Data from accounts_customuser:\n")

        users = connection.execute(text("""
            SELECT id, email, is_active, is_staff
            FROM accounts_customuser
        """))

        for user in users:
            print(dict(user._mapping))
    else:
        print("\n❌ accounts_customuser table not found.")
