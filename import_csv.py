import pandas as pd
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

df = pd.read_csv(
    "data/ProuniRelatorioDadosAbertos2020.csv",
    sep=";",
    encoding="latin1"
)

dados = df.to_dict(orient="records")

collection.insert_many(dados)

print("Dados importados!")