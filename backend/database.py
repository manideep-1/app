"""Shared MongoDB connection and get_db dependency for use by server and auth."""
import os
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")


def _get_required_env(name: str) -> str:
    val = os.environ.get(name)
    if not val or not str(val).strip():
        raise RuntimeError(f"Missing required environment variable: {name}")
    return str(val).strip()


mongo_url = _get_required_env("MONGO_URL")
db_name = _get_required_env("DB_NAME")
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]


async def get_db():
    return db
