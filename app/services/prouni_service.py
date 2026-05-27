import pandas as pd

from database import collection


def get_all_data():

    dados = list(
        collection.find({}, {"_id": 0})
    )

    return pd.DataFrame(dados)


def get_estado_data(estado):

    dados = list(
        collection.find(
            {"UF_BENEFICIARIO": estado},
            {"_id": 0}
        )
    )

    return pd.DataFrame(dados)
