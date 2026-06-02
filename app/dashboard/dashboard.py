import re
import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

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

SIGLA_STOP_WORDS = {
    "A",
    "AS",
    "DA",
    "DAS",
    "DE",
    "DO",
    "DOS",
    "E",
    "EM",
    "PARA",
}

UF_COORDS = {
    "AC": (-8.77, -70.55),
    "AL": (-9.71, -35.73),
    "AM": (-3.47, -65.10),
    "AP": (1.41, -51.77),
    "BA": (-12.96, -38.51),
    "CE": (-5.20, -39.53),
    "DF": (-15.83, -47.86),
    "ES": (-19.19, -40.34),
    "GO": (-16.64, -49.31),
    "MA": (-5.42, -45.44),
    "MG": (-18.10, -44.38),
    "MS": (-20.51, -54.54),
    "MT": (-12.64, -55.42),
    "PA": (-5.53, -52.29),
    "PB": (-7.06, -35.55),
    "PE": (-8.28, -35.07),
    "PI": (-8.28, -43.68),
    "PR": (-24.89, -51.55),
    "RJ": (-22.84, -43.15),
    "RN": (-5.81, -36.59),
    "RO": (-11.22, -62.80),
    "RR": (1.89, -61.22),
    "RS": (-30.01, -51.22),
    "SC": (-27.33, -49.44),
    "SE": (-10.90, -37.07),
    "SP": (-22.19, -48.79),
    "TO": (-10.25, -48.25),
}


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
        "MUNICIPIO",
    ]

    for column in text_columns:
        if column in data.columns:
            data[column] = data[column].fillna("Nao informado").astype(str).str.strip()

    data["DATA_NASCIMENTO_DT"] = pd.to_datetime(
        data["DATA_NASCIMENTO"],
        dayfirst=True,
        errors="coerce",
    )
    data["IDADE"] = 2020 - data["DATA_NASCIMENTO_DT"].dt.year
    data.loc[(data["IDADE"] < 14) | (data["IDADE"] > 90), "IDADE"] = pd.NA
    data["SIGLA_IES_BOLSA"] = data["NOME_IES_BOLSA"].apply(make_university_acronym)

    return data


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
        suffix_words = re.findall(r"[A-Z0-9]+", suffix)
        if suffix_words and len(suffix_words[0]) >= 3:
            return suffix_words[0][:14]

    words = [
        word
        for word in re.findall(r"[A-Z0-9]+", normalized)
        if word not in SIGLA_STOP_WORDS
    ]

    if not words:
        return "NI"

    return "".join(word[0] for word in words[:6])[:10]


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


def fmt_number(value):
    return f"{value:,.0f}".replace(",", ".")


def grouped_count(data, columns):
    return data.groupby(columns).size().reset_index(name="Bolsas")


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


def stacked_bar(data, x_field, color_field, height=320):
    chart = (
        alt.Chart(data)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X(f"{x_field}:N", title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Bolsas:Q", title=None, stack="zero"),
            color=alt.Color(f"{color_field}:N", scale=alt.Scale(range=PALETTE), title=None),
            tooltip=[
                alt.Tooltip(f"{x_field}:N", title=x_field),
                alt.Tooltip(f"{color_field}:N", title=color_field),
                alt.Tooltip("Bolsas:Q", title="Bolsas", format=","),
            ],
        )
        .properties(height=height)
    )

    return polish_chart(chart)


def horizontal_stacked_bar(data, y_field, color_field, height=340):
    chart = (
        alt.Chart(data)
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            x=alt.X("Bolsas:Q", title=None, stack="zero"),
            y=alt.Y(f"{y_field}:N", title=None, sort="-x"),
            color=alt.Color(f"{color_field}:N", scale=alt.Scale(range=PALETTE), title=None),
            tooltip=[
                alt.Tooltip(f"{y_field}:N", title=y_field),
                alt.Tooltip(f"{color_field}:N", title=color_field),
                alt.Tooltip("Bolsas:Q", title="Bolsas", format=","),
            ],
        )
        .properties(height=height)
    )

    return polish_chart(chart)


def heatmap(data, x_field, y_field, height=330):
    chart = (
        alt.Chart(data)
        .mark_rect(cornerRadius=3)
        .encode(
            x=alt.X(f"{x_field}:N", title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y(f"{y_field}:N", title=None, sort="-x"),
            color=alt.Color(
                "Bolsas:Q",
                scale=alt.Scale(scheme="tealblues"),
                title="Bolsas",
            ),
            tooltip=[
                alt.Tooltip(f"{x_field}:N", title=x_field),
                alt.Tooltip(f"{y_field}:N", title=y_field),
                alt.Tooltip("Bolsas:Q", title="Bolsas", format=","),
            ],
        )
        .properties(height=height)
    )

    return polish_chart(chart)


def shorten_label(value, max_chars=20):
    text = str(value)
    if len(text) <= max_chars:
        return text

    return text[: max_chars - 3].rstrip() + "..."


def university_course_graph(data, institution, height=360):
    graph_base = data[data["SIGLA_IES_BOLSA"] == institution]
    edges = grouped_count(graph_base, ["SIGLA_IES_BOLSA", "NOME_CURSO_BOLSA"])
    edges = edges.sort_values("Bolsas", ascending=False).head(8).reset_index(drop=True)

    if edges.empty:
        return None

    total_institution = edges["Bolsas"].sum()
    institution_nodes = pd.DataFrame(
        [
            {
                "Id": institution,
                "Label": institution,
                "Tipo": "Instituicao",
                "Bolsas": total_institution,
                "x": 0.18,
                "y": 0.50,
            }
        ]
    )
    course_nodes = pd.DataFrame(
        [
            {
                "Id": row["NOME_CURSO_BOLSA"],
                "Label": shorten_label(row["NOME_CURSO_BOLSA"], 24),
                "Tipo": "Curso",
                "Bolsas": row["Bolsas"],
                "x": 0.74,
                "y": (index + 1) / (len(edges) + 1),
            }
            for index, row in edges.iterrows()
        ]
    )
    nodes = pd.concat([institution_nodes, course_nodes], ignore_index=True)

    edge_lines = pd.concat(
        [
            pd.DataFrame(
                {
                    "Ligacao": edges.index,
                    "x": 0.18,
                    "y": 0.50,
                    "SIGLA_IES_BOLSA": edges["SIGLA_IES_BOLSA"],
                    "NOME_CURSO_BOLSA": edges["NOME_CURSO_BOLSA"],
                    "Bolsas": edges["Bolsas"],
                }
            ),
            pd.DataFrame(
                {
                    "Ligacao": edges.index,
                    "x": 0.74,
                    "y": course_nodes["y"],
                    "SIGLA_IES_BOLSA": edges["SIGLA_IES_BOLSA"],
                    "NOME_CURSO_BOLSA": edges["NOME_CURSO_BOLSA"],
                    "Bolsas": edges["Bolsas"],
                }
            ),
        ],
        ignore_index=True,
    )

    edges_chart = (
        alt.Chart(edge_lines)
        .mark_line(color="#8fa3b8", opacity=0.58)
        .encode(
            x=alt.X("x:Q", axis=None, scale=alt.Scale(domain=[0, 1])),
            y=alt.Y("y:Q", axis=None, scale=alt.Scale(domain=[0, 1])),
            detail="Ligacao:N",
            strokeWidth=alt.StrokeWidth("Bolsas:Q", scale=alt.Scale(range=[1, 7]), legend=None),
            tooltip=[
                alt.Tooltip("SIGLA_IES_BOLSA:N", title="Instituicao"),
                alt.Tooltip("NOME_CURSO_BOLSA:N", title="Curso"),
                alt.Tooltip("Bolsas:Q", title="Bolsas", format=","),
            ],
        )
    )
    nodes_chart = (
        alt.Chart(nodes)
        .mark_circle(stroke="#ffffff", strokeWidth=2, opacity=0.97)
        .encode(
            x=alt.X("x:Q", axis=None, scale=alt.Scale(domain=[0, 1])),
            y=alt.Y("y:Q", axis=None, scale=alt.Scale(domain=[0, 1])),
            size=alt.Size("Bolsas:Q", scale=alt.Scale(range=[240, 1400]), legend=None),
            color=alt.Color("Tipo:N", scale=alt.Scale(range=[PALETTE[0], PALETTE[1]]), title=None),
            tooltip=[
                alt.Tooltip("Id:N", title="No"),
                alt.Tooltip("Tipo:N", title="Tipo"),
                alt.Tooltip("Bolsas:Q", title="Bolsas", format=","),
            ],
        )
    )
    labels = (
        alt.Chart(nodes)
        .mark_text(fontSize=12, color="#172033", fontWeight="bold", dx=14, align="left")
        .encode(
            x=alt.X("x:Q", axis=None, scale=alt.Scale(domain=[0, 1])),
            y=alt.Y("y:Q", axis=None, scale=alt.Scale(domain=[0, 1])),
            text="Label:N",
        )
    )
    edge_labels = (
        alt.Chart(edge_lines[edge_lines["x"] == 0.74])
        .mark_text(fontSize=11, color="#61708a", dx=14, dy=15, align="left")
        .encode(
            x=alt.X("x:Q", axis=None, scale=alt.Scale(domain=[0, 1])),
            y=alt.Y("y:Q", axis=None, scale=alt.Scale(domain=[0, 1])),
            text=alt.Text("Bolsas:Q", format=","),
        )
    )

    return polish_chart((edges_chart + nodes_chart + labels + edge_labels).properties(height=height))


def age_by_scholarship_type_chart(data, height=330):
    ages = data[["IDADE", "TIPO_BOLSA"]].dropna().copy()

    if ages.empty:
        return None

    bins = list(range(15, 96, 5))
    labels = [f"{start}-{start + 5}" for start in bins[:-1]]
    ages["Faixa idade"] = pd.cut(
        ages["IDADE"],
        bins=bins,
        labels=labels,
        right=False,
    )
    ages = ages.dropna(subset=["Faixa idade"])

    if ages.empty:
        return None

    chart = (
        alt.Chart(ages)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X(
                "Faixa idade:N",
                title="Faixa de idade",
                sort=labels,
                axis=alt.Axis(grid=False, labelAngle=-45, labelOverlap=False),
            ),
            y=alt.Y("count():Q", title="Bolsas", axis=alt.Axis(grid=True, tickCount=5)),
            color=alt.Color("TIPO_BOLSA:N", scale=alt.Scale(range=PALETTE), title="Tipo de bolsa"),
            xOffset=alt.XOffset("TIPO_BOLSA:N"),
            tooltip=[
                alt.Tooltip("Faixa idade:N", title="Faixa de idade"),
                alt.Tooltip("TIPO_BOLSA:N", title="Tipo de bolsa"),
                alt.Tooltip("count():Q", title="Bolsas", format=","),
            ],
        )
        .properties(height=height)
    )

    return polish_chart(chart)


def uf_bubble_map(data, height=410):
    uf_data = count_by(data, "UF_BENEFICIARIO", "UF")
    coords = pd.DataFrame(
        [
            {"UF": uf, "Latitude": lat, "Longitude": lon}
            for uf, (lat, lon) in UF_COORDS.items()
        ]
    )
    map_data = uf_data.merge(coords, on="UF", how="inner")

    base = (
        alt.Chart(map_data)
        .mark_circle(opacity=0.78, stroke="#ffffff", strokeWidth=1.5)
        .encode(
            x=alt.X("Longitude:Q", title=None, scale=alt.Scale(domain=[-75, -32])),
            y=alt.Y("Latitude:Q", title=None, scale=alt.Scale(domain=[-34, 6])),
            size=alt.Size("Bolsas:Q", scale=alt.Scale(range=[90, 2600]), legend=None),
            color=alt.Color("Bolsas:Q", scale=alt.Scale(scheme="tealblues"), legend=None),
            tooltip=[
                alt.Tooltip("UF:N", title="UF"),
                alt.Tooltip("Bolsas:Q", title="Bolsas", format=","),
            ],
        )
        .properties(height=height)
    )

    labels = (
        alt.Chart(map_data)
        .mark_text(fontSize=11, fontWeight="bold", color="#172033")
        .encode(
            x="Longitude:Q",
            y="Latitude:Q",
            text="UF:N",
        )
    )

    return polish_chart(base + labels)


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
total_ies = filtered["SIGLA_IES_BOLSA"].nunique()
total_municipios = filtered["MUNICIPIO_BENEFICIARIO"].nunique()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Bolsas", fmt_number(total_bolsas))
kpi2.metric("Cursos", fmt_number(total_cursos))
kpi3.metric("Instituicoes", fmt_number(total_ies))
kpi4.metric("Municipios", fmt_number(total_municipios))

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
    st.markdown('<div class="section-title">Mapa de concentracao por UF</div>', unsafe_allow_html=True)
    st.markdown('<div class="caption">Bolhas maiores indicam maior volume de bolsas por estado.</div>', unsafe_allow_html=True)
    st.altair_chart(
        uf_bubble_map(filtered, height=390),
        use_container_width=True,
    )

with right:
    st.markdown('<div class="section-title">Tipo de bolsa por regiao</div>', unsafe_allow_html=True)
    st.markdown('<div class="caption">Comparacao regional entre bolsas integrais e parciais.</div>', unsafe_allow_html=True)
    regiao_tipo = grouped_count(filtered, ["REGIAO_BENEFICIARIO", "TIPO_BOLSA"])
    st.altair_chart(
        stacked_bar(regiao_tipo, "REGIAO_BENEFICIARIO", "TIPO_BOLSA", height=390),
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

left, right = st.columns((1, 1))

with left:
    st.markdown('<div class="section-title">Grafo por universidade</div>', unsafe_allow_html=True)
    st.markdown('<div class="caption">Escolha uma sigla para ver somente os cursos ligados a essa universidade. O numero ao lado do curso indica a quantidade de bolsas.</div>', unsafe_allow_html=True)
    top_graph_institutions = count_by(filtered, "SIGLA_IES_BOLSA", "Instituicao", limit=4)["Instituicao"].tolist()
    if not top_graph_institutions:
        st.info("Nao ha dados suficientes para montar o grafo no recorte selecionado.")
    else:
        graph_tabs = st.tabs(top_graph_institutions)
        for tab, institution in zip(graph_tabs, top_graph_institutions):
            with tab:
                graph_chart = university_course_graph(filtered, institution, height=330)
                if graph_chart is None:
                    st.info("Nao ha cursos suficientes para montar o grafo desta universidade.")
                else:
                    st.altair_chart(graph_chart, use_container_width=True)

with right:
    st.markdown('<div class="section-title">Idades por tipo de bolsa</div>', unsafe_allow_html=True)
    st.markdown('<div class="caption">Comparacao das faixas etarias entre bolsas integrais e parciais.</div>', unsafe_allow_html=True)
    age_chart = age_by_scholarship_type_chart(filtered, height=330)
    if age_chart is None:
        st.info("Nao ha dados de idade suficientes para montar o grafico.")
    else:
        st.altair_chart(age_chart, use_container_width=True)

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

left, right = st.columns((1.2, 1))

with left:
    st.markdown('<div class="section-title">Instituicoes com mais bolsas</div>', unsafe_allow_html=True)
    st.markdown('<div class="caption">Ranking das siglas das instituicoes de ensino com maior volume no recorte atual.</div>', unsafe_allow_html=True)
    top_ies = count_by(filtered, "SIGLA_IES_BOLSA", "Instituicao", limit=12)
    st.altair_chart(
        horizontal_bar(top_ies, "Bolsas", "Instituicao", height=420),
        use_container_width=True,
    )

with right:
    st.markdown('<div class="section-title">Turno do curso</div>', unsafe_allow_html=True)
    turno_data = count_by(filtered, "NOME_TURNO_CURSO_BOLSA", "Turno")
    st.altair_chart(
        horizontal_bar(turno_data, "Bolsas", "Turno", "Turno", height=420),
        use_container_width=True,
    )

st.divider()
st.header("Analise focada em Campinas")

campinas_beneficiarios = filtered[
    filtered["MUNICIPIO_BENEFICIARIO"].str.upper() == "CAMPINAS"
].copy()
campinas_campus = filtered[
    filtered["MUNICIPIO"].str.upper() == "CAMPINAS"
].copy()

camp1, camp2, camp3, camp4 = st.columns(4)
camp1.metric("Beneficiarios moradores", fmt_number(len(campinas_beneficiarios)))
camp2.metric("Cursos dos moradores", fmt_number(campinas_beneficiarios["NOME_CURSO_BOLSA"].nunique()))
camp3.metric("Bolsas em campus Campinas", fmt_number(len(campinas_campus)))
camp4.metric("Instituicoes em Campinas", fmt_number(campinas_campus["SIGLA_IES_BOLSA"].nunique()))

if campinas_beneficiarios.empty and campinas_campus.empty:
    st.info("Nao ha registros de Campinas no recorte selecionado.")
else:
    left, right = st.columns((1, 1))

    with left:
        st.markdown('<div class="section-title">Campinas: cursos dos beneficiarios</div>', unsafe_allow_html=True)
        if campinas_beneficiarios.empty:
            st.info("Sem beneficiarios moradores de Campinas nos filtros atuais.")
        else:
            camp_cursos = count_by(campinas_beneficiarios, "NOME_CURSO_BOLSA", "Curso", limit=10)
            st.altair_chart(
                horizontal_bar(camp_cursos, "Bolsas", "Curso", height=340),
                use_container_width=True,
            )

    with right:
        st.markdown('<div class="section-title">Campinas: perfil por modalidade</div>', unsafe_allow_html=True)
        if campinas_beneficiarios.empty:
            st.info("Sem beneficiarios moradores de Campinas nos filtros atuais.")
        else:
            camp_modalidade = count_by(campinas_beneficiarios, "MODALIDADE_ENSINO_BOLSA", "Modalidade")
            st.altair_chart(
                donut_chart(camp_modalidade, "Modalidade", "Bolsas"),
                use_container_width=True,
            )

    left, right = st.columns((1.1, 1))

    with left:
        st.markdown('<div class="section-title">Campinas: instituicoes/campus</div>', unsafe_allow_html=True)
        if campinas_campus.empty:
            st.info("Sem campus localizados em Campinas nos filtros atuais.")
        else:
            camp_ies = count_by(campinas_campus, "SIGLA_IES_BOLSA", "Instituicao", limit=10)
            st.altair_chart(
                horizontal_bar(camp_ies, "Bolsas", "Instituicao", height=340),
                use_container_width=True,
            )

    with right:
        st.markdown('<div class="section-title">Campinas: tipo de bolsa</div>', unsafe_allow_html=True)
        camp_base = campinas_beneficiarios if not campinas_beneficiarios.empty else campinas_campus
        camp_tipo = count_by(camp_base, "TIPO_BOLSA", "Tipo")
        st.altair_chart(
            horizontal_bar(camp_tipo, "Bolsas", "Tipo", "Tipo", height=260),
            use_container_width=True,
        )

st.markdown('<div class="section-title">Tabela de dados filtrados</div>', unsafe_allow_html=True)
preview_columns = [
    "UF_BENEFICIARIO",
    "MUNICIPIO_BENEFICIARIO",
    "SIGLA_IES_BOLSA",
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
