import streamlit as st

from services.prouni_service import (
    get_all_data,
    get_estado_data
)

st.set_page_config(
    page_title="Prouni Analytics",
    layout="wide"
)

st.title("Prouni Analytics 2020")

df = get_all_data()

if df.empty:
    st.warning("Nenhum dado encontrado para montar os dashboards.")
    st.stop()

estado = st.selectbox(
    "Estado",
    sorted(
        df["UF_BENEFICIARIO"]
        .dropna()
        .unique()
    )
)

filtrado = get_estado_data(estado)

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Total Bolsas",
        len(filtrado)
    )

with col2:

    st.metric(
        "Cursos",
        filtrado[
            "NOME_CURSO_BOLSA"
        ].nunique()
    )

st.subheader("Distribuição por Sexo")

sexo = filtrado[
    "SEXO_BENEFICIARIO"
].value_counts()

st.bar_chart(sexo)

st.subheader("Top Cursos")

top = filtrado[
    "NOME_CURSO_BOLSA"
].value_counts().head(10)

st.bar_chart(top)
