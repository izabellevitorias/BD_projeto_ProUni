import altair as alt
import pandas as pd
import streamlit as st

from services.prouni_service import get_all_data


st.set_page_config(
    page_title="ProUni Analytics",
    layout="wide",
)


st.markdown(
    """
    <style>
    .stApp {
        background: #f6f7fb;
    }

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e3e7ef;
    }

    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3 {
        color: #172033 !important;
        letter-spacing: 0;
    }

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stWidgetLabel"] p {
        color: #31415c !important;
    }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e3e7ef;
        border-radius: 8px;
        padding: 18px 18px 14px;
        box-shadow: 0 8px 24px rgba(34, 43, 69, 0.06);
    }

    div[data-testid="stMetricLabel"] p {
        color: #61708a !important;
        font-size: 0.84rem;
    }

    div[data-testid="stMetricValue"] {
        color: #172033;
        font-weight: 750;
    }

    .section-title {
        color: #172033;
        font-size: 1.05rem;
        font-weight: 700;
        margin: 0.35rem 0 0.45rem;
    }

    .caption {
        color: #61708a;
        font-size: 0.86rem;
        margin-top: -0.15rem;
        margin-bottom: 0.6rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


PALETTE = ["#2f6f73", "#d96459", "#f2b84b", "#4e79a7", "#8f5fbf", "#59a14f", "#e15759"]


@st.cache_data(show_spinner="Carregando dados...")
def load_data():
    data = get_all_data()
    text_columns = [
        "REGIAO_BENEFICIARIO",
        "UF_BENEFICIARIO",
        "TIPO_BOLSA",
        "MODALIDADE_ENSINO_BOLSA",
        "NOME_CURSO_BOLSA",
        "NOME_TURNO_CURSO_BOLSA",
        "SEXO_BENEFICIARIO",
        "RACA_BENEFICIARIO",
        "MUNICIPIO_BENEFICIARIO",
        "NOME_IES_BOLSA",
    ]

    for column in text_columns:
        if column in data.columns:
            data[column] = data[column].fillna("Nao informado").astype(str).str.strip()

    return data


def count_by(data, column, label, limit=None):
    grouped = (
        data[column]
        .value_counts()
        .rename_axis(label)
        .reset_index(name="Bolsas")
    )

    if limit:
        grouped = grouped.head(limit)

    return grouped


def polish_chart(chart):
    return (
        chart.configure(background="transparent")
        .configure_view(strokeWidth=0)
        .configure_axis(
            domain=False,
            gridColor="#e6eaf1",
            labelColor="#31415c",
            labelFontSize=12,
            titleColor="#31415c",
            tickColor="#d9deea",
        )
        .configure_legend(
            labelColor="#31415c",
            labelFontSize=12,
            titleColor="#31415c",
        )
    )


def horizontal_bar(data, x_field, y_field, color_field=None, height=340):
    color = (
        alt.Color(f"{color_field}:N", scale=alt.Scale(range=PALETTE), legend=None)
        if color_field
        else alt.value(PALETTE[0])
    )

    chart = (
        alt.Chart(data)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            x=alt.X(f"{x_field}:Q", title=None, axis=alt.Axis(grid=True, tickCount=5)),
            y=alt.Y(f"{y_field}:N", title=None, sort="-x"),
            color=color,
            tooltip=[
                alt.Tooltip(f"{y_field}:N", title=y_field),
                alt.Tooltip(f"{x_field}:Q", title="Bolsas", format=","),
            ],
        )
        .properties(height=height)
    )

    return polish_chart(chart)


def vertical_bar(data, x_field, y_field, color_field, height=320):
    chart = (
        alt.Chart(data)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X(f"{x_field}:N", title=None, sort="-y", axis=alt.Axis(labelAngle=0)),
            y=alt.Y(f"{y_field}:Q", title=None, axis=alt.Axis(grid=True, tickCount=5)),
            color=alt.Color(f"{color_field}:N", scale=alt.Scale(range=PALETTE), legend=None),
            tooltip=[
                alt.Tooltip(f"{x_field}:N", title=x_field),
                alt.Tooltip(f"{y_field}:Q", title="Bolsas", format=","),
            ],
        )
        .properties(height=height)
    )

    return polish_chart(chart)


def donut_chart(data, category_field, value_field):
    chart = (
        alt.Chart(data)
        .mark_arc(innerRadius=70, outerRadius=118, stroke="#ffffff", strokeWidth=3)
        .encode(
            theta=alt.Theta(f"{value_field}:Q"),
            color=alt.Color(f"{category_field}:N", scale=alt.Scale(range=PALETTE), title=None),
            tooltip=[
                alt.Tooltip(f"{category_field}:N", title=category_field),
                alt.Tooltip(f"{value_field}:Q", title="Bolsas", format=","),
            ],
        )
        .properties(height=300)
    )

    return polish_chart(chart)


df = load_data()

if df.empty:
    st.warning("Nenhum dado encontrado para montar os dashboards.")
    st.stop()

st.title("ProUni Analytics 2020")

with st.sidebar:
    st.header("Filtros")

    regioes = sorted(df["REGIAO_BENEFICIARIO"].dropna().unique())
    regioes_selecionadas = st.multiselect("Regiao", regioes, default=regioes)

    estados_base = df[df["REGIAO_BENEFICIARIO"].isin(regioes_selecionadas)]
    estados = sorted(estados_base["UF_BENEFICIARIO"].dropna().unique())
    estados_selecionados = st.multiselect("Estado", estados, default=estados)

    tipos = sorted(df["TIPO_BOLSA"].dropna().unique())
    tipos_selecionados = st.multiselect("Tipo de bolsa", tipos, default=tipos)

    modalidades = sorted(df["MODALIDADE_ENSINO_BOLSA"].dropna().unique())
    modalidades_selecionadas = st.multiselect("Modalidade", modalidades, default=modalidades)

filtered = df[
    df["REGIAO_BENEFICIARIO"].isin(regioes_selecionadas)
    & df["UF_BENEFICIARIO"].isin(estados_selecionados)
    & df["TIPO_BOLSA"].isin(tipos_selecionados)
    & df["MODALIDADE_ENSINO_BOLSA"].isin(modalidades_selecionadas)
].copy()

if filtered.empty:
    st.warning("Nenhum registro encontrado para os filtros selecionados.")
    st.stop()

total_bolsas = len(filtered)
total_cursos = filtered["NOME_CURSO_BOLSA"].nunique()
total_ies = filtered["NOME_IES_BOLSA"].nunique()
total_municipios = filtered["MUNICIPIO_BENEFICIARIO"].nunique()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Bolsas", f"{total_bolsas:,}".replace(",", "."))
kpi2.metric("Cursos", f"{total_cursos:,}".replace(",", "."))
kpi3.metric("Instituicoes", f"{total_ies:,}".replace(",", "."))
kpi4.metric("Municipios", f"{total_municipios:,}".replace(",", "."))

st.divider()

left, right = st.columns((1.35, 1))

with left:
    st.markdown('<div class="section-title">Bolsas por estado</div>', unsafe_allow_html=True)
    st.markdown('<div class="caption">Ranking de UFs conforme os filtros atuais.</div>', unsafe_allow_html=True)
    uf_data = count_by(filtered, "UF_BENEFICIARIO", "UF")
    st.altair_chart(
        vertical_bar(uf_data, "UF", "Bolsas", "UF", height=330),
        use_container_width=True,
    )

with right:
    st.markdown('<div class="section-title">Tipo de bolsa</div>', unsafe_allow_html=True)
    st.markdown('<div class="caption">Participacao entre bolsas integrais e parciais.</div>', unsafe_allow_html=True)
    tipo_data = count_by(filtered, "TIPO_BOLSA", "Tipo")
    st.altair_chart(
        donut_chart(tipo_data, "Tipo", "Bolsas"),
        use_container_width=True,
    )

left, right = st.columns((1, 1))

with left:
    st.markdown('<div class="section-title">Distribuicao por sexo</div>', unsafe_allow_html=True)
    sexo_data = count_by(filtered, "SEXO_BENEFICIARIO", "Sexo")
    st.altair_chart(
        horizontal_bar(sexo_data, "Bolsas", "Sexo", "Sexo", height=220),
        use_container_width=True,
    )

with right:
    st.markdown('<div class="section-title">Modalidade de ensino</div>', unsafe_allow_html=True)
    modalidade_data = count_by(filtered, "MODALIDADE_ENSINO_BOLSA", "Modalidade")
    st.altair_chart(
        horizontal_bar(modalidade_data, "Bolsas", "Modalidade", "Modalidade", height=220),
        use_container_width=True,
    )

left, right = st.columns((1.15, 1))

with left:
    st.markdown('<div class="section-title">Top cursos</div>', unsafe_allow_html=True)
    top_cursos = count_by(filtered, "NOME_CURSO_BOLSA", "Curso", limit=12)
    st.altair_chart(
        horizontal_bar(top_cursos, "Bolsas", "Curso", height=420),
        use_container_width=True,
    )

with right:
    st.markdown('<div class="section-title">Perfil por raca/cor</div>', unsafe_allow_html=True)
    raca_data = count_by(filtered, "RACA_BENEFICIARIO", "Raca/cor")
    st.altair_chart(
        horizontal_bar(raca_data, "Bolsas", "Raca/cor", "Raca/cor", height=420),
        use_container_width=True,
    )

st.markdown('<div class="section-title">Tabela de dados filtrados</div>', unsafe_allow_html=True)
preview_columns = [
    "UF_BENEFICIARIO",
    "MUNICIPIO_BENEFICIARIO",
    "NOME_CURSO_BOLSA",
    "TIPO_BOLSA",
    "MODALIDADE_ENSINO_BOLSA",
    "SEXO_BENEFICIARIO",
    "RACA_BENEFICIARIO",
]
st.dataframe(
    filtered[preview_columns].head(500),
    use_container_width=True,
    hide_index=True,
)
