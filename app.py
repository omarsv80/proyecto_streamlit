# -----------------------------
# Dashboard de Ventas (Streamlit)
# -----------------------------
import io
import pandas as pd
import streamlit as st
import plotly.express as px

# ============ CONFIG ============ #
RAW_CSV_URL = "https://raw.githubusercontent.com/omarsv80/proyecto_streamlit/main/SampleSuperstore.csv"

st.set_page_config(
    page_title="Dashboard de Ventas",
    layout="wide",
    page_icon="📊",
)

st.title("📊 Dashboard Interactivo de Análisis de Ventas")
st.caption("Datos cargados automáticamente desde GitHub ✅")

# ============ CARGA (cache) ============ #
@st.cache_data(ttl=3600, show_spinner=True)
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url, encoding="utf-8")
    # Normalizamos nombres por si difieren en mayúsculas/minúsculas
    df.columns = [c.strip() for c in df.columns]
    # Parseo opcional de fechas si existen
    for col in ["Order Date", "Order Date ", "Fecha", "OrderDate"]:
        if col in df.columns:
            df["__order_date__"] = pd.to_datetime(df[col], errors="coerce")
            break
    # Campos esperados (según Superstore)
    for need in ["Sales", "Profit", "Discount"]:
        if need not in df.columns:
            df[need] = 0.0
    return df

df = load_data(RAW_CSV_URL)

# ============ FILTROS (sidebar) ============ #
st.sidebar.header("🔎 Filtros")
def pick_options(series):
    vals = sorted([v for v in series.dropna().unique().tolist()])
    return vals

# Filtros seguros (solo si existen esas columnas)
region = category = segment = None
if "Region" in df.columns:
    region = st.sidebar.multiselect("Región", pick_options(df["Region"]))
if "Category" in df.columns:
    category = st.sidebar.multiselect("Categoría", pick_options(df["Category"]))
if "Segment" in df.columns:
    segment = st.sidebar.multiselect("Segmento", pick_options(df["Segment"]))

df_f = df.copy()
if region:
    df_f = df_f[df_f["Region"].isin(region)]
if category:
    df_f = df_f[df_f["Category"].isin(category)]
if segment:
    df_f = df_f[df_f["Segment"].isin(segment)]

# ============ KPIs ============ #
total_sales = float(df_f["Sales"].sum()) if "Sales" in df_f.columns else 0.0
total_profit = float(df_f["Profit"].sum()) if "Profit" in df_f.columns else 0.0
avg_disc = float(df_f["Discount"].mean()) if "Discount" in df_f.columns else 0.0

k1, k2, k3 = st.columns(3)
k1.metric("Ventas (sum)", f"${total_sales:,.0f}")
k2.metric("Ganancia (sum)", f"${total_profit:,.0f}")
k3.metric("Descuento prom.", f"{avg_disc:.2%}")

st.divider()

# ============ GRÁFICAS ============ #
g1, g2 = st.columns(2)

# 1) Ventas por Categoría (si existe)
with g1:
    if "Category" in df_f.columns and "Sales" in df_f.columns:
        cat_sales = df_f.groupby("Category", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
        fig_cat = px.bar(cat_sales, x="Category", y="Sales", title="Ventas por Categoría", text_auto=".2s")
        fig_cat.update_layout(height=420, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("No se encontró la columna 'Category' o 'Sales' para graficar.")

# 2) Ventas por Mes (si hay fecha)
with g2:
    if "__order_date__" in df_f.columns and "Sales" in df_f.columns:
        tmp = df_f.dropna(subset=["__order_date__"]).copy()
        if not tmp.empty:
            tmp["Mes"] = tmp["__order_date__"].dt.to_period("M").dt.to_timestamp()
            monthly = tmp.groupby("Mes", as_index=False)["Sales"].sum()
            fig_m = px.line(monthly, x="Mes", y="Sales", markers=True, title="Ventas por Mes")
            fig_m.update_layout(height=420, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig_m, use_container_width=True)
        else:
            st.info("No hay fechas válidas para graficar ventas por mes.")
    else:
        st.info("No se encontró fecha de pedido para graficar ventas por mes.")

st.divider()

# ============ TABLAS DE APOYO ============ #
st.subheader("📄 Vista rápida de datos (filtrados)")
st.dataframe(df_f.head(50), use_container_width=True, height=300)

# Tabla dinámica simple (si tiene columnas típicas)
st.subheader("📌 Resumen por Región x Categoría (Ventas y Profit)")
if {"Region", "Category", "Sales", "Profit"}.issubset(df_f.columns):
    piv = (
        df_f.pivot_table(index="Region", columns="Category", values="Sales", aggfunc="sum")
        .fillna(0)
        .round(2)
    )
    st.dataframe(piv, use_container_width=True)
else:
    st.info("Para la tabla dinámica se necesitan: Region, Category, Sales, Profit.")

# ============ EXPORTAR ============ #
st.subheader("⬇️ Exportar datos filtrados")

colA, colB = st.columns(2)

with colA:
    csv_bytes = df_f.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Descargar CSV (filtrado)",
        data=csv_bytes,
        file_name="datos_filtrados.csv",
        mime="text/csv",
        use_container_width=True,
    )

with colB:
    # Exportar a Excel en memoria
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
        df_f.to_excel(writer, index=False, sheet_name="Filtrado")
    st.download_button(
        "Descargar Excel (filtrado)",
        data=bio.getvalue(),
        file_name="datos_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

st.caption("© Equipo • Streamlit + Plotly + Pandas")
