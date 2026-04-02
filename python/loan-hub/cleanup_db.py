import sqlalchemy
from sqlalchemy import text
from database import engine

def cleanup():
    try:
        with engine.connect() as connection:
            print("Wiping public schema...")
            # Drop the public schema and recreate it
            connection.execute(text("DROP SCHEMA public CASCADE"))
            connection.execute(text("CREATE SCHEMA public"))
            connection.commit()
            print("Successfully cleaned up database.")
    except Exception as e:
        print(f"Error cleaning up database: {e}")

if __name__ == "__main__":
    cleanup()
