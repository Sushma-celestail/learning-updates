import traceback
from database import SessionLocal, verify_db_connection
from services.user_service import UserService
from models.schemas import UserCreate
from models.enums import UserRole
from config import settings

def debug_db():
    print("Verifying DB connection...")
    verify_db_connection()
    
    db = SessionLocal()
    try:
        user_service = UserService(db)
        print(f"Checking for admin user: {settings.ADMIN_USERNAME}")
        try:
            user_service.get_user_by_username(settings.ADMIN_USERNAME)
            print("Admin user exists.")
        except Exception:
            print("Admin user does not exist. Seeding...")
            admin_data = UserCreate(
                username=settings.ADMIN_USERNAME,
                password=settings.ADMIN_PASSWORD,
                email=settings.ADMIN_EMAIL,
                phone="0000000000",
                monthly_income=1000000
            )
            admin = user_service.register_user(admin_data)
            print("User registered. Setting role to ADMIN...")
            admin.role = UserRole.ADMIN
            print("Committing...")
            db.commit()
            print("Admin user seeded successfully.")
    except Exception as e:
        print("\n--- DATABASE ERROR ---")
        traceback.print_exc()
        print("--- END OF TRACEBACK ---")
    finally:
        db.close()

if __name__ == "__main__":
    debug_db()
