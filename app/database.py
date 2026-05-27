import os
from pathlib import Path

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

MONGO_URI = (os.getenv("MONGODB_URI") or "").strip()
MONGO_DB = (os.getenv("MONGODB_DB") or "").strip()
MONGO_COLLECTION = (os.getenv("MONGODB_COLLECTION") or "").strip()

if not MONGO_URI.startswith(("mongodb://", "mongodb+srv://")):
    raise ValueError(
        "MONGODB_URI invalida ou nao configurada. "
        "Ela deve comecar com 'mongodb://' ou 'mongodb+srv://'."
    )

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

if not MONGO_DB:
    raise ValueError("MONGODB_DB nao configurada.")

if not MONGO_COLLECTION:
    raise ValueError("MONGODB_COLLECTION nao configurada.")

db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]
