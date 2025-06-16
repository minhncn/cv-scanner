import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("DATABASE_URL environment variable is not set.")
    exit(1)

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Database connection successful! Result:", result.scalar())
except OperationalError as e:
    print("Database connection failed:", e)
except Exception as e:
    print("Unexpected error:", e)
