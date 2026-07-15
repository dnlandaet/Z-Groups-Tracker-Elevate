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
# Use the official raw URL from Wikimedia upload servers to bypass hotlinking protection
logo_url = "https://upload.wikimedia.org/wikipedia/commons/c/cd/Amrize_Logo_2025.svg"

# Header columns structure (Adjust width ratio for better alignment)
col_logo, col_title = st.columns([1, 5])
with col_logo:
    # Use HTML wrapper to ensure perfect loading and centering
    st.markdown(f'<img src="{logo_url}" width="160" style="margin-top: 10px;">', unsafe_allow_html=True)
with col_title:
    st.title("Credit & Portfolio Control Dashboard")

st.markdown("Upload your comparative monthly files below to track analyst changes and overall portfolio movement.")

# --- STEP 1: FILE UPLOADER ---
st.sidebar.header("Data Source Upload")
prev_file = st.sidebar.file_uploader("Upload PREVIOUS MONTH file (Excel)", type=["xlsx", "xls"])
curr_file = st.sidebar.file_uploader("Upload CURRENT MONTH file (Excel)", type=["xlsx", "xls"])

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

    # --- STEP 4: TRANSITION TABLE (ANALYST CHANGE TRACKER) ---
    st.subheader("🔄 Credit Analyst Assignment Transitions")
    st.markdown("These are the accounts that changed credit analysts between the previous and current month, displaying their current exposure.")

    # Merge dataframes using 'Customer' ID
    df_comparison = pd.merge(
        df_prev_clean[["Customer", "Credit Analyst", "Total Past Due", "Total Balance"]],
        df_curr_clean[["Customer", "Customer Name", "Credit Analyst", "Total Past Due", "Total Balance"]],
        on="Customer",
        suffixes=("_Previous", "_Current")
    )

    # Filter where credit analyst assignments differ
    df_analyst_changes = df_comparison[
        df_comparison["Credit Analyst_Previous"] != df_comparison["Credit Analyst_Current"]
    ]

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
        
        # Financial summary of transferred portfolio
        transferred_past_due = df_analyst_changes["Total Past Due_Current"].sum()
        transferred_balance = df_analyst_changes["Total Balance_Current"].sum()
        
        st.info(
            f"💰 **Financial Impact of Changes:** Transferred accounts represent a total of "
            f"**${transferred_balance:,.2f}** in Total Balance and **${transferred_past_due:,.2f}** in Total Past Due."
        )
    else:
        st.success("✅ No credit analyst assignment transitions were detected between the loaded months.")

    st.write("---")

    # --- STEP 5: CURRENT MONTH ANALYST DISTRIBUTION ---
    st.subheader("👥 Analyst Portfolio Distribution (Current Month)")
    st.markdown("Breakdown of active, open-balance accounts (excluding 'Not Found') currently assigned to each credit analyst.")

    # Group Current Active Month Data by Analyst
    df_analyst_distribution = df_curr_open.groupby("Credit Analyst").agg(
        Account_Count=("Customer", "count"),
        Sum_Past_Due=("Total Past Due", "sum"),
        Sum_Balance=("Total Balance", "sum")
    ).reset_index()

    # Sort descending based on count of accounts
    df_analyst_distribution = df_analyst_distribution.sort_values(by="Account_Count", ascending=False)

    df_analyst_distribution = df_analyst_distribution.rename(columns={
        "Credit Analyst": "Credit Analyst",
        "Account_Count": "Account Count",
        "Sum_Past_Due": "Accumulated Total Past Due",
        "Sum_Balance": "Accumulated Total Balance"
    })

    # Render styled distribution dataframe
    st.dataframe(
        df_analyst_distribution.style.format({
            "Account Count": "{:,}",
            "Accumulated Total Past Due": "${:,.2f}",
            "Accumulated Total Balance": "${:,.2f}"
        }),
        use_container_width=True
    )