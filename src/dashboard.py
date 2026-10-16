import os
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(
    page_title="Dashboard de Temperaturas IoT",
    page_icon="🌡️",
    layout="wide",
)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "iotdb")
DB_USER = os.getenv("DB_USER", "iotuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "iotpass")

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

@st.cache_data(ttl=60)
def load_view(view_name: str) -> pd.DataFrame:
    allowed = {
        "avg_temp_por_local",
        "leituras_por_hora",
        "temp_max_min_por_dia",
    }
    if view_name not in allowed:
        raise ValueError("View não permitida.")
    return pd.read_sql(f"SELECT * FROM {view_name}", engine)


st.title("🌡️ Dashboard de Temperaturas IoT")
st.caption("Pipeline: CSV → Python/Pandas → PostgreSQL/Docker → SQL Views → Streamlit")

try:
    avg = load_view("avg_temp_por_local")
    hourly = load_view("leituras_por_hora")
    daily = load_view("temp_max_min_por_dia")

    c1, c2, c3 = st.columns(3)
    c1.metric("Ambientes monitorados", int(avg["location"].nunique()))
    c2.metric("Leituras", f"{int(avg['total_leituras'].sum()):,}".replace(",", "."))
    c3.metric("Temperatura média", f"{avg['avg_temp'].mean():.1f} °C")

    st.divider()

    st.header("Média de temperatura por ambiente")
    fig1 = px.bar(
        avg,
        x="location",
        y="avg_temp",
        text="avg_temp",
        labels={"location": "Local", "avg_temp": "Temperatura média (°C)"},
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.header("Leituras por hora do dia")
    fig2 = px.line(
        hourly,
        x="hora",
        y="contagem",
        markers=True,
        labels={"hora": "Hora", "contagem": "Quantidade de leituras"},
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.header("Temperaturas máximas e mínimas por dia")
    fig3 = px.line(
        daily,
        x="data",
        y=["temp_max", "temp_min"],
        labels={"value": "Temperatura (°C)", "data": "Data"},
    )
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("Ver dados das views"):
        st.subheader("Média por ambiente")
        st.dataframe(avg, use_container_width=True)
        st.subheader("Leituras por hora")
        st.dataframe(hourly, use_container_width=True)
        st.subheader("Máxima e mínima por dia")
        st.dataframe(daily, use_container_width=True)

except Exception as exc:
    st.error(
        "Não foi possível carregar o PostgreSQL. "
        "Suba o Docker e execute primeiro `python src/pipeline.py`."
    )
    st.exception(exc)
