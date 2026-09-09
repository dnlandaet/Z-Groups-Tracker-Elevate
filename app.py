import streamlit as st
import pandas as pd
import numpy as np
import os
import gc
from io import BytesIO
from datetime import datetime


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Amrize - Z-Groups Tracker Elevate",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# 2. UI / CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #f8fafc;
    color: #1e293b;
    font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
}

h1, h2, h3, h4, h5, h6 {
    color: #011e6a !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px;
}

[data-testid="stSidebar"] {
    background-color: #011e6a;
    border-right: 1px solid #e2e8f0;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
    color: #ffffff !important;
}

div[data-testid="stMetric"] {
    background-color: #f0f5ff !important;
    border: 1px solid #dbeafe !important;
    border-left: 6px solid #2563eb !important;
    padding: 20px !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    height: 140px !important;
    min-height: 140px !important;
    max-height: 140px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    box-sizing: border-box !important;
}

div[data-testid="stMetric"] > div {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

div[data-testid="stMetricValue"] {
    color: #001fbe !important;
    font-weight: 800 !important;
    font-size: 30px !important;
    word-break: break-all;
}

div[data-testid="stMetricLabel"] {
    color: #334155 !important;
    font-size: 13px !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600 !important;
}

div[data-testid="stDataFrame"] {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 8px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.stAlert,
div[data-testid="stAlert"] {
    background-color: #e0f2fe !important;
    border: 1px solid #7dd3fc !important;
    border-left: 6px solid #0284c7 !important;
    color: #0369a1 !important;
    border-radius: 10px !important;
}

.stAlert p,
.stAlert span,
.stAlert div {
    color: #0369a1 !important;
    font-weight: 600 !important;
}

hr {
    border-top: 1.5px solid #e2e8f0;
    margin: 2rem 0;
}

.period-badge {
    background: #f0f5ff;
    color: #011e6a;
    padding: 8px 18px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 14px;
    display: inline-block;
    border: 1px solid #93c5fd;
    margin-bottom: 15px;
    box-shadow: 0 2px 4px rgba(1, 30, 106, 0.05);
}

.stButton > button {
    background-color: #0284c7;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 8px 18px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background-color: #0369a1;
    box-shadow: 0 4px 10px rgba(2, 132, 199, 0.25);
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. CONSTANTS
# ============================================================

MONTHS = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

YEARS = [2024, 2025, 2026, 2027, 2028, 2029, 2030]

REQUIRED_COLUMNS = [
    "Customer",
    "Customer Name",
    "Z-Group",
    "Credit Analyst",
    "Total Past Due",
    "Total Balance"
]

INVALID_ANALYST_STATES = [
    "NOT FOUND",
    "NO CREDIT ANALYST ASSIGNED.",
    "NAN",
    "",
    "NONE",
    "UNASSIGNED",
    "NONE.",
    "NULL"
]

INVALID_ZGROUP_STATES = [
    "NONE",
    "NAN",
    "",
    "NULL",
    "NOT FOUND",
    "NONE."
]


# ============================================================
# 4. LOGIN
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False


def check_login():
    username = st.session_state.get("username_input", "")
    password = st.session_state.get("password_input", "")

    if username == "ElevateBE" and password == "Elevate2026":
        st.session_state["logged_in"] = True
        if "login_error" in st.session_state:
            del st.session_state["login_error"]
    else:
        st.session_state["login_error"] = "❌ Incorrect username or password."


if not st.session_state["logged_in"]:

    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])

    with col_l2:

        logo_names = [
            "Amrize_Logo_2025.svg",
            "Amrize_Logo_2025.png",
            "logo.png",
            "logo.svg"
        ]

        for name in logo_names:
            if os.path.exists(name):
                st.image(name, width=220)
                break

        st.subheader("🔑 Sign In to Z-Groups Tracker")

        st.text_input(
            "Username",
            key="username_input"
        )

        st.text_input(
            "Password",
            type="password",
            key="password_input",
            on_change=check_login
        )

        st.button(
            "Login",
            on_click=check_login,
            type="primary"
        )

        if "login_error" in st.session_state:
            st.error(st.session_state["login_error"])

    st.stop()


# ============================================================
# 5. BRANDING
# ============================================================

logo_file = None

for name in [
    "Amrize_Logo_2025.svg",
    "Amrize_Logo_2025.png",
    "logo.png",
    "logo.svg"
]:
    if os.path.exists(name):
        logo_file = name
        break

if logo_file:
    st.image(logo_file, width=280)
else:
    st.info(
        "⚠️ Place 'Amrize_Logo_2025.svg' or 'logo.png' "
        "in your project folder."
    )

st.title("Z-Groups Tracker Elevate")


# ============================================================
# 6. PERIOD
# ============================================================

st.sidebar.header("🗓️ Report Period Selection")

current_month_index = datetime.now().month - 1
current_year = datetime.now().year

selected_month = st.sidebar.selectbox(
    "Report Month",
    options=MONTHS,
    index=current_month_index
)

selected_year = st.sidebar.selectbox(
    "Report Year",
    options=YEARS,
    index=YEARS.index(current_year)
    if current_year in YEARS else 2
)

report_period_str = f"{selected_month} {selected_year}"

st.markdown(
    f"""
    <div class="period-badge">
        📅 Active Report Period:
        <strong>{report_period_str}</strong>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    "Upload your comparative monthly files (Excel or CSV) "
    "or connect to Google Sheets to track analyst changes "
    "and overall portfolio movement."
)


# ============================================================
# 7. MEMORY-SAFE FILE READER
# ============================================================

def normalize_column_name(name):
    return str(name).strip()


def detect_columns_from_header(uploaded_file):
    file_name = uploaded_file.name.lower()
    uploaded_file.seek(0)

    if file_name.endswith(".csv"):
        try:
            header = pd.read_csv(uploaded_file, nrows=0, encoding="utf-8")
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            header = pd.read_csv(uploaded_file, nrows=0, encoding="latin1")
    else:
        header = pd.read_excel(uploaded_file, nrows=0)

    header.columns = [normalize_column_name(c) for c in header.columns]
    return list(header.columns)


def get_use_columns(uploaded_file):
    columns = detect_columns_from_header(uploaded_file)
    use_columns = [col for col in REQUIRED_COLUMNS if col in columns]

    if "Status" in columns:
        if "Status" not in use_columns:
            use_columns.append("Status")
    elif len(columns) >= 7:
        seventh_column = columns[6]
        if seventh_column not in use_columns:
            use_columns.append(seventh_column)

    return columns, use_columns


def load_data_file(uploaded_file):
    if uploaded_file is None:
        return None

    file_name = uploaded_file.name.lower()

    try:
        columns, use_columns = get_use_columns(uploaded_file)
        missing_required = [col for col in REQUIRED_COLUMNS if col not in columns]

        if missing_required:
            raise ValueError(
                "Missing required columns: " + ", ".join(missing_required)
            )

        uploaded_file.seek(0)

        if file_name.endswith(".csv"):
            try:
                df = pd.read_csv(uploaded_file, usecols=use_columns, encoding="utf-8")
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, usecols=use_columns, encoding="latin1")
        elif file_name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, usecols=use_columns, engine="openpyxl")
        elif file_name.endswith(".xls"):
            df = pd.read_excel(uploaded_file, usecols=use_columns)
        else:
            raise ValueError("Unsupported file type.")

        df.columns = [normalize_column_name(c) for c in df.columns]

        if "Status" not in df.columns and len(columns) >= 7:
            seventh_original = columns[6]
            if seventh_original in df.columns:
                df.rename(columns={seventh_original: "Status"}, inplace=True)

        if "Status" not in df.columns:
            df["Status"] = "Unspecified"

        return df

    except Exception as e:
        raise RuntimeError(f"Could not read '{uploaded_file.name}': {e}")


# ============================================================
# 8. DATA CLEANING
# ============================================================

def clean_currency_series(series):
    if series is None:
        return pd.Series(dtype="float32")

    return (
        series.astype(str)
        .str.replace(r"[\$,]", "", regex=True)
        .str.strip()
        .replace({"nan": np.nan, "None": np.nan, "": np.nan})
        .pipe(pd.to_numeric, errors="coerce")
        .fillna(0)
        .astype("float32")
    )


def clean_customer_series(series):
    numeric = pd.to_numeric(
        series.astype(str).str.replace(r"\.0$", "", regex=True).str.strip(),
        errors="coerce"
    )
    return numeric.fillna(0).astype("int64").astype(str)


def clean_data(df):
    keep_columns = [
        "Customer",
        "Customer Name",
        "Z-Group",
        "Credit Analyst",
        "Total Past Due",
        "Total Balance",
        "Status"
    ]

    df = df[[c for c in keep_columns if c in df.columns]].copy()

    balance_text = df["Total Balance"].astype(str).str.strip().str.upper()
    df = df[balance_text != "NOT FOUND"].copy()

    df["Customer"] = clean_customer_series(df["Customer"])
    df["Total Balance"] = clean_currency_series(df["Total Balance"])
    df["Total Past Due"] = clean_currency_series(df["Total Past Due"])

    for col in ["Customer Name", "Z-Group", "Credit Analyst"]:
        df[col] = df[col].fillna("").astype(str).str.strip()

    df["Status"] = df["Status"].fillna("Unspecified").astype(str).str.strip()
    return df


# ============================================================
# 9. DUPLICATE CUSTOMER PROTECTION
# ============================================================

def consolidate_duplicate_customers(df):
    if df.empty:
        return df

    duplicate_count = df["Customer"].duplicated().sum()
    if duplicate_count == 0:
        return df

    def first_valid(series):
        for value in series:
            value_str = str(value).strip()
            if value_str and value_str.lower() != "nan":
                return value
        return ""

    grouped = df.groupby("Customer", as_index=False).agg(
        {
            "Customer Name": first_valid,
            "Z-Group": first_valid,
            "Credit Analyst": first_valid,
            "Total Past Due": "sum",
            "Total Balance": "sum",
            "Status": first_valid
        }
    )

    st.warning(
        f"⚠️ Duplicate Customer IDs detected: {duplicate_count:,} duplicate rows "
        f"consolidated to prevent multiplied metrics."
    )
    return grouped


# ============================================================
# 10. DATA SOURCE
# ============================================================

st.sidebar.header("Data Source Selection")

data_source = st.sidebar.radio(
    "Choose Data Source:",
    ("Upload Files (Excel / CSV)", "Connect Google Sheets")
)

df_prev_raw = None
df_curr_raw = None


# ============================================================
# 11. FILE UPLOAD
# ============================================================

if data_source == "Upload Files (Excel / CSV)":
    prev_file = st.sidebar.file_uploader(
        "Upload PREVIOUS MONTH file",
        type=["xlsx", "xls", "csv"],
        key="previous_file"
    )
    curr_file = st.sidebar.file_uploader(
        "Upload CURRENT MONTH file",
        type=["xlsx", "xls", "csv"],
        key="current_file"
    )

    if prev_file and curr_file:
        with st.spinner("Loading and optimizing your files..."):
            try:
                df_prev_raw = load_data_file(prev_file)
                df_curr_raw = load_data_file(curr_file)
            except Exception as e:
                st.error(f"❌ Error loading files:\n\n{e}")
                st.stop()


# ============================================================
# 12. GOOGLE SHEETS
# ============================================================

else:
    default_sheet_url = (
        "https://docs.google.com/spreadsheets/d/"
        "1HmShbAOnElJOQ9qy0lvYkxL6qxS7dc2xl9QzuUWTaAs/"
        "edit?gid=1603648333#gid=1603648333"
    )

    sheet_url = st.sidebar.text_input("Google Sheet URL", value=default_sheet_url)

    if st.sidebar.button("Load Google Sheets Data"):
        try:
            if "/d/" in sheet_url:
                sheet_id = sheet_url.split("/d/")[1].split("/")[0]
            else:
                sheet_id = sheet_url.strip()

            url_pm = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=P.M.+Report"
            url_cm = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=C.M.+Report"

            df_prev_raw = pd.read_csv(url_pm)
            df_curr_raw = pd.read_csv(url_cm)

            st.session_state["df_prev_raw"] = df_prev_raw
            st.session_state["df_curr_raw"] = df_curr_raw

            st.sidebar.success("Google Sheets loaded successfully!")

        except Exception as e:
            st.error(f"❌ Error connecting to Google Sheets: {e}")
            st.stop()

    elif "df_prev_raw" in st.session_state and "df_curr_raw" in st.session_state:
        df_prev_raw = st.session_state["df_prev_raw"]
        df_curr_raw = st.session_state["df_curr_raw"]


# ============================================================
# 13. LOGOUT
# ============================================================

if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.session_state.pop("df_prev_raw", None)
    st.session_state.pop("df_curr_raw", None)
    st.rerun()


# ============================================================
# 14. STOP IF NO DATA
# ============================================================

if df_prev_raw is None or df_curr_raw is None:
    st.info(
        "💡 Please upload both previous and current month "
        "files or load the Google Sheets data from the sidebar."
    )
    st.stop()


# ============================================================
# 15. CLEAN DATA
# ============================================================

with st.spinner("Cleaning and validating data..."):
    try:
        df_prev_global = clean_data(df_prev_raw)
        df_curr_global = clean_data(df_curr_raw)

        del df_prev_raw
        del df_curr_raw
        gc.collect()

        df_prev_global = consolidate_duplicate_customers(df_prev_global)
        df_curr_global = consolidate_duplicate_customers(df_curr_global)

    except Exception as e:
        st.error(f"❌ Error processing the data: {e}")
        st.stop()


# ============================================================
# 16. GENERAL PORTFOLIO SUMMARY
# ============================================================

prev_active_accounts = df_prev_global[
    df_prev_global["Status"].str.upper().eq("ACTIVE")
]

curr_active_accounts = df_curr_global[
    df_curr_global["Status"].str.upper().eq("ACTIVE")
]

prev_active_count = len(prev_active_accounts)
curr_active_count = len(curr_active_accounts)

if prev_active_count > 0:
    variation_active = (
        (curr_active_count - prev_active_count) / prev_active_count * 100
    )
    variation_str_active = f"{variation_active:+.2f}%"
else:
    variation_str_active = "N/A"

total_balance_active_curr = curr_active_accounts.loc[
    curr_active_accounts["Total Balance"] != 0, "Total Balance"
].sum()

st.subheader("📌 General Portfolio Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Active Accounts (Previous Month)", f"{prev_active_count:,}")

with col2:
    st.metric(
        f"Active Accounts ({report_period_str})",
        f"{curr_active_count:,}",
        delta=variation_str_active
    )

with col3:
    st.metric(
        f"Total Active Balance ({report_period_str})",
        f"${total_balance_active_curr:,.2f}"
    )

st.write("---")


# ============================================================
# 17. STATUS FILTER
# ============================================================

available_statuses = sorted(
    set(df_prev_global["Status"].unique()).union(
        set(df_curr_global["Status"].unique())
    )
)

selected_statuses = available_statuses

if available_statuses and available_statuses != ["Unspecified"]:
    selected_statuses = st.sidebar.multiselect(
        "Filter Tables by Status (Column G)",
        options=available_statuses,
        default=available_statuses
    )

if selected_statuses:
    df_prev_clean = df_prev_global[df_prev_global["Status"].isin(selected_statuses)]
    df_curr_clean = df_curr_global[df_curr_global["Status"].isin(selected_statuses)]
else:
    df_prev_clean = df_prev_global.iloc[0:0]
    df_curr_clean = df_curr_global.iloc[0:0]

df_prev_open = df_prev_clean[df_prev_clean["Total Balance"] != 0]
df_curr_open = df_curr_clean[df_curr_clean["Total Balance"] != 0]


# ============================================================
# 18. ANALYST TRANSITIONS
# ============================================================

st.subheader("🔄 Credit Analyst Assignment Transitions")
st.markdown(
    "These are the accounts that transitioned strictly **from one specific credit analyst to another** "
    "(excluding unassigned states or None)."
)

prev_transition = df_prev_clean[
    ["Customer", "Credit Analyst", "Total Past Due", "Total Balance"]
]
curr_transition = df_curr_clean[
    ["Customer", "Customer Name", "Credit Analyst", "Total Past Due", "Total Balance"]
]

df_comparison = pd.merge(
    prev_transition,
    curr_transition,
    on="Customer",
    suffixes=("_Previous", "_Current"),
    how="inner"
)

df_comparison["Credit Analyst_Previous"] = (
    df_comparison["Credit Analyst_Previous"].fillna("").astype(str).str.strip()
)
df_comparison["Credit Analyst_Current"] = (
    df_comparison["Credit Analyst_Current"].fillna("").astype(str).str.strip()
)

df_analyst_changes = df_comparison[
    (df_comparison["Credit Analyst_Previous"] != df_comparison["Credit Analyst_Current"])
    & (~df_comparison["Credit Analyst_Previous"].str.upper().isin(INVALID_ANALYST_STATES))
    & (~df_comparison["Credit Analyst_Current"].str.upper().isin(INVALID_ANALYST_STATES))
]

if not df_analyst_changes.empty:
    df_changes_formatted = (
        df_analyst_changes[
            [
                "Customer",
                "Customer Name",
                "Credit Analyst_Previous",
                "Credit Analyst_Current",
                "Total Past Due_Current",
                "Total Balance_Current"
            ]
        ]
        .rename(
            columns={
                "Credit Analyst_Previous": "Previous Analyst",
                "Credit Analyst_Current": "Current Analyst",
                "Total Past Due_Current": "Total Past Due",
                "Total Balance_Current": "Total Balance"
            }
        )
    )

    st.dataframe(
        df_changes_formatted.style.format(
            {"Total Past Due": "${:,.2f}", "Total Balance": "${:,.2f}"}
        ),
        use_container_width=True
    )

    transferred_past_due = df_analyst_changes["Total Past Due_Current"].sum()
    transferred_balance = df_analyst_changes["Total Balance_Current"].sum()
    transferred_count = len(df_analyst_changes)

    st.info(
        f"💰 **Financial Impact of Assignments:** Identified **{transferred_count:,}** accounts "
        f"transferred between valid analysts for {report_period_str}, representing "
        f"**${transferred_balance:,.2f}** in Total Balance and **${transferred_past_due:,.2f}** in Total Past Due."
    )
else:
    df_changes_formatted = pd.DataFrame()
    transferred_count = 0
    transferred_past_due = 0
    transferred_balance = 0

    st.info(f"✅ No credit analyst assignment transitions detected for {report_period_str}.")

del df_comparison
gc.collect()

st.write("---")


# ============================================================
# 19. NEW ACCOUNTS
# ============================================================

st.subheader("✨ New Accounts of the Month")
st.markdown(
    f"These are new active accounts identified in **{report_period_str}** with open AR that did not "
    f"exist in the previous month report."
)

prev_customer_ids = set(df_prev_clean["Customer"].unique())
df_new_accounts = df_curr_open[~df_curr_open["Customer"].isin(prev_customer_ids)]

new_accounts_count = len(df_new_accounts)
new_accounts_balance = df_new_accounts["Total Balance"].sum()

if not df_new_accounts.empty:
    df_new_formatted = df_new_accounts[
        ["Customer", "Customer Name", "Z-Group", "Credit Analyst", "Total Past Due", "Total Balance"]
    ].rename(columns={"Credit Analyst": "Analyst"})

    st.dataframe(
        df_new_formatted.style.format(
            {"Total Past Due": "${:,.2f}", "Total Balance": "${:,.2f}"}
        ),
        use_container_width=True
    )

    st.info(
        f"New Accounts Impact: Identified {new_accounts_count:,} new open AR accounts in "
        f"{report_period_str} with a combined balance of ${new_accounts_balance:,.2f}."
    )
else:
    df_new_formatted = pd.DataFrame()
    st.info(f"No new open AR accounts identified for {report_period_str}.")

st.write("---")


# ============================================================
# 20. UNASSIGNED ACCOUNTS
# ============================================================

st.subheader("⚠️ Unassigned Accounts")
st.markdown(
    f"These are **{report_period_str}** accounts with an open balance where "
    f"**BOTH Z-Group and Credit Analyst are empty or unassigned**."
)

zgroup_invalid_mask = df_curr_open["Z-Group"].astype(str).str.strip().str.upper().isin(INVALID_ZGROUP_STATES)
analyst_invalid_mask = df_curr_open["Credit Analyst"].astype(str).str.strip().str.upper().isin(INVALID_ANALYST_STATES)

df_unassigned = df_curr_open[zgroup_invalid_mask & analyst_invalid_mask]

unassigned_count = len(df_unassigned)
unassigned_balance_sum = df_unassigned["Total Balance"].sum()

if not df_unassigned.empty:
    df_unassigned_formatted = df_unassigned[
        ["Customer", "Customer Name", "Status", "Z-Group", "Credit Analyst", "Total Past Due", "Total Balance"]
    ].rename(columns={"Credit Analyst": "Assigned Status"})

    st.dataframe(
        df_unassigned_formatted.style.format(
            {"Total Past Due": "${:,.2f}", "Total Balance": "${:,.2f}"}
        ),
        use_container_width=True
    )

    st.info(
        f"Total Exposure Unassigned: There are {unassigned_count:,} accounts in {report_period_str} "
        f"with open balance missing BOTH Z-Group and Credit Analyst (${unassigned_balance_sum:,.2f})."
    )
else:
    df_unassigned_formatted = pd.DataFrame()
    st.info(f"Great! No active open-balance accounts unassigned in {report_period_str}.")

st.write("---")


# ============================================================
# 21. ANALYST PORTFOLIO DISTRIBUTION
# ============================================================

st.subheader("👥 Analyst Portfolio Distribution & Monthly Variation")

prev_valid_analysts = df_prev_global[
    ~df_prev_global["Credit Analyst"].astype(str).str.strip().str.upper().isin(INVALID_ANALYST_STATES)
]
curr_valid_analysts = df_curr_global[
    ~df_curr_global["Credit Analyst"].astype(str).str.strip().str.upper().isin(INVALID_ANALYST_STATES)
]

prev_total_all = prev_valid_analysts.groupby("Credit Analyst").agg(Total_Prev_All=("Customer", "count")).reset_index()
curr_total_all = curr_valid_analysts.groupby("Credit Analyst").agg(Total_Curr_All=("Customer", "count")).reset_index()

prev_open_active = prev_valid_analysts[(prev_valid_analysts["Total Balance"] != 0) & (prev_valid_analysts["Status"].str.upper().eq("ACTIVE"))]
curr_open_active = curr_valid_analysts[(curr_valid_analysts["Total Balance"] != 0) & (curr_valid_analysts["Status"].str.upper().eq("ACTIVE"))]

prev_open_active_dist = prev_open_active.groupby("Credit Analyst").agg(Open_AR_Prev_Active=("Customer", "count")).reset_index()
curr_open_active_dist = curr_open_active.groupby("Credit Analyst").agg(
    Open_AR_Curr_Active=("Customer", "count"),
    Sum_Past_Due=("Total Past Due", "sum"),
    Sum_Balance=("Total Balance", "sum")
).reset_index()

df_dist_merged = pd.merge(curr_open_active_dist, prev_open_active_dist, on="Credit Analyst", how="outer")
df_dist_merged = pd.merge(df_dist_merged, curr_total_all, on="Credit Analyst", how="outer")
df_dist_merged = pd.merge(df_dist_merged, prev_total_all, on="Credit Analyst", how="outer")

for col in ["Open_AR_Prev_Active", "Open_AR_Curr_Active", "Total_Curr_All", "Total_Prev_All", "Sum_Past_Due", "Sum_Balance"]:
    if col in df_dist_merged.columns:
        df_dist_merged[col] = pd.to_numeric(df_dist_merged[col], errors="coerce").fillna(0)

df_dist_merged["Account_Diff"] = df_dist_merged["Open_AR_Curr_Active"] - df_dist_merged["Open_AR_Prev_Active"]

prev_counts = df_dist_merged["Open_AR_Prev_Active"]
curr_counts = df_dist_merged["Open_AR_Curr_Active"]

pct_change = np.where(
    prev_counts > 0,
    ((curr_counts - prev_counts) / prev_counts * 100),
    np.nan
)

df_dist_merged["Open AR % Change"] = [
    f"{val:+.2f}%" if not np.isnan(val) else ("New (+100%)" if curr > 0 else "0.00%")
    for val, curr in zip(pct_change, curr_counts)
]

df_dist_merged = df_dist_merged.sort_values(by="Open_AR_Curr_Active", ascending=False)

df_dist_final = df_dist_merged[
    [
        "Credit Analyst",
        "Total_Prev_All",
        "Total_Curr_All",
        "Open_AR_Prev_Active",
        "Open_AR_Curr_Active",
        "Open AR % Change",
        "Sum_Past_Due",
        "Sum_Balance"
    ]
].rename(
    columns={
        "Total_Prev_All": "Prev Accounts (All)",
        "Total_Curr_All": "Curr Accounts (All)",
        "Open_AR_Prev_Active": "Prev Acc Open AR",
        "Open_AR_Curr_Active": "Curr Acc Open AR",
        "Sum_Past_Due": "Total Past Due",
        "Sum_Balance": "Total Balance"
    }
)

st.dataframe(
    df_dist_final.style.format(
        {
            "Prev Accounts (All)": "{:,.0f}",
            "Curr Accounts (All)": "{:,.0f}",
            "Prev Acc Open AR": "{:,.0f}",
            "Curr Acc Open AR": "{:,.0f}",
            "Total Past Due": "${:,.2f}",
            "Total Balance": "${:,.2f}"
        }
    ),
    use_container_width=True
)

st.write("---")


# ============================================================
# 22. EXECUTIVE SUMMARY
# ============================================================

st.subheader(f"📋 Executive Summary & Insights ({report_period_str})")

if not df_dist_merged.empty:
    top_vol_row = df_dist_merged.loc[df_dist_merged["Open_AR_Curr_Active"].idxmax()]
    top_vol_analyst = top_vol_row["Credit Analyst"]
    top_vol_count = int(top_vol_row["Open_AR_Curr_Active"])

    top_exp_row = df_dist_merged.loc[df_dist_merged["Sum_Balance"].idxmax()]
    top_exp_analyst = top_exp_row["Credit Analyst"]
    top_exp_balance = top_exp_row["Sum_Balance"]
else:
    top_vol_analyst = "N/A"
    top_vol_count = 0
    top_exp_analyst = "N/A"
    top_exp_balance = 0


# ============================================================
# 23. LOST ACCOUNTS
# ============================================================

account_match_prev = df_prev_global[["Customer", "Credit Analyst"]]
account_match_curr = df_curr_global[["Customer", "Credit Analyst", "Total Balance"]]

df_account_match = pd.merge(
    account_match_prev,
    account_match_curr,
    on="Customer",
    suffixes=("_Prev", "_Curr"),
    how="inner"
)

df_account_match["Credit Analyst_Prev"] = df_account_match["Credit Analyst_Prev"].fillna("").astype(str).str.strip()
df_account_match["Credit Analyst_Curr"] = df_account_match["Credit Analyst_Curr"].fillna("").astype(str).str.strip()

df_lost_accounts = df_account_match[
    (~df_account_match["Credit Analyst_Prev"].str.upper().isin(INVALID_ANALYST_STATES))
    & (df_account_match["Credit Analyst_Prev"] != df_account_match["Credit Analyst_Curr"])
]

lost_summary = df_lost_accounts.groupby("Credit Analyst_Prev").agg(
    Lost_Count=("Customer", "count"),
    Lost_Balance_Current=("Total Balance", "sum")
).reset_index()

if not lost_summary.empty:
    max_lost_row = lost_summary.loc[lost_summary["Lost_Count"].idxmax()]
    lost_analyst = max_lost_row["Credit Analyst_Prev"]
    accounts_lost = int(max_lost_row["Lost_Count"])
    lost_balance_real = max_lost_row["Lost_Balance_Current"]
else:
    lost_analyst = "N/A"
    accounts_lost = 0
    lost_balance_real = 0


# ============================================================
# 24. SUMMARY DISPLAY
# ============================================================

col_summary, col_notes = st.columns([2, 1])

with col_summary:
    summary_text = f"""
- **Workload Leader:** **{top_vol_analyst}** manages the highest volume of active clients with **{top_vol_count:,}** accounts.
- **Risk Exposure Leader:** **{top_exp_analyst}** holds the highest portfolio risk exposure totaling **${top_exp_balance:,.2f}** in Total Balance.
"""
    if accounts_lost > 0:
        summary_text += f"- **Highest Account Reduction:** **{lost_analyst}** had **{accounts_lost:,}** accounts removed from their portfolio in **{report_period_str}**, representing **${lost_balance_real:,.2f}** in Total Balance.\n"
    else:
        summary_text += f"- **Highest Account Reduction:** No active analysts experienced account removals in **{report_period_str}**.\n"

    summary_text += f"""
- **New Clients Added:** Identified **{new_accounts_count:,}** brand-new client accounts in **{report_period_str}**, representing **${new_accounts_balance:,.2f}** in open balance.
- **Unassigned Portfolio:** There are **{unassigned_count:,}** unassigned accounts missing both Z-Group and Credit Analyst, representing **${unassigned_balance_sum:,.2f}**.
"""
    st.markdown(summary_text)

with col_notes:
    if unassigned_count > 0:
        st.info(
            f"⚠️ **Action Required:** Review and assign analyst ownership to the "
            f"**{unassigned_count:,} unassigned accounts** as soon as possible "
            f"(${unassigned_balance_sum:,.2f} exposure)."
        )
    else:
        st.info(
            f"✅ **Outstanding:** All active open-balance accounts have assigned "
            f"analysts in {report_period_str}."
        )


# ============================================================
# 25. HTML REPORT
# ============================================================

st.write("---")
st.subheader("📥 Export & Download Report")


def render_html_table(df, currency_cols=None):
    if df is None or df.empty:
        return '<div class="alert-box">No records available.</div>'

    df_display = df.copy()
    if currency_cols:
        for col in currency_cols:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(
                    lambda x: f"${x:,.2f}" if isinstance(x, (int, float, np.number)) else x
                )

    headers = "".join([f"<th>{col}</th>" for col in df_display.columns])
    
    rows = ""
    for _, row in df_display.iterrows():
        cells = "".join([f"<td>{val}</td>" for val in row])
        rows += f"<tr>{cells}</tr>\n"

    return f"""
    <div class="table-scroll-container">
        <table class="styled-table">
            <thead>
                <tr>{headers}</tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
    """


def build_html_report_data():
    logo_html = ""
    if logo_file and os.path.exists(logo_file):
        import base64
        ext = logo_file.split(".")[-1]
        with open(logo_file, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            logo_html = f'<img src="data:image/{ext};base64,{encoded_string}" style="width: 240px; margin-bottom: 15px;" />'
    else:
        logo_html = '<h1 style="color: #011e6a; margin: 0; font-size: 32px; font-weight: 800;">AMRIZE</h1>'

    html_transitions = render_html_table(df_changes_formatted, ["Total Past Due", "Total Balance"])
    html_new_accounts = render_html_table(df_new_formatted, ["Total Past Due", "Total Balance"])
    html_unassigned = render_html_table(df_unassigned_formatted, ["Total Past Due", "Total Balance"])
    html_distribution = render_html_table(df_dist_final, ["Total Past Due", "Total Balance"])

    # Transición alert text
    if not df_analyst_changes.empty:
        trans_alert = f"💰 <strong>Financial Impact of Assignments:</strong> Identified <strong>{transferred_count:,}</strong> accounts transferred between valid analysts for {report_period_str}, representing <strong>${transferred_balance:,.2f}</strong> in Total Balance and <strong>${transferred_past_due:,.2f}</strong> in Total Past Due."
    else:
        trans_alert = f"✅ No credit analyst assignment transitions were detected between valid analysts for {report_period_str}."

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Amrize - Z-Groups Tracker Elevate ({report_period_str})</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background-color: #f8fafc;
    color: #1e293b;
    margin: 0;
    padding: 40px;
}}

.header-container {{
    margin-bottom: 25px;
}}

.main-title {{
    font-size: 28px;
    font-weight: 800;
    color: #011e6a;
    margin-top: 5px;
    margin-bottom: 12px;
}}

.period-badge {{
    display: inline-block;
    background: #f0f5ff;
    color: #011e6a;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 13.5px;
    border: 1px solid #93c5fd;
    margin-bottom: 25px;
}}

.kpi-container {{
    display: flex;
    gap: 20px;
    margin-bottom: 35px;
}}

.kpi-card {{
    flex: 1;
    background: #f0f5ff;
    border: 1px solid #dbeafe;
    border-left: 6px solid #2563eb;
    padding: 22px;
    border-radius: 12px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}}

.kpi-title {{
    font-size: 12px;
    color: #334155;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.kpi-value {{
    font-size: 32px;
    font-weight: 800;
    color: #001fbe;
    margin-top: 8px;
}}

.section-title {{
    font-size: 20px;
    font-weight: 700;
    color: #011e6a;
    margin: 35px 0 6px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}}

.section-desc {{
    font-size: 13.5px;
    color: #64748b;
    margin-bottom: 15px;
}}

.alert-box {{
    background-color: #e0f2fe;
    border: 1px solid #7dd3fc;
    border-left: 6px solid #0284c7;
    padding: 14px 20px;
    color: #0369a1;
    border-radius: 10px;
    font-weight: 500;
    font-size: 14px;
    margin-top: 12px;
    margin-bottom: 25px;
}}

.search-box {{
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 13.5px;
    color: #64748b;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}}

.table-scroll-container {{
    max-height: 420px;
    overflow-y: auto;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    background: white;
    margin-bottom: 8px;
}}

.styled-table {{
    width: 100%;
    border-collapse: collapse;
    background: white;
}}

.styled-table th {{
    position: sticky;
    top: 0;
    background-color: #011e6a;
    color: white;
    font-weight: 700;
    font-size: 13px;
    padding: 12px 14px;
    text-align: left;
    border-right: 1px solid #1e3a8a;
    z-index: 2;
}}

.styled-table td {{
    padding: 11px 14px;
    text-align: left;
    font-size: 13px;
    border-bottom: 1px solid #e2e8f0;
    border-right: 1px solid #f1f5f9;
    color: #1e293b;
}}

.styled-table tr:nth-child(even) {{
    background-color: #f8fafc;
}}

.styled-table tr:hover {{
    background-color: #f1f5f9;
}}

.insights-card {{
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 24px;
    margin-top: 15px;
    display: flex;
    gap: 25px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}}

.insights-left {{
    flex: 2;
}}

.insights-right {{
    flex: 1;
}}

.insights-list {{
    list-style: none;
    padding: 0;
    margin: 0;
}}

.insights-list li {{
    font-size: 14.5px;
    line-height: 1.8;
    margin-bottom: 10px;
    color: #334155;
}}

</style>
</head>
<body>

<div class="header-container">
    {logo_html}
    <div class="main-title">Z-Groups Tracker Elevate</div>
    <div class="period-badge">📅 Active Report Period: <strong>{report_period_str}</strong></div>
</div>

<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-title">Active Accounts (Previous Month)</div>
        <div class="kpi-value">{prev_active_count:,}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Active Accounts ({report_period_str})</div>
        <div class="kpi-value">{curr_active_count:,}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Total Active Balance ({report_period_str})</div>
        <div class="kpi-value">${total_balance_active_curr:,.2f}</div>
    </div>
</div>

<div class="section-title">🔄 Credit Analyst Assignment Transitions</div>
<div class="section-desc">These are the accounts that transitioned strictly from one specific credit analyst to another (excluding unassigned states or None).</div>
{html_transitions}
<div class="alert-box">{trans_alert}</div>

<div class="section-title">✨ New Accounts of the Month</div>
<div class="section-desc">These are new active accounts identified in <strong>{report_period_str}</strong> with open AR that did not exist in the previous month report.</div>
{html_new_accounts}
<div class="alert-box"><strong>New Accounts Impact:</strong> Identified <strong>{new_accounts_count:,}</strong> new open AR accounts in <strong>{report_period_str}</strong> with a combined balance of <strong>${new_accounts_balance:,.2f}</strong>.</div>

<div class="section-title">⚠️ Unassigned Accounts</div>
<div class="section-desc">These are <strong>{report_period_str}</strong> accounts with an open balance where BOTH Z-Group and Credit Analyst are empty or unassigned.</div>
{html_unassigned}
<div class="alert-box"><strong>Total Exposure Unassigned:</strong> There are <strong>{unassigned_count:,}</strong> accounts in <strong>{report_period_str}</strong> with open balance missing BOTH Z-Group and Credit Analyst, representing a total of <strong>${unassigned_balance_sum:,.2f}</strong>.</div>

<div class="section-title">👥 Analyst Portfolio Distribution</div>
<div class="search-box">🔍 Search/Filter table by Analyst or Values...</div>
{html_distribution}

<div class="section-title">📋 Executive Summary & Insights ({report_period_str})</div>
<div class="insights-card">
    <div class="insights-left">
        <ul class="insights-list">
            <li>• <strong>Workload Leader:</strong> <strong>{top_vol_analyst}</strong> manages the highest volume of active clients with <strong>{top_vol_count:,}</strong> accounts.</li>
            <li>• <strong>Risk Exposure Leader:</strong> <strong>{top_exp_analyst}</strong> holds the highest portfolio risk exposure totaling <strong>${top_exp_balance:,.2f}</strong> in Total Balance.</li>
            {"<li>• <strong>Highest Account Reduction:</strong> <strong>" + str(lost_analyst) + "</strong> had <strong>" + f"{accounts_lost:,}" + "</strong> accounts removed representing <strong>$" + f"{lost_balance_real:,.2f}" + "</strong>.</li>" if accounts_lost > 0 else "<li>• <strong>Highest Account Reduction:</strong> No active analysts experienced account removals in " + report_period_str + ".</li>"}
            <li>• <strong>New Clients Added:</strong> Identified <strong>{new_accounts_count:,}</strong> brand-new client accounts in <strong>{report_period_str}</strong>, representing <strong>${new_accounts_balance:,.2f}</strong> in open balance.</li>
            <li>• <strong>Unassigned Portfolio:</strong> There are <strong>{unassigned_count:,}</strong> unassigned accounts missing both Z-Group and Credit Analyst, representing <strong>${unassigned_balance_sum:,.2f}</strong>.</li>
        </ul>
    </div>
    <div class="insights-right">
        {"<div class='alert-box' style='margin:0;'>⚠️ <strong>Action Required:</strong> Review unassigned accounts.</div>" if unassigned_count > 0 else "<div class='alert-box' style='margin:0;'>✅ <strong>Outstanding:</strong> All active open-balance accounts have assigned analysts.</div>"}
    </div>
</div>

</body>
</html>"""


st.download_button(
    label="📄 Download Report as HTML",
    data=build_html_report_data(),
    file_name=f"Z_Groups_Report_{selected_month}_{selected_year}.html",
    mime="text/html"
)