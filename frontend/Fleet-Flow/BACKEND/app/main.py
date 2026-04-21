from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, users, warehouses, inventory, shipments
from app.db.base import Base
from app.db.session import engine
from fastapi.responses import RedirectResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Warehouse Management System",
    description="RBAC-based Warehouse Kingdom",
    version="1.0.0",
    docs_url="/docs"
)

#  Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return RedirectResponse(url="/docs")

app.include_router(auth.router,       prefix="/auth",       tags=["Auth"])
app.include_router(users.router,      prefix="/users",      tags=["Admin"])
app.include_router(warehouses.router, prefix="/warehouses", tags=["Warehouses"])
app.include_router(inventory.router,  prefix="/inventory",  tags=["Inventory"])
app.include_router(shipments.router,  prefix="/shipments",  tags=["Shipments"])