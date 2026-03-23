from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

client = None

async def connect_mongo():
    global client
    client = AsyncIOMotorClient(MONGO_URL)
    print("✅ MongoDB connected")

async def close_mongo():
    client.close()
    print("❌ MongoDB disconnected")

def get_mongo_db():
    return client[MONGO_DB_NAME]