import sys
import os

# Add the BACKEND directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'BACKEND'))
sys.path.append(backend_path)

from sqlalchemy import text
from app.db.session import engine

def migrate():
    with engine.connect() as conn:
        print("Checking for otp_code column...")
        # Check if column exists
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='otp_code'"))
        if not result.fetchone():
            print("Adding otp_code and otp_expires_at columns to users table...")
            conn.execute(text("ALTER TABLE users ADD COLUMN otp_code VARCHAR"))
            conn.execute(text("ALTER TABLE users ADD COLUMN otp_expires_at TIMESTAMP"))
            conn.commit()
            print("Migration successful.")
        else:
            print("Columns already exist.")

if __name__ == "__main__":
    migrate()
