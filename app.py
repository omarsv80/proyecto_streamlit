import streamlit as st
import pandas as pd

# URL pública del CSV en GitHub
RAW_URL = "https://raw.githubusercontent.com/omarsv80/proyecto_streamlit/main/SampleSuperstore.csv"

st.set_page_config(page_title="Dashboard de Ventas", layout="wide")

st.title("📊 Dashboard Interactivo de Análisis de Ventas")

# Cargar automáticamente desde GitHub
try:
    df = pd.read_csv(RAW_URL)
    st.success("Datos cargados automáticamente desde GitHub ✅")
except Exception as e:
    st.error("Error al cargar el CSV automáticamente.")
    st.text(str(e))

# Mostrar los primeros datos
st.dataframe(df.head())
