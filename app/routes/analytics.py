from fastapi import APIRouter

from app.services.prouni_service import (
    get_all_data
)

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


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