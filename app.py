import streamlit as st
import pandas as pd
import os
import re

# 1. Page Configuration
st.set_page_config(
    page_title="Amrize - Z-Groups Tracker Elevate",
    page_icon="📊",
    layout="wide"
)

# 2. Custom CSS to inject Brand Colors & Equal Metric Heights
st.markdown("""
    <style>
    /* Headers & Title Colors */
    h1, h2, h3, h4, h5, h6 {
        color: #011e6a !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #011e6a;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    
    /* Metric Card Styling & EQUAL HEIGHT FIX */
    div[data-testid="stMetric"] {
        background-color: #f0f5ff;
        border-left: 5px solid #2a6eff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        min-height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    div[data-testid="stMetricValue"] {
        color: #0404bd !important;
        font-weight: bold;
        font-size: 26px !important;
        word-break: break-all;
    }
    div[data-testid="stMetricLabel"] {
        color: #011e6a !important;
        font-size: 14px;
        font-weight: 500;
    }
    
    /* Info Box / Alert Styling overrides */
    .stAlert {
        border-left-color: #7cd3ff !important;
    }
    
    /* Horizontal Dividers */
    hr {
        border-top: 2px solid #7cd3ff;
    }
    </style>
""", unsafe_allow_html=True)

# --- LOGIN SYSTEM ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

def check_login():
    """Validates the hardcoded credentials"""
    if st.session_state["username_input"] == "ElevateBE" and st.session_state["password_input"] == "Elevate2026":
        st.session_state["logged_in"] = True
        st.success("Login successful!")
        if "login_error" in st.session_state:
            del st.session_state["login_error"]
    else:
        st.session_state["login_error"] = "❌ Incorrect username or password."

if not st.session_state["logged_in"]:
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.write("")
        st.write("")
        logo_names = ["Amrize_Logo_2025.svg", "Amrize_Logo_2025.png", "logo.png", "logo.svg"]
        for name in logo_names:
            if os.path.exists(name):
                st.image(name, width=220)
                break
        
        st.subheader("🔑 Sign In to Z-Groups Tracker")
        st.text_input("Username", key="username_input")
        st.text_input("Password", type="password", key="password_input", on_change=check_login)
        st.button("Login", on_click=check_login, type="primary")
        
        if "login_error" in st.session_state:
            st.error(st.session_state["login_error"])
            
    st.stop()

# --- BRANDING: AUTOMATIC LOGO DETECTOR (After Login) ---
logo_file = None
possible_names = ["Amrize_Logo_2025.svg", "Amrize_Logo_2025.png", "logo.png", "logo.svg"]
for name in possible_names:
    if os.path.exists(name):
        logo_file = name
        break

if logo_file:
    st.image(logo_file, width=280)
else:
    st.info("⚠️ Place 'Amrize_Logo_2025.svg' or 'logo.png' in your project folder.")

st.title("Z-Groups Tracker Elevate")
st.markdown("Upload your comparative monthly files (Excel or CSV) or connect to Google Sheets to track analyst changes and overall portfolio movement.")

# --- HELPER FUNCTION: UNIVERSAL FILE READER ---
def load_data_file(uploaded_file):
    """Dynamically reads Excel (.xlsx, .xls) and CSV files"""
    if uploaded_file is not None:
        file_name = uploaded_file.name.lower()
        if file_name.endswith('.csv'):
            try:
                return pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                return pd.read_csv(uploaded_file, encoding='latin1')
        else:
            return pd.read_excel(uploaded_file)
    return None

# --- STEP 1: DATA SOURCE SELECTION ---
st.sidebar.header("Data Source Selection")
data_source = st.sidebar.radio(
    "Choose Data Source:",
    ("Upload Files (Excel / CSV)", "Connect Google Sheets")
)

df_prev_raw = None
df_curr_raw = None

if data_source == "Upload Files (Excel / CSV)":
    prev_file = st.sidebar.file_uploader("Upload PREVIOUS MONTH file", type=["xlsx", "xls", "csv"])
    curr_file = st.sidebar.file_uploader("Upload CURRENT MONTH file", type=["xlsx", "xls", "csv"])
    
    if prev_file and curr_file:
        try:
            df_prev_raw = load_data_file(prev_file)
            df_curr_raw = load_data_file(curr_file)
        except Exception as e:
            st.error(f"Error reading uploaded files: {e}")
            st.stop()

else:
    default_sheet_url = "https://docs.google.com/spreadsheets/d/1HmShbAOnElJOQ9qy0lvYkxL6qxS7dc2xl9QzuUWTaAs/edit?gid=1603648333#gid=1603648333"
    sheet_url = st.sidebar.text_input("Google Sheet URL", value=default_sheet_url)
    
    if st.sidebar.button("Load Google Sheets Data"):
        try:
            if "/d/" in sheet_url:
                sheet_id = sheet_url.split("/d/")[1].split("/")[0]
            else:
                sheet_id = sheet_url
                
            url_pm = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=P.M.+Report"
            url_cm = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=C.M.+Report"
            
            df_prev_raw = pd.read_csv(url_pm)
            df_curr_raw = pd.read_csv(url_cm)
            
            st.session_state["df_prev_raw"] = df_prev_raw
            st.session_state["df_curr_raw"] = df_curr_raw
            st.sidebar.success("Google Sheets loaded successfully!")
        except Exception as e:
            st.error(f"Error connecting to Google Sheets: {e}")
            st.stop()
    elif "df_prev_raw" in st.session_state and "df_curr_raw" in st.session_state:
        df_prev_raw = st.session_state["df_prev_raw"]
        df_curr_raw = st.session_state["df_curr_raw"]

if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.rerun()

if df_prev_raw is None or df_curr_raw is None:
    st.info("💡 Please upload both previous and current month files or load the Google Sheets data from the sidebar.")
    st.stop()

# --- STEP 2: ROBUST DATA CLEANING & VALIDATION ---

def sanitize_and_normalize_columns(df):
    """Strip spaces and assign Status column if located in Column G (7th column)"""
    df.columns = df.columns.astype(str).str.strip()
    
    if "Status" not in df.columns and len(df.columns) >= 7:
        df.rename(columns={df.columns[6]: "Status"}, inplace=True)
        
    return df

df_prev_raw = sanitize_and_normalize_columns(df_prev_raw)
df_curr_raw = sanitize_and_normalize_columns(df_curr_raw)

required_cols = ["Customer", "Customer Name", "Z-Group", "Credit Analyst", "Total Past Due", "Total Balance"]

missing_prev = [c for c in required_cols if c not in df_prev_raw.columns]
missing_curr = [c for c in required_cols if c not in df_curr_raw.columns]

if missing_prev or missing_curr:
    st.error(f"Error: Missing required columns!\nPrevious File Missing: {missing_prev}\nCurrent File Missing: {missing_curr}")
    st.stop()

def clean_currency_series(series):
    """Converts strings with $, commas, or spaces safely into floats"""
    return pd.to_numeric(
        series.astype(str)
        .str.replace(r'[\$,]', '', regex=True)
        .str.strip(),
        errors='coerce'
    ).fillna(0)

def clean_data(df):
    df_clean = df.copy()
    
    df_clean = df_clean[
        df_clean["Total Balance"].astype(str).str.strip().str.upper() != "NOT FOUND"
    ]
    
    df_clean["Customer"] = (
        pd.to_numeric(df_clean["Customer"].astype(str).str.replace(r'\.0$', '', regex=True), errors='coerce')
        .fillna(0)
        .astype(int)
        .astype(str)
    )
    
    df_clean["Total Balance"] = clean_currency_series(df_clean["Total Balance"])
    df_clean["Total Past Due"] = clean_currency_series(df_clean["Total Past Due"])
    
    if "Status" in df_clean.columns:
        df_clean["Status"] = df_clean["Status"].fillna("Unspecified").astype(str).str.strip()
    else:
        df_clean["Status"] = "Unspecified"
        
    return df_clean

# Base global limpia
df_prev_global = clean_data(df_prev_raw)
df_curr_global = clean_data(df_curr_raw)

# --- STEP 3: GENERAL PORTFOLIO SUMMARY (BASADO ESTRICTAMENTE EN STATUS == 'ACTIVE' DE LA COLUMNA G) ---
prev_active_accounts = df_prev_global[df_prev_global["Status"].str.upper() == "ACTIVE"]
curr_active_accounts = df_curr_global[df_curr_global["Status"].str.upper() == "ACTIVE"]

prev_active_count = len(prev_active_accounts)
curr_active_count = len(curr_active_accounts)

if prev_active_count > 0:
    variation_active = ((curr_active_count - prev_active_count) / prev_active_count) * 100
    variation_str_active = f"{variation_active:+.2f}%"
else:
    variation_str_active = "N/A"

st.subheader("📌 General Portfolio Summary")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Active Accounts (Previous Month)", 
        value=f"{prev_active_count:,}"
    )
with col2:
    st.metric(
        label="Active Accounts (Current Month)", 
        value=f"{curr_active_count:,}", 
        delta=variation_str_active
    )
with col3:
    total_balance_active_curr = curr_active_accounts[curr_active_accounts["Total Balance"] != 0]["Total Balance"].sum()
    st.metric(
        label="Total Active Balance (Current Month)", 
        value=f"${total_balance_active_curr:,.2f}"
    )

st.write("---")

# --- SIDEBAR FILTER: STATUS (APLICA A LAS TABLAS DE DETALLE INFERIORES) ---
df_prev_clean = df_prev_global.copy()
df_curr_clean = df_curr_global.copy()

available_statuses = sorted(list(set(df_prev_clean["Status"].unique()).union(set(df_curr_clean["Status"].unique()))))
if available_statuses and available_statuses != ["Unspecified"]:
    selected_statuses = st.sidebar.multiselect(
        "Filter Tables by Status (Column G)",
        options=available_statuses,
        default=available_statuses
    )
    if selected_statuses:
        df_prev_clean = df_prev_clean[df_prev_clean["Status"].isin(selected_statuses)]
        df_curr_clean = df_curr_clean[df_curr_clean["Status"].isin(selected_statuses)]

# Open Balance datasets (Open AR)
df_prev_open = df_prev_clean[df_prev_clean["Total Balance"] != 0]
df_curr_open = df_curr_clean[df_curr_clean["Total Balance"] != 0]

# --- STEP 4: STRICT ANALYST-TO-ANALYST TRANSITION TABLE ---
st.subheader("🔄 Credit Analyst Assignment Transitions")
st.markdown("These are the accounts that transitioned strictly **from one specific credit analyst to another** (excluding unassigned states or None).")

df_comparison = pd.merge(
    df_prev_clean[["Customer", "Credit Analyst", "Total Past Due", "Total Balance"]],
    df_curr_clean[["Customer", "Customer Name", "Credit Analyst", "Total Past Due", "Total Balance"]],
    on="Customer",
    suffixes=("_Previous", "_Current")
)

df_comparison["Credit Analyst_Previous"] = df_comparison["Credit Analyst_Previous"].fillna("").astype(str).str.strip()
df_comparison["Credit Analyst_Current"] = df_comparison["Credit Analyst_Current"].fillna("").astype(str).str.strip()

invalid_states = ["NOT FOUND", "NO CREDIT ANALYST ASSIGNED.", "NAN", "", "NONE", "UNASSIGNED", "NONE.", "NULL"]

df_analyst_changes = df_comparison[
    (df_comparison["Credit Analyst_Previous"] != df_comparison["Credit Analyst_Current"]) &
    (~df_comparison["Credit Analyst_Previous"].str.upper().isin(invalid_states)) &
    (~df_comparison["Credit Analyst_Current"].str.upper().isin(invalid_states)) &
    (df_comparison["Credit Analyst_Previous"].notna()) &
    (df_comparison["Credit Analyst_Current"].notna())
]

transferred_balance = 0
transferred_past_due = 0

if not df_analyst_changes.empty:
    df_changes_formatted = df_analyst_changes[[
        "Customer", "Customer Name", 
        "Credit Analyst_Previous", "Credit Analyst_Current", 
        "Total Past Due_Current", "Total Balance_Current"
    ]].rename(columns={
        "Credit Analyst_Previous": "Previous Analyst",
        "Credit Analyst_Current": "Current Analyst",
        "Total Past Due_Current": "Total Past Due",
        "Total Balance_Current": "Total Balance"
    })

    st.dataframe(
        df_changes_formatted.style.format({
            "Total Past Due": "${:,.2f}",
            "Total Balance": "${:,.2f}"
        }),
        use_container_width=True
    )
    
    transferred_past_due = df_analyst_changes["Total Past Due_Current"].sum()
    transferred_balance = df_analyst_changes["Total Balance_Current"].sum()
    transferred_count = len(df_analyst_changes)
    
    st.info(
        f"💰 **Financial Impact of Assignments:** Identified **{transferred_count}** accounts transferred between valid analysts, "
        f"representing **${transferred_balance:,.2f}** in Total Balance and **${transferred_past_due:,.2f}** in Total Past Due."
    )
else:
    st.success("✅ No credit analyst assignment transitions were detected between valid analysts for the selected status filter.")

st.write("---")

# --- NEW SECTION: NEW ACCOUNTS OF THE MONTH ---
st.subheader("✨ New Accounts of the Month")
st.markdown("These are new active accounts identified in the current month with open AR that did not exist in the previous month report.")

prev_customer_ids = set(df_prev_clean["Customer"].unique())
df_new_accounts = df_curr_open[~df_curr_open["Customer"].isin(prev_customer_ids)]

new_accounts_count = len(df_new_accounts)
new_accounts_balance = df_new_accounts["Total Balance"].sum()

if not df_new_accounts.empty:
    df_new_formatted = df_new_accounts[[
        "Customer", "Customer Name", "Z-Group", "Credit Analyst", "Total Past Due", "Total Balance"
    ]].rename(columns={
        "Credit Analyst": "Analyst",
        "Total Past Due": "Total Past Due",
        "Total Balance": "Total Balance"
    })

    st.dataframe(
        df_new_formatted.style.format({
            "Total Past Due": "${:,.2f}",
            "Total Balance": "${:,.2f}"
        }),
        use_container_width=True
    )
    st.info(
        f"New Accounts Impact: Identified {new_accounts_count} new open AR accounts with a combined balance of ${new_accounts_balance:,.2f}."
    )
else:
    st.success("No new open AR accounts were identified for the current month.")

st.write("---")

# --- UNASSIGNED ACCOUNTS SECTION ---
st.subheader("⚠️ Unassigned Accounts")
st.markdown("These are current month accounts with an open balance that do not have an active Credit Analyst assigned (contains 'No Credit Analyst Assigned.', 'Not Found', or blank fields).")

df_unassigned = df_curr_open[
    (df_curr_open["Credit Analyst"].astype(str).str.strip().str.upper().isin(invalid_states)) |
    (df_curr_open["Credit Analyst"].isna())
]

unassigned_balance_sum = 0
unassigned_count = len(df_unassigned)

if not df_unassigned.empty:
    df_unassigned_formatted = df_unassigned[[
        "Customer", "Customer Name", "Z-Group", "Credit Analyst", "Total Past Due", "Total Balance"
    ]].rename(columns={
        "Credit Analyst": "Assigned Status",
        "Total Past Due": "Total Past Due",
        "Total Balance": "Total Balance"
    })

    st.dataframe(
        df_unassigned_formatted.style.format({
            "Total Past Due": "${:,.2f}",
            "Total Balance": "${:,.2f}"
        }),
        use_container_width=True
    )

    unassigned_balance_sum = df_unassigned["Total Balance"].sum()
    st.warning(
        f"Total Exposure Unassigned: There are {unassigned_count} accounts with open balance currently without an analyst, "
        f"representing a total of ${unassigned_balance_sum:,.2f}."
    )
else:
    st.success("Great! Every active open-balance account has an analyst assigned for the current month.")

st.write("---")

# --- STEP 5: ANALYST PORTFOLIO DISTRIBUTION (REGLAS DE MUESTRA EXACTAS REQUERIDAS) ---
st.subheader("👥 Analyst Portfolio Distribution & Monthly Variation")
st.markdown("Detailed breakdown of analyst portfolios including overall accounts (Active + Inactive) and open AR active exposure.")

# 1. Total cuentas sin importar status (Active e Inactive)
df_prev_valid_analysts = df_prev_global[~df_prev_global["Credit Analyst"].astype(str).str.strip().str.upper().isin(invalid_states)]
df_curr_valid_analysts = df_curr_global[~df_curr_global["Credit Analyst"].astype(str).str.strip().str.upper().isin(invalid_states)]

prev_total_all = df_prev_valid_analysts.groupby("Credit Analyst").agg(Total_Prev_All=("Customer", "count")).reset_index()
curr_total_all = df_curr_valid_analysts.groupby("Credit Analyst").agg(Total_Curr_All=("Customer", "count")).reset_index()

# 2. Cuentas con Open AR (SOLO ACTIVE)
df_prev_open_active = df_prev_valid_analysts[
    (df_prev_valid_analysts["Total Balance"] != 0) & 
    (df_prev_valid_analysts["Status"].str.upper() == "ACTIVE")
]

df_curr_open_active = df_curr_valid_analysts[
    (df_curr_valid_analysts["Total Balance"] != 0) & 
    (df_curr_valid_analysts["Status"].str.upper() == "ACTIVE")
]

prev_open_active_dist = df_prev_open_active.groupby("Credit Analyst").agg(Open_AR_Prev_Active=("Customer", "count")).reset_index()
curr_open_active_dist = df_curr_open_active.groupby("Credit Analyst").agg(
    Open_AR_Curr_Active=("Customer", "count"),
    Sum_Past_Due=("Total Past Due", "sum"),
    Sum_Balance=("Total Balance", "sum")
).reset_index()

# Unir métricas en una sola tabla
df_dist_merged = pd.merge(curr_open_active_dist, prev_open_active_dist, on="Credit Analyst", how="outer")
df_dist_merged = pd.merge(df_dist_merged, curr_total_all, on="Credit Analyst", how="outer")
df_dist_merged = pd.merge(df_dist_merged, prev_total_all, on="Credit Analyst", how="outer").fillna(0)

# Calcular % de cambio en Open AR
def calc_open_ar_pct(row):
    prev = row["Open_AR_Prev_Active"]
    curr = row["Open_AR_Curr_Active"]
    if prev > 0:
        return f"{((curr - prev) / prev * 100):+.2f}%"
    elif curr > 0:
        return "New (+100%)"
    else:
        return "0.00%"

df_dist_merged["Open AR % Change"] = df_dist_merged.apply(calc_open_ar_pct, axis=1)
df_dist_merged = df_dist_merged.sort_values(by="Open_AR_Curr_Active", ascending=False)

# Reordenar y formatear con encabezados ejecutivos claros
df_dist_final = df_dist_merged[[
    "Credit Analyst", 
    "Total_Prev_All", 
    "Total_Curr_All",
    "Open_AR_Prev_Active", 
    "Open_AR_Curr_Active", 
    "Open AR % Change", 
    "Sum_Past_Due", 
    "Sum_Balance"
]].rename(columns={
    "Credit Analyst": "Credit Analyst",
    "Total_Prev_All": "Prev Accounts (All)",
    "Total_Curr_All": "Curr Accounts (All)",
    "Open_AR_Prev_Active": "Prev Open AR (Active)",
    "Open_AR_Curr_Active": "Curr Open AR (Active)",
    "Open AR % Change": "Open AR % Change",
    "Sum_Past_Due": "Total Past Due",
    "Sum_Balance": "Total Balance"
})

st.dataframe(
    df_dist_final.style.format({
        "Prev Accounts (All)": "{:,.0f}",
        "Curr Accounts (All)": "{:,.0f}",
        "Prev Open AR (Active)": "{:,.0f}",
        "Curr Open AR (Active)": "{:,.0f}",
        "Total Past Due": "${:,.2f}",
        "Total Balance": "${:,.2f}"
    }),
    use_container_width=True
)

st.write("---")

# --- EXECUTIVE SUMMARY ---
st.subheader("📋 Executive Summary & Insights")

if not curr_open_active_dist.empty:
    top_account_analyst_row = curr_open_active_dist.loc[curr_open_active_dist["Open_AR_Curr_Active"].idxmax()]
    top_acc_analyst = top_account_analyst_row["Credit Analyst"]
    top_acc_count = top_account_analyst_row["Open_AR_Curr_Active"]

    top_exposure_analyst_row = curr_open_active_dist.loc[curr_open_active_dist["Sum_Balance"].idxmax()]
    top_exp_analyst = top_exposure_analyst_row["Credit Analyst"]
    top_exp_balance = top_exposure_analyst_row["Sum_Balance"]
else:
    top_acc_analyst, top_acc_count = "N/A", 0
    top_exp_analyst, top_exp_balance = "N/A", 0

unassigned_ratio = (unassigned_balance_sum / total_balance_active_curr * 100) if total_balance_active_curr > 0 else 0

col_summary, col_notes = st.columns([2, 1])

with col_summary:
    st.markdown(f"""
    Workload Leader: {top_acc_analyst} currently manages the largest volume of active clients with {top_acc_count} accounts.
    
    Risk Exposure Leader: {top_exp_analyst} holds the highest portfolio exposure under management, totaling ${top_exp_balance:,.2f} in Total Balance.
    
    Transitional Exposure: A total of ${transferred_balance:,.2f} (and ${transferred_past_due:,.2f} in Past Due) has shifted analyst responsibility this month.
    
    New Accounts Exposure: {new_accounts_count} new accounts added this month with an open balance totaling ${new_accounts_balance:,.2f}.
    
    Unassigned Portfolio: There are {unassigned_count} unassigned accounts, representing {unassigned_ratio:.2f}% of the total open balance (${unassigned_balance_sum:,.2f}).
    """)
    
with col_notes:
    if unassigned_count > 0:
        st.warning(f"Action Required: We recommend reviewing and assigning the {unassigned_count} unassigned accounts immediately to minimize portfolio risk of ${unassigned_balance_sum:,.2f}.")
    else:
        st.success("Outstanding! The entire credit team is fully assigned. No unattended portfolio balances detected this month.")