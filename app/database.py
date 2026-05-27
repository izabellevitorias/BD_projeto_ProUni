import os

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(
    os.getenv("MONGODB_URI")
)

db = client[
    os.getenv("MONGODB_DB")
]

collection = db[
    os.getenv("MONGODB_COLLECTION")
]