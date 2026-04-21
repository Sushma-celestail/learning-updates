import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.core.security import hash_password
from app.core.roles import Role

# ✅ Import ALL models FIRST to register relationships
from app.models.warehouse import Warehouse
from app.models.user import User
from app.models.inventory import Inventory
from app.models.shipment import Shipment

# Create session
db = SessionLocal()

try:
    # Check if admin already exists
    existing_admin = db.query(User).filter(User.email == "admin@gmail.com").first()
    if existing_admin:
        print("[INFO] Admin already exists!")
        db.close()
        exit()
    
    # Create new admin
    admin = User(
        name="Super Admin",
        email="admin@gmail.com",
        password=hash_password("Admin123"),
        role=Role.ADMIN,
        warehouse_id=None
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print("[SUCCESS] Admin created successfully!")
    print(f"   Email: admin@gmail.com")
    print(f"   Password: Admin123")
    print(f"   Role: {admin.role}")
    
except Exception as e:
    print(f"[ERROR] Error: {e}")
    db.rollback()
finally:
    db.close()