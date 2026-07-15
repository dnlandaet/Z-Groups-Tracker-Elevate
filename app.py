import streamlit as st
import pandas as pd
import os

# 1. Page Configuration
st.set_page_config(
    page_title="Amrize - Z-Groups Tracker Elevate",
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

# --- HEADER LAYOUT (LOGO ON TOP, TITLE BELOW) ---
if logo_file:
    st.image(logo_file, width=280)
else:
    st.info("⚠️ Place 'Amrize_Logo_2025.svg' or 'logo.png' in your project folder.")

st.title("Z-Groups Tracker Elevate")
st.markdown("Upload your comparative monthly files below to track analyst changes and overall portfolio movement.")

# --- STEP 1: FILE UPLOADER ---
st.sidebar.header("Data Source Upload")
prev_file = st.sidebar.file_uploader("Upload PREVIOUS MONTH file (Excel)", type=["xlsx", "xls"])
curr_file = st.sidebar.file_uploader("Upload CURRENT MONTH file (Excel)", type=["xlsx", "xls"])

if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.rerun()

# File Check Warning
if not prev_file or not curr_file:
    st.info("💡 Please upload both previous and current month Excel files in the sidebar to generate the comparison analysis.")
else:
    # --- STEP 2: READ AND CLEAN DATA ---
    try:
        df_prev = pd.read_excel(prev_file)
        df_curr = pd.read_excel(curr_file)
    except Exception as e:
        st.error(f"Error reading Excel files: {e}")
        st.stop()

    # Required Columns Validation
    required_cols = ["Customer", "Customer Name", "Z-Group", "Credit Analyst", "Total Past Due", "Total Balance"]
    
    if not all(col in df_prev.columns for col in required_cols) or not all(col in df_curr.columns for col in required_cols):
        st.error(f"Error: Make sure both files contain exactly these columns: {', '.join(required_cols)}")
        st.stop()

    # Data Cleaning Function (excl. Nulls, "Not Found", 0)
    def clean_data(df):
        df_clean = df.copy()
        
        # Remove records containing "NOT FOUND" in Total Balance
        df_clean = df_clean[
            df_clean["Total Balance"].astype(str).str.strip().str.upper() != "NOT FOUND"
        ]
        
        # Convert Customer column to integer (removing decimals) and then to string safely
        df_clean["Customer"] = pd.to_numeric(df_clean["Customer"], errors='coerce').fillna(0).astype(int).astype(str)
        
        # Convert numeric columns safely to floats
        df_clean["Total Balance"] = pd.to_numeric(df_clean["Total Balance"], errors='coerce')
        df_clean["Total Past Due"] = pd.to_numeric(df_clean["Total Past Due"], errors='coerce')
        
        # Fill missing values with zero
        df_clean["Total Balance"] = df_clean["Total Balance"].fillna(0)
        df_clean["Total Past Due"] = df_clean["Total Past Due"].fillna(0)
        
        return df_clean

    df_prev_clean = clean_data(df_prev)
    df_curr_clean = clean_data(df_curr)

    # Filter out records where Total Balance is strictly non-zero (Open Balances)
    df_prev_open = df_prev_clean[df_prev_clean["Total Balance"] != 0]
    df_curr_open = df_curr_clean[df_curr_clean["Total Balance"] != 0]

    # --- STEP 3: METRICS AND COMPARATIVE INDICATORS ---
    prev_count = len(df_prev_open)
    curr_count = len(df_curr_open)
    
    # Calculate % Variation
    if prev_count > 0:
        variation = ((curr_count - prev_count) / prev_count) * 100
        variation_str = f"{variation:+.2f}%"
    else:
        variation_str = "N/A (No previous month accounts)"

    st.subheader("📌 General Portfolio Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Open Balance Accounts (Previous Month)", 
            value=f"{prev_count:,}"
        )
    with col2:
        st.metric(
            label="Open Balance Accounts (Current Month)", 
            value=f"{curr_count:,}", 
            delta=variation_str
        )
    with col3:
        total_balance_curr = df_curr_open["Total Balance"].sum()
        st.metric(
            label="Total Active Balance (Current Month)", 
            value=f"${total_balance_curr:,.2f}"
        )

    st.write("---")

    # --- STEP 4: TRANSITION TABLE (STRICT ANALYST-TO-ANALYST CHANGES) ---
    st.subheader("🔄 Credit Analyst Assignment Transitions")
    st.markdown("These are the accounts that transitioned strictly **from one specific credit analyst to another** (excluding brand new accounts or previously unassigned accounts).")

    # Merge dataframes on Customer
    df_comparison = pd.merge(
        df_prev_clean[["Customer", "Credit Analyst", "Total Past Due", "Total Balance"]],
        df_curr_clean[["Customer", "Customer Name", "Credit Analyst", "Total Past Due", "Total Balance"]],
        on="Customer",
        suffixes=("_Previous", "_Current")
    )

    # Convert Analyst names to string and clean spaces
    df_comparison["Credit Analyst_Previous"] = df_comparison["Credit Analyst_Previous"].astype(str).str.strip()
    df_comparison["Credit Analyst_Current"] = df_comparison["Credit Analyst_Current"].astype(str).str.strip()

    # Define invalid analyst states to filter out
    invalid_states = ["NOT FOUND", "NO CREDIT ANALYST ASSIGNED.", "NAN", "", "NONE", "UNASSIGNED"]

    # Filter strictly analyst-to-analyst changes
    df_analyst_changes = df_comparison[
        (df_comparison["Credit Analyst_Previous"] != df_comparison["Credit Analyst_Current"]) &
        (~df_comparison["Credit Analyst_Previous"].str.upper().isin(invalid_states)) &
        (~df_comparison["Credit Analyst_Current"].str.upper().isin(invalid_states))
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
            "Total Past Due_Current": "Current Total Past Due",
            "Total Balance_Current": "Current Total Balance"
        })

        # Render styled dataframe with currency formatting
        st.dataframe(
            df_changes_formatted.style.format({
                "Current Total Past Due": "${:,.2f}",
                "Current Total Balance": "${:,.2f}"
            }),
            use_container_width=True
        )
        
        # Financial summary of transitions
        transferred_past_due = df_analyst_changes["Total Past Due_Current"].sum()
        transferred_balance = df_analyst_changes["Total Balance_Current"].sum()
        
        st.info(
            f"💰 **Financial Impact of Assignments:** Transferred accounts represent a total of "
            f"**${transferred_balance:,.2f}** in Total Balance and **${transferred_past_due:,.2f}** in Total Past Due."
        )
    else:
        st.success("✅ No credit analyst assignment transitions were detected between valid analysts.")

    st.write("---")

    # --- NEW SECTION: UNASSIGNED ACCOUNTS WITH OPEN BALANCE ---
    st.subheader("⚠️ Unassigned Accounts (Current Month)")
    st.markdown("These are current month accounts with an **open balance** that do not have an active Credit Analyst assigned (contains 'No Credit Analyst Assigned.', 'Not Found', or blank fields).")

    # Filter unassigned accounts in the current month open balance data
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
            "Total Past Due": "Total Past Due (Actual)",
            "Total Balance": "Total Balance (Actual)"
        })

        st.dataframe(
            df_unassigned_formatted.style.format({
                "Total Past Due (Actual)": "${:,.2f}",
                "Total Balance (Actual)": "${:,.2f}"
            }),
            use_container_width=True
        )

        unassigned_balance_sum = df_unassigned["Total Balance"].sum()
        st.warning(
            f"🚨 **Total Exposure Unassigned:** There are **{unassigned_count}** accounts with open balance currently without an analyst, "
            f"representing a total of **${unassigned_balance_sum:,.2f}**."
        )
    else:
        st.success("✅ Great! Every active open-balance account has an analyst assigned for the current month.")

    st.write("---")

    # --- STEP 5: CURRENT MONTH ANALYST DISTRIBUTION ---
    st.subheader("👥 Analyst Portfolio Distribution (Current Month)")
    st.markdown("Breakdown of active, open-balance accounts (excluding 'Not Found' and unassigned) currently assigned to each active credit analyst.")

    # Filter out unassigned accounts from analyst statistics to keep active team clean
    df_curr_open_assigned = df_curr_open[
        ~df_curr_open["Credit Analyst"].astype(str).str.strip().str.upper().isin(invalid_states)
    ]

    df_analyst_distribution = df_curr_open_assigned.groupby("Credit Analyst").agg(
        Account_Count=("Customer", "count"),
        Sum_Past_Due=("Total Past Due", "sum"),
        Sum_Balance=("Total Balance", "sum")
    ).reset_index()

    df_analyst_distribution = df_analyst_distribution.sort_values(by="Account_Count", ascending=False)

    df_analyst_distribution_formatted = df_analyst_distribution.rename(columns={
        "Credit Analyst": "Credit Analyst",
        "Account_Count": "Account Count",
        "Sum_Past_Due": "Accumulated Total Past Due",
        "Sum_Balance": "Accumulated Total Balance"
    })

    st.dataframe(
        df_analyst_distribution_formatted.style.format({
            "Account Count": "{:,}",
            "Accumulated Total Past Due": "${:,.2f}",
            "Accumulated Total Balance": "${:,.2f}"
        }),
        use_container_width=True
    )

    st.write("---")

    # --- NEW SECTION: EXECUTIVE SUMMARY (SUMMARY BOX) ---
    st.subheader("📋 Executive Summary & Insights")
    
    # 1. Calculate critical distribution variables dynamically
    if not df_analyst_distribution.empty:
        # Analyst with the most accounts
        top_account_analyst_row = df_analyst_distribution.loc[df_analyst_distribution["Account_Count"].idxmax()]
        top_acc_analyst = top_account_analyst_row["Credit Analyst"]
        top_acc_count = top_account_analyst_row["Account_Count"]

        # Analyst with the most total balance (exposure)
        top_exposure_analyst_row = df_analyst_distribution.loc[df_analyst_distribution["Sum_Balance"].idxmax()]
        top_exp_analyst = top_exposure_analyst_row["Credit Analyst"]
        top_exp_balance = top_exposure_analyst_row["Sum_Balance"]
    else:
        top_acc_analyst, top_acc_count = "N/A", 0
        top_exp_analyst, top_exp_balance = "N/A", 0

    # 2. Calculate ratios
    unassigned_ratio = (unassigned_balance_sum / total_balance_curr * 100) if total_balance_curr > 0 else 0

    # Render clean bullet-point list
    col_summary, col_notes = st.columns([2, 1])

    with col_summary:
        st.markdown(f"""
        * 📊 **Workload Leader:** **{top_acc_analyst}** currently manages the largest volume of active clients with **{top_acc_count} accounts**.
        * 📈 **Risk Exposure Leader:** **{top_exp_analyst}** holds the highest portfolio exposure under management, totaling **${top_exp_balance:,.2f}** in Total Balance.
        * 🔄 **Transitional Exposure:** A total of **${transferred_balance:,.2f}** (and **${transferred_past_due:,.2f}** in Past Due) has shifted analyst responsibility this month.
        * ⚠️ **Unassigned Portfolio:** There are **{unassigned_count} unassigned accounts**, representing **{unassigned_ratio:.2f}%** of the total open balance (**${unassigned_balance_sum:,.2f}**).
        """)
        
    with col_notes:
        # Action Item Highlight Box
        if unassigned_count > 0:
            st.warning(f"💡 **Action Required:** We recommend reviewing and assigning the **{unassigned_count} unassigned accounts** immediately to minimize portfolio risk of **${unassigned_balance_sum:,.2f}**.")
        else:
            st.success("🎉 **Outstanding!** The entire credit team is fully assigned. No unattended portfolio balances detected this month.")