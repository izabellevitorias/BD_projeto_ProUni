from functools import lru_cache
from pathlib import Path

import pandas as pd
from pymongo.errors import PyMongoError

from database import collection


CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "ProuniRelatorioDadosAbertos2020.csv"

SIGLAS_CONHECIDAS = {
    "UNIVERSIDADE PAULISTA": "UNIP",
    "UNIVERSIDADE ESTACIO DE SA": "ESTACIO",
    "CENTRO UNIVERSITARIO LEONARDO DA VINCI": "UNIASSELVI",
    "CENTRO UNIVERSITARIO DE MARINGA": "UNICESUMAR",
    "PONTIFICIA UNIVERSIDADE CATOLICA DE MINAS GERAIS": "PUC MINAS",
    "UNIVERSIDADE PITAGORAS UNOPAR": "UNOPAR",
    "UNIVERSIDADE CIDADE DE SAO PAULO": "UNICID",
    "UNIVERSIDADE CRUZEIRO DO SUL": "UNICSUL",
    "CENTRO UNIVERSITARIO DAS FACULDADES METROPOLITANAS UNIDAS": "FMU",
    "UNIVERSIDADE SAO JUDAS TADEU": "USJT",
    "CENTRO UNIVERSITARIO ANHANGUERA": "ANHANGUERA",
}

SIGLA_STOP_WORDS = {"A", "AS", "DA", "DAS", "DE", "DO", "DOS", "E", "EM", "PARA"}


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


def normalize_text(value):
    text = str(value).strip().upper()
    replacements = str.maketrans(
        "ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ",
        "AAAAAEEEEIIIIOOOOOUUUUC",
    )
    return text.translate(replacements)


def make_university_acronym(name):
    normalized = normalize_text(name)

    words = normalized.replace("-", " ").split()
    if len(words) == 1 and 2 <= len(normalized) <= 14:
        return normalized

    for full_name, acronym in SIGLAS_CONHECIDAS.items():
        if full_name in normalized:
            return acronym

    if "-" in normalized:
        suffix = normalized.split("-")[-1].strip()
        suffix_words = suffix.split()
        if suffix_words and len(suffix_words[0]) >= 3:
            return suffix_words[0][:14]

    words = [
        word
        for word in words
        if word not in SIGLA_STOP_WORDS
    ]

    if not words:
        return "NI"

    return "".join(word[0] for word in words[:6])[:10]


def grafo_universidades_por_estado():
    df = get_all_data()
    nodes = []
    edges = []
    node_ids = set()

    for uf, grupo in df.groupby("UF_BENEFICIARIO"):
        universidades = sorted(
            {
                make_university_acronym(universidade)
                for universidade in grupo["NOME_IES_BOLSA"].dropna().unique()
            }
        )

        for universidade in universidades:
            if universidade not in node_ids:
                nodes.append({"id": universidade})
                node_ids.add(universidade)

        for index, origem in enumerate(universidades):
            for destino in universidades[index + 1:]:
                edges.append({"source": origem, "target": destino, "estado": uf})

    return {"nodes": nodes, "edges": edges}
