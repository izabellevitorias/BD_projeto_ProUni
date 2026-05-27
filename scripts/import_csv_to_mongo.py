from pathlib import Path
import time

import pandas as pd
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from database import MONGO_COLLECTION, MONGO_DB, MONGO_URI


CSV_PATH = Path(__file__).resolve().parent.parent / "app" / "data" / "ProuniRelatorioDadosAbertos2020.csv"
BATCH_SIZE = 1000


def wait_for_mongo(client):
    for _ in range(30):
        try:
            client.admin.command("ping")
            return
        except ServerSelectionTimeoutError:
            time.sleep(1)

    client.admin.command("ping")


def main():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1000)
    wait_for_mongo(client)

    collection = client[MONGO_DB][MONGO_COLLECTION]

    if collection.estimated_document_count() > 0:
        print("Collection ja possui dados. Importacao ignorada.")
        return

    print("Importando CSV para o MongoDB...")

    total = 0
    for chunk in pd.read_csv(CSV_PATH, sep=";", encoding="latin1", chunksize=BATCH_SIZE):
        records = chunk.where(pd.notnull(chunk), None).to_dict("records")
        if records:
            collection.insert_many(records)
            total += len(records)
            print(f"{total} documentos importados")

    print(f"Importacao concluida: {total} documentos.")


if __name__ == "__main__":
    main()
