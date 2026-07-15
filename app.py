import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Amrize Monthly Comparative Dashboard",
    page_icon="📊",
    layout="wide"
)

# 2. Custom CSS to inject Brand Colors (Amrize Palette)
st.markdown(f"""
    <style>
    /* Headers & Title Colors */
    h1, h2, h3, h4, h5, h6 {{
        color: #011e6a !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: #011e6a;
    }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{
        color: #ffffff !important;
    }}
    
    /* Metric Card Styling */
    div[data-testid="stMetric"] {{
        background-color: #f0f5ff;
        border-left: 5px solid #2a6eff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    div[data-testid="stMetricValue"] {{
        color: #0404bd !important;
        font-weight: bold;
    }}
    div[data-testid="stMetricLabel"] {{
        color: #011e6a !important;
        font-size: 14px;
        font-weight: 500;
    }}
    
    /* Info Box / Alert Styling overrides */
    .stAlert {{
        border-left-color: #7cd3ff !important;
    }}
    
    /* Horizontal Dividers */
    hr {{
        border-top: 2px solid #7cd3ff;
    }}
    </style>
""", unsafe_allow_html=True)

# --- BRANDING: AMRIZE LOGO INTEGRATION ---
# Usamos la URL directa del render en PNG que provee Wikimedia Commons para evitar problemas de compatibilidad con SVG en HTML puro de Streamlit
logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Amrize_Logo_2025.svg/512px-Amrize_Logo_2025.svg.png"

# Colocamos el Logo y el Título alineados
col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.image(logo_url, use_container_width=True)
with col_title:
    st.title("Credit & Portfolio Control Dashboard")

st.markdown("Upload your comparative monthly files below to track analyst changes and overall portfolio movement.")

# --- EL RESTO DE TU CÓDIGO (STEP 1 EN ADELANTE) CONTINÚA EXACTAMENTE IGUAL ---