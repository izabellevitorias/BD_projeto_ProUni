from fastapi import APIRouter

from services.prouni_service import get_all_data, grafo_universidades_por_estado

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/grafo-universidades")
def grafo_universidades():
    return grafo_universidades_por_estado()


@router.get("/estados")
def estados():

    df = get_all_data()

    return sorted(
        df["UF_BENEFICIARIO"]
        .dropna()
        .unique()
        .tolist()
    )


@router.get("/total-bolsas")
def total_bolsas():

    df = get_all_data()

    return {
        "total": len(df)
    }
