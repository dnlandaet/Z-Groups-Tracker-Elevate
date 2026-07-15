import streamlit as st
import pandas as pd

# Configuración de la página del dashboard
st.set_page_config(
    page_title="Dashboard de Comparativa Mensual",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard de Control de Créditos y Cartera")
st.markdown("Sube los archivos de los meses para analizar los movimientos de analistas y balances.")

# --- PASO 1: SUBIDA DE ARCHIVOS ---
st.sidebar.header("Carga de Datos")
archivo_anterior = st.sidebar.file_uploader("Subir archivo MES ANTERIOR (Excel)", type=["xlsx", "xls"])
archivo_actual = st.sidebar.file_uploader("Subir archivo MES ACTUAL (Excel)", type=["xlsx", "xls"])

# Advertencia si falta algún archivo
if not archivo_anterior or not archivo_actual:
    st.info("💡 Por favor, sube ambos archivos de Excel en la barra lateral para generar el análisis.")
else:
    # --- PASO 2: LECTURA Y LIMPIEZA DE DATOS ---
    try:
        df_ant = pd.read_excel(archivo_anterior)
        df_act = pd.read_excel(archivo_actual)
    except Exception as e:
        st.error(f"Error al leer los archivos de Excel: {e}")
        st.stop()

    # Columnas requeridas
    columnas_requeridas = ["Customer", "Customer Name", "Z-Group", "Credit Analyst", "Total Past Due", "Total Balance"]
    
    # Validar que los archivos tengan las columnas necesarias
    if not all(col in df_ant.columns for col in columnas_requeridas) or not all(col in df_act.columns for col in columnas_requeridas):
        st.error(f"Error: Asegúrate de que ambos archivos contengan exactamente estas columnas: {', '.join(columnas_requeridas)}")
        st.stop()

    # Función para limpiar y filtrar datos con balance abierto (excluye nulos, "Not Found", 0 y textos similares)
    def limpiar_datos(df):
        # Convertir a string para hacer la comparación de 'Not Found' de forma segura
        df_clean = df.copy()
        
        # Eliminar filas donde Total Balance sea "Not Found" (sin importar mayúsculas/minúsculas o espacios)
        df_clean = df_clean[
            df_clean["Total Balance"].astype(str).str.strip().str.upper() != "NOT FOUND"
        ]
        
        # Convertir las columnas numéricas a float, tratando errores como NaN
        df_clean["Total Balance"] = pd.to_numeric(df_clean["Total Balance"], errors='coerce')
        df_clean["Total Past Due"] = pd.to_numeric(df_clean["Total Past Due"], errors='coerce')
        
        # Rellenar nulos con 0 para evitar errores matemáticos
        df_clean["Total Balance"] = df_clean["Total Balance"].fillna(0)
        df_clean["Total Past Due"] = df_clean["Total Past Due"].fillna(0)
        
        return df_clean

    df_ant_clean = limpiar_datos(df_ant)
    df_act_clean = limpiar_datos(df_act)

    # Filtrar únicamente las cuentas que tienen "balance abierto" (Total Balance diferente de 0)
    df_ant_abierto = df_ant_clean[df_ant_clean["Total Balance"] != 0]
    df_act_abierto = df_act_clean[df_act_clean["Total Balance"] != 0]

    # --- PASO 3: CÁLCULO DE MÉTRICAS E INDICADORES ---
    cant_ant = len(df_ant_abierto)
    cant_act = len(df_act_abierto)
    
    # Calcular variación porcentual de cantidad de cuentas
    if cant_ant > 0:
        variacion = ((cant_act - cant_ant) / cant_ant) * 100
        variacion_str = f"{variacion:+.2f}%"
    else:
        variacion_str = "N/A (Mes anterior sin cuentas)"

    st.subheader("📌 Resumen General")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Cuentas con Balance Abierto (Mes Anterior)", 
            value=f"{cant_ant:,}"
        )
    with col2:
        st.metric(
            label="Cuentas con Balance Abierto (Mes Actual)", 
            value=f"{cant_act:,}", 
            delta=variacion_str
        )
    with col3:
        total_monto_act = df_act_abierto["Total Balance"].sum()
        st.metric(
            label="Monto Total Balance Abierto (Mes Actual)", 
            value=f"${total_monto_act:,.2f}"
        )

    st.write("---")

    # --- PASO 4: TABLA 1 - CUENTAS QUE CAMBIARON DE CREDIT ANALYST ---
    st.subheader("🔄 Cuentas con Cambio de Analista de Crédito")
    st.markdown("Esta tabla muestra las cuentas en las que el analista asignado cambió de un mes al otro, junto a su dinero en riesgo actual.")

    # Cruzar datos usando el número de cliente "Customer"
    df_comparativa = pd.merge(
        df_ant_clean[["Customer", "Credit Analyst", "Total Past Due", "Total Balance"]],
        df_act_clean[["Customer", "Customer Name", "Credit Analyst", "Total Past Due", "Total Balance"]],
        on="Customer",
        suffixes=("_Anterior", "_Actual")
    )

    # Filtrar donde el analista sea diferente
    df_cambio_analista = df_comparativa[
        df_comparativa["Credit Analyst_Anterior"] != df_comparativa["Credit Analyst_Actual"]
    ]

    # Formatear la tabla de salida
    if not df_cambio_analista.empty:
        # Renombrar columnas para que sean más claras
        df_cambio_presentacion = df_cambio_analista[[
            "Customer", "Customer Name", 
            "Credit Analyst_Anterior", "Credit Analyst_Actual", 
            "Total Past Due_Actual", "Total Balance_Actual"
        ]].rename(columns={
            "Credit Analyst_Anterior": "Analista Anterior",
            "Credit Analyst_Actual": "Analista Nuevo",
            "Total Past Due_Actual": "Total Past Due (Actual)",
            "Total Balance_Actual": "Total Balance (Actual)"
        })

        # Mostrar tabla estilizada con formato de moneda en streamlit
        st.dataframe(
            df_cambio_presentacion.style.format({
                "Total Past Due (Actual)": "${:,.2f}",
                "Total Balance (Actual)": "${:,.2f}"
            }),
            use_container_width=True
        )
        
        # Resumen monetario del cambio
        total_past_due_cambio = df_cambio_analista["Total Past Due_Actual"].sum()
        total_balance_cambio = df_cambio_analista["Total Balance_Actual"].sum()
        
        st.info(
            f"💰 **Impacto financiero de los cambios:** Las cuentas transferidas representan un total de "
            f"**${total_balance_cambio:,.2f}** en Total Balance y **${total_past_due_cambio:,.2f}** en Total Past Due."
        )
    else:
        st.success("✅ No se detectaron cuentas que hayan cambiado de Analista de Crédito entre los meses cargados.")

    st.write("---")

    # --- PASO 5: TABLA 2 - CANTIDAD DE CUENTAS POR ANALISTA (MES ACTUAL) ---
    st.subheader("👥 Cuentas y Cartera por Analista (Mes Actual)")
    st.markdown("Distribución de cuentas con balance abierto (excluyendo 'Not Found') asignadas a cada analista en el mes actual.")

    # Agrupar el dataframe del mes actual ya limpio y filtrado
    df_por_analista = df_act_abierto.groupby("Credit Analyst").agg(
        Cantidad_Cuentas=("Customer", "count"),
        Suma_Total_Past_Due=("Total Past Due", "sum"),
        Suma_Total_Balance=("Total Balance", "sum")
    ).reset_index()

    # Ordenar por cantidad de cuentas de mayor a menor
    df_por_analista = df_por_analista.sort_values(by="Cantidad_Cuentas", ascending=False)

    # Cambiar nombres de las columnas para la presentación
    df_por_analista = df_por_analista.rename(columns={
        "Credit Analyst": "Analista de Crédito",
        "Cantidad_Cuentas": "Cantidad de Cuentas",
        "Suma_Total_Past_Due": "Total Past Due Acumulado",
        "Suma_Total_Balance": "Total Balance Acumulado"
    })

    # Mostrar la tabla en el dashboard
    st.dataframe(
        df_por_analista.style.format({
            "Cantidad de Cuentas": "{:,}",
            "Total Past Due Acumulado": "${:,.2f}",
            "Total Balance Acumulado": "${:,.2f}"
        }),
        use_container_width=True
    )