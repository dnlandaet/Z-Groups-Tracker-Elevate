import streamlit as st
import pandas as pd

st.title("📊 Mi Primer Dashboard")
st.write("¡Hola Mundo! Este dashboard está conectado con GitHub.")

# Creamos una tabla rápida
datos = pd.DataFrame({
    'Categoría': ['A', 'B', 'C'],
    'Valores': [10, 20, 30]
})

st.bar_chart(datos.set_index('Categoría'))