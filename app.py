
import streamlit as st
import pandas as pd

# Configuración de página (sin 'title' directo, usando 'page_title')
st.set_page_config(page_title='Explorador de Datos', layout='wide')

st.title('📊 Bloque 1 · Carga y vista previa')

file = st.file_uploader('Elige un archivo CSV o Excel', type=['csv','xlsx'])
if file:
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    st.success(f'Archivo cargado: {file.name} ({len(df)} filas, {len(df.columns)} columnas)')
    st.dataframe(df.head(50))
