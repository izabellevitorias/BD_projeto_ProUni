from functools import lru_cache
from pathlib import Path

import pandas as pd
from pymongo.errors import PyMongoError

from database import collection


CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "ProuniRelatorioDadosAbertos2020.csv"


@lru_cache(maxsize=1)
def get_csv_data():
    return pd.read_csv(CSV_PATH, sep=";", encoding="latin1")


def get_all_data():
    try:
        dados = list(
            collection.find({}, {"_id": 0})
        )

        if dados:
            return pd.DataFrame(dados)
    except PyMongoError:
        pass

    return get_csv_data()


def get_estado_data(estado):
    df = get_all_data()
    return df[df["UF_BENEFICIARIO"] == estado]
