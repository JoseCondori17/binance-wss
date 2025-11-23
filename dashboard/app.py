import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any

# Configuración de la página
st.set_page_config(
    page_title="Binance Trading Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de la API
# Si estamos en Docker, usar el nombre del servicio, sino localhost
import os
API_HOST = os.getenv("API_HOST", "localhost")
API_BASE_URL = f"http://{API_HOST}:8000/api/v1"


# Funciones auxiliares para obtener datos
def get_kpi_data(endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Obtiene datos de un endpoint específico de KPIs"""
    try:
        url = f"{API_BASE_URL}/kpis/{endpoint}"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error al obtener datos de {endpoint}: {str(e)}")
        return {}


def get_resumen_completo(params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Obtiene todos los KPIs en una sola llamada"""
    return get_kpi_data("resumen", params)


# Estilos CSS personalizados
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .kpi-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .section-header {
        font-size: 28px;
        font-weight: bold;
        color: #1f77b4;
        margin-top: 30px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)


# Sidebar - Filtros
st.sidebar.title("Filtros de Análisis")

# Filtro de símbolo
symbol_filter = st.sidebar.selectbox(
    "Símbolo",
    options=["Todos", "BTCUSDT", "ETHUSDT", "BNBUSDT"],
    index=0
)

# Filtro de rango de fechas
st.sidebar.subheader("Rango de Fechas")
use_date_filter = st.sidebar.checkbox("Aplicar filtro de fechas", value=False)

fecha_inicio = None
fecha_fin = None

if use_date_filter:
    fecha_inicio = st.sidebar.date_input(
        "Fecha inicio",
        value=datetime.now() - timedelta(days=7)
    )
    fecha_fin = st.sidebar.date_input(
        "Fecha fin",
        value=datetime.now()
    )
    
    # Convertir a datetime
    fecha_inicio = datetime.combine(fecha_inicio, datetime.min.time())
    fecha_fin = datetime.combine(fecha_fin, datetime.max.time())

# Preparar parámetros para la API
api_params = {}
if symbol_filter != "Todos":
    api_params["symbol"] = symbol_filter
if use_date_filter and fecha_inicio:
    api_params["fecha_inicio"] = fecha_inicio.isoformat()
if use_date_filter and fecha_fin:
    api_params["fecha_fin"] = fecha_fin.isoformat()

# Botón de actualización
refresh = st.sidebar.button("Actualizar Datos", type="primary")

# Header principal
st.title("📊 Binance Trading Analytics Dashboard")
st.markdown("---")

# Obtener datos
with st.spinner("Cargando datos..."):
    data = get_resumen_completo(api_params)

if not data:
    st.warning("No se pudieron cargar los datos. Verifica que la API esté corriendo.")
    st.stop()

# ============================================================================
# SECCIÓN 1: MÉTRICAS GLOBALES
# ============================================================================
st.markdown('<div class="section-header">📈 Resumen Global del Mercado</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

# Volatilidad Global
volatilidad_global = data.get("volatilidad", {}).get("datos_globales", {})
with col1:
    st.metric(
        label="Volatilidad Promedio",
        value=f"{volatilidad_global.get('valor_global', 0):.2f}%",
        delta=None
    )

# Volumen Global
volumen_global = data.get("volumen", {}).get("datos_globales", {})
with col2:
    st.metric(
        label="Volumen Total (USDT)",
        value=f"${volumen_global.get('valor_global_usdt', 0):,.0f}",
        delta=None
    )

with col3:
    st.metric(
        label="Volumen Total (BTC)",
        value=f"{volumen_global.get('valor_global_btc', 0):.4f}",
        delta=None
    )

# Presión Compradora Global
presion_global = data.get("presion", {}).get("datos_globales", {})
with col4:
    sentimiento = presion_global.get("sentimiento_global", "NEUTRAL")
    color_sentimiento = "🟢" if sentimiento == "ALCISTA" else "🔴" if sentimiento == "BAJISTA" else "🟡"
    st.metric(
        label="Sentimiento Global",
        value=f"{color_sentimiento} {sentimiento}",
        delta=f"{presion_global.get('valor_global_pct', 0):.1f}% Compradores"
    )

st.markdown("---")

# ============================================================================
# SECCIÓN 2: VOLATILIDAD DEL MERCADO
# ============================================================================
st.markdown('<div class="section-header">🎢 Análisis de Volatilidad</div>', unsafe_allow_html=True)

volatilidad_data = data.get("volatilidad", {}).get("datos_por_simbolo", [])

if volatilidad_data:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Volatilidad por Símbolo")
        df_vol = pd.DataFrame(volatilidad_data)
        
        fig_vol = px.bar(
            df_vol,
            x="symbol",
            y="volatilidad_promedio",
            title="Volatilidad Promedio por Par",
            labels={"volatilidad_promedio": "Volatilidad (%)", "symbol": "Símbolo"},
            color="volatilidad_promedio",
            color_continuous_scale="Reds"
        )
        st.plotly_chart(fig_vol, use_container_width=True)
    
    with col2:
        st.subheader("Precios Extremos")
        fig_precios = go.Figure()
        
        fig_precios.add_trace(go.Bar(
            name="Precio Máximo",
            x=df_vol["symbol"],
            y=df_vol["precio_max"],
            marker_color="green"
        ))
        
        fig_precios.add_trace(go.Bar(
            name="Precio Mínimo",
            x=df_vol["symbol"],
            y=df_vol["precio_min"],
            marker_color="red"
        ))
        
        fig_precios.update_layout(
            title="Rango de Precios por Símbolo",
            xaxis_title="Símbolo",
            yaxis_title="Precio (USDT)",
            barmode="group"
        )
        st.plotly_chart(fig_precios, use_container_width=True)
    
    # Tabla detallada
    st.subheader("Datos Detallados de Volatilidad")
    st.dataframe(
        df_vol,
        use_container_width=True,
        hide_index=True,
        column_config={
            "symbol": "Símbolo",
            "volatilidad_promedio": st.column_config.NumberColumn("Vol. Promedio (%)", format="%.4f"),
            "volatilidad_maxima": st.column_config.NumberColumn("Vol. Máxima (%)", format="%.4f"),
            "precio_max": st.column_config.NumberColumn("Precio Max", format="$%.2f"),
            "precio_min": st.column_config.NumberColumn("Precio Min", format="$%.2f"),
            "num_registros": "Registros"
        }
    )

st.markdown("---")

# ============================================================================
# SECCIÓN 3: VOLUMEN DE TRADING
# ============================================================================
st.markdown('<div class="section-header">💰 Análisis de Volumen de Trading</div>', unsafe_allow_html=True)

volumen_data = data.get("volumen", {}).get("datos_por_simbolo", [])

if volumen_data:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Volumen en USDT por Símbolo")
        df_vol_usdt = pd.DataFrame(volumen_data)
        
        fig_vol_usdt = px.pie(
            df_vol_usdt,
            values="volumen_usdt",
            names="symbol",
            title="Distribución del Volumen (USDT)",
            hole=0.4
        )
        st.plotly_chart(fig_vol_usdt, use_container_width=True)
    
    with col2:
        st.subheader("Número de Trades por Símbolo")
        
        fig_trades = px.bar(
            df_vol_usdt,
            x="symbol",
            y="num_trades",
            title="Total de Trades Ejecutados",
            labels={"num_trades": "Número de Trades", "symbol": "Símbolo"},
            color="num_trades",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_trades, use_container_width=True)
    
    # Gráfico de volumen promedio y USDT por trade
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Volumen Promedio por Periodo")
        fig_vol_prom = px.bar(
            df_vol_usdt,
            x="symbol",
            y="volumen_promedio_por_periodo",
            title="Volumen Promedio por Vela (BTC)",
            labels={"volumen_promedio_por_periodo": "Volumen (BTC)", "symbol": "Símbolo"},
            color="volumen_promedio_por_periodo",
            color_continuous_scale="Greens"
        )
        st.plotly_chart(fig_vol_prom, use_container_width=True)
    
    with col2:
        st.subheader("USDT por Trade")
        fig_usdt_trade = px.bar(
            df_vol_usdt,
            x="symbol",
            y="usdt_por_trade",
            title="Promedio de USDT por Operación",
            labels={"usdt_por_trade": "USDT/Trade", "symbol": "Símbolo"},
            color="usdt_por_trade",
            color_continuous_scale="Oranges"
        )
        st.plotly_chart(fig_usdt_trade, use_container_width=True)
    
    # Tabla detallada
    st.subheader("Datos Detallados de Volumen")
    st.dataframe(
        df_vol_usdt,
        use_container_width=True,
        hide_index=True,
        column_config={
            "symbol": "Símbolo",
            "volumen_btc": st.column_config.NumberColumn("Vol. BTC", format="%.8f"),
            "volumen_usdt": st.column_config.NumberColumn("Vol. USDT", format="$%.2f"),
            "num_trades": "Trades",
            "volumen_promedio_por_periodo": st.column_config.NumberColumn("Vol. Prom/Periodo", format="%.8f"),
            "usdt_por_trade": st.column_config.NumberColumn("USDT/Trade", format="$%.2f")
        }
    )

st.markdown("---")

# ============================================================================
# SECCIÓN 4: PRESIÓN COMPRADORA VS VENDEDORA
# ============================================================================
st.markdown('<div class="section-header">⚖️ Presión Compradora vs Vendedora</div>', unsafe_allow_html=True)

presion_data = data.get("presion", {}).get("datos_por_simbolo", [])

if presion_data:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Presión por Símbolo")
        df_presion = pd.DataFrame(presion_data)
        
        fig_presion = go.Figure()
        
        fig_presion.add_trace(go.Bar(
            name="Presión Compradora",
            x=df_presion["symbol"],
            y=df_presion["presion_compradora"],
            marker_color="green"
        ))
        
        fig_presion.add_trace(go.Bar(
            name="Presión Vendedora",
            x=df_presion["symbol"],
            y=df_presion["presion_vendedora"],
            marker_color="red"
        ))
        
        fig_presion.update_layout(
            title="Presión Compradora vs Vendedora (%)",
            xaxis_title="Símbolo",
            yaxis_title="Porcentaje (%)",
            barmode="stack"
        )
        st.plotly_chart(fig_presion, use_container_width=True)
    
    with col2:
        st.subheader("Sentimiento del Mercado")
        
        # Crear gráfico de gauge para cada símbolo
        for idx, row in df_presion.iterrows():
            sentimiento_color = "green" if row["sentimiento"] == "ALCISTA" else "red" if row["sentimiento"] == "BAJISTA" else "gray"
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=row["presion_compradora"],
                title={"text": f"{row['symbol']} - {row['sentimiento']}"},
                delta={"reference": 50},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": sentimiento_color},
                    "steps": [
                        {"range": [0, 45], "color": "lightcoral"},
                        {"range": [45, 55], "color": "lightgray"},
                        {"range": [55, 100], "color": "lightgreen"}
                    ],
                    "threshold": {
                        "line": {"color": "black", "width": 4},
                        "thickness": 0.75,
                        "value": 50
                    }
                }
            ))
            
            fig_gauge.update_layout(height=250)
            st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Volúmenes exactos compradores vs vendedores
    st.subheader("Volumen Compradores vs Vendedores (BTC)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_vol_comp = px.bar(
            df_presion,
            x="symbol",
            y=["volumen_compradores", "volumen_vendedores"],
            title="Distribución de Volumen por Tipo de Trader",
            labels={"value": "Volumen (BTC)", "symbol": "Símbolo", "variable": "Tipo"},
            barmode="group"
        )
        st.plotly_chart(fig_vol_comp, use_container_width=True)
    
    with col2:
        # Tabla de datos
        st.dataframe(
            df_presion,
            use_container_width=True,
            hide_index=True,
            column_config={
                "symbol": "Símbolo",
                "presion_compradora": st.column_config.NumberColumn("Presión Comp. (%)", format="%.2f"),
                "presion_vendedora": st.column_config.NumberColumn("Presión Vend. (%)", format="%.2f"),
                "sentimiento": "Sentimiento",
                "volumen_compradores": st.column_config.NumberColumn("Vol. Compradores", format="%.8f"),
                "volumen_vendedores": st.column_config.NumberColumn("Vol. Vendedores", format="%.8f")
            }
        )

st.markdown("---")

# ============================================================================
# SECCIÓN 5: ESTADÍSTICAS DE AGGREGATE TRADES
# ============================================================================
st.markdown('<div class="section-header">🔄 Análisis de Aggregate Trades</div>', unsafe_allow_html=True)

aggtrades_data = data.get("aggtrades", {}).get("datos_por_simbolo", [])

if aggtrades_data:
    df_aggtrades = pd.DataFrame(aggtrades_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Total de Aggregate Trades")
        
        fig_total_trades = px.bar(
            df_aggtrades,
            x="symbol",
            y="total_aggtrades",
            title="Número Total de Aggregate Trades",
            labels={"total_aggtrades": "Total AggTrades", "symbol": "Símbolo"},
            color="total_aggtrades",
            color_continuous_scale="Purples"
        )
        st.plotly_chart(fig_total_trades, use_container_width=True)
    
    with col2:
        st.subheader("Distribución Compradores/Vendedores")
        
        fig_dist_trades = go.Figure()
        
        fig_dist_trades.add_trace(go.Bar(
            name="Trades Compradores",
            x=df_aggtrades["symbol"],
            y=df_aggtrades["trades_compradores"],
            marker_color="green"
        ))
        
        fig_dist_trades.add_trace(go.Bar(
            name="Trades Vendedores",
            x=df_aggtrades["symbol"],
            y=df_aggtrades["trades_vendedores"],
            marker_color="red"
        ))
        
        fig_dist_trades.update_layout(
            title="Trades por Tipo de Trader",
            xaxis_title="Símbolo",
            yaxis_title="Número de Trades",
            barmode="stack"
        )
        st.plotly_chart(fig_dist_trades, use_container_width=True)
    
    # Porcentaje y cantidad promedio
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Porcentaje de Trades Compradores")
        
        fig_pct_comp = px.bar(
            df_aggtrades,
            x="symbol",
            y="pct_trades_compradores",
            title="% de Trades Ejecutados por Compradores",
            labels={"pct_trades_compradores": "Porcentaje (%)", "symbol": "Símbolo"},
            color="pct_trades_compradores",
            color_continuous_scale="RdYlGn"
        )
        fig_pct_comp.add_hline(y=50, line_dash="dash", line_color="gray", annotation_text="Equilibrio 50%")
        st.plotly_chart(fig_pct_comp, use_container_width=True)
    
    with col2:
        st.subheader("Cantidad Promedio por Trade")
        
        fig_cant_prom = px.bar(
            df_aggtrades,
            x="symbol",
            y="cantidad_promedio_trade",
            title="Cantidad Promedio por Trade (BTC)",
            labels={"cantidad_promedio_trade": "Cantidad (BTC)", "symbol": "Símbolo"},
            color="cantidad_promedio_trade",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_cant_prom, use_container_width=True)
    
    # Tabla detallada
    st.subheader("Datos Detallados de Aggregate Trades")
    st.dataframe(
        df_aggtrades,
        use_container_width=True,
        hide_index=True,
        column_config={
            "symbol": "Símbolo",
            "total_aggtrades": "Total AggTrades",
            "trades_compradores": "Trades Compradores",
            "trades_vendedores": "Trades Vendedores",
            "pct_trades_compradores": st.column_config.NumberColumn("% Trades Comp.", format="%.2f"),
            "cantidad_promedio_trade": st.column_config.NumberColumn("Cant. Prom/Trade", format="%.8f")
        }
    )

st.markdown("---")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>Binance Trading Analytics Dashboard | Datos en tiempo real desde MongoDB</p>
        <p>Actualizado: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    unsafe_allow_html=True
)
