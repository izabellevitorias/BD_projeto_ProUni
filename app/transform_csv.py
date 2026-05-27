import pandas as pd
import os

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION")

client = MongoClient(MONGODB_URI)

db = client[MONGODB_DB]

collection = db[MONGODB_COLLECTION]

df = pd.read_csv(
    "data/ProuniRelatorioDadosAbertos2020.csv",
    sep=";",
    encoding="latin1"
)

dados = df.to_dict(orient="records")

collection.insert_many(dados)

print("Dados importados com sucesso!")