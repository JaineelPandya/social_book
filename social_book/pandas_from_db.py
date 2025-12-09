import pandas as pd
from sqlalchemy import create_engine
import numpy as np

# ✅ 1. PostgreSQL DB URL (USE YOUR CORRECT PASSWORD)
DB_URL = "postgresql://postgres:simple123@localhost:5432/social_book"
engine = create_engine(DB_URL)

# ✅ 2. Fetch Django Custom User Data from DB
query = """
SELECT id, email, birth_year, public_visibility
FROM accounts_customuser
"""

df = pd.read_sql(query, engine)

print("\n✅ USER DATA FROM DJANGO DATABASE:")
print(df)

# ---------------------------------------------------
# ✅ 3. FILTER: Only Public Visible Users
# ---------------------------------------------------
df_public = df[df["public_visibility"] == True]
print("\n✅ Only Public Users:")
print(df_public)

# ---------------------------------------------------
# ✅ 4. FILTER: Users with birth_year < 2000 (Age > 25 approx)
# ---------------------------------------------------
df_age = df[df["birth_year"] < 2000]
print("\n✅ Users with birth_year < 2000:")
print(df_age)

# ---------------------------------------------------
# ✅ 5. REPLACE: Replace missing birth_year with 2000
# ---------------------------------------------------
df["birth_year"] = df["birth_year"].fillna(2000)

print("\n✅ Birth year after filling missing values:")
print(df)

# ---------------------------------------------------
# ✅ 6. CREATE SECOND DUMMY DF & APPEND
# ---------------------------------------------------
df_dummy = pd.DataFrame({
    "id": [999, 1000],
    "email": ["dummy1@test.com", "dummy2@test.com"],
    "birth_year": [1995, 1998],
    "public_visibility": [True, False]
})

print("\n✅ Dummy DataFrame:")
print(df_dummy)

# ✅ Append both
final_df = pd.concat([df, df_dummy], ignore_index=True)

print("\n✅ FINAL APPENDED DATAFRAME:")
print(final_df)
