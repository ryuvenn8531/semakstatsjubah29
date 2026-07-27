import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Page branding and responsive wide layout
st.set_page_config(
    page_title="jubahstats",
    page_icon="🎓",
    layout="wide"  # Automatically fills available browser width
)

st.title("🎓 jubahstats")
st.caption("Real-time attendance & graduation gown metrics dashboard")
st.divider()

# 2. Paste your Google Sheet URL here
sheet_url = "PASTE_YOUR_PUBLIC_GOOGLE_SHEET_URL_HERE"

# 3. Connect and fetch data with 10-minute cache TTL
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=sheet_url, worksheet=0, usecols=[0, 1, 2, 3, 4], ttl="10m")

# 4. Clean column names
df.columns = ["KAMPUS", "SETUJU_HADIR", "TIDAK_HADIR", "JDA", "JBA"]
df = df.dropna(subset=["KAMPUS"])

# Convert numeric columns safely
numeric_cols = ["SETUJU_HADIR", "TIDAK_HADIR", "JDA", "JBA"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# Calculate percentage of Column D (JDA) over Column E (JBA)
df["JDA_PERCENT"] = (df["JDA"] / df["JBA"]).fillna(0) * 100

# 5. Responsive Metric Summary Cards
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
col1.metric("Total Setuju Hadir", f"{int(df['SETUJU_HADIR'].sum()):,}")
col2.metric("Total Tidak Hadir", f"{int(df['TIDAK_HADIR'].sum()):,}")
col3.metric("Total JDA", f"{int(df['JDA'].sum()):,}")
col4.metric("Total JBA", f"{int(df['JBA'].sum()):,}")

st.divider()

# 6. Responsive HTML Table Display
st.subheader("Campus Breakdowns")

df_display = df.copy()

# Format values cleanly
df_display["SETUJU_HADIR"] = df_display["SETUJU_HADIR"].apply(lambda x: f"{int(x):,}")
df_display["TIDAK_HADIR"] = df_display["TIDAK_HADIR"].apply(lambda x: f"{int(x):,}")
df_display["JDA"] = df_display["JDA"].apply(lambda x: f"{int(x):,}")
df_display["JBA"] = df_display["JBA"].apply(lambda x: f"{int(x):,}")
df_display["JDA_PERCENT"] = df_display["JDA_PERCENT"].apply(lambda x: f"{x:.2f}%")

df_display = df_display.rename(columns={
    "KAMPUS": "Kampus / Location",
    "SETUJU_HADIR": "Setuju Hadir",
    "TIDAK_HADIR": "Tidak Hadir",
    "JDA": "JDA",
    "JBA": "JBA",
    "JDA_PERCENT": "% JDA / JBA"
})

# Generate clean centered HTML table without row index
raw_table = df_display.to_html(index=False, classes="responsive-table")

# Responsive CSS Wrapper
st.markdown(f"""
    <style>
    /* Allows horizontal scrolling on small screens without breaking text layout */
    .table-container {{
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        margin-top: 10px;
    }}
    
    .responsive-table {{
        width: 100%;
        min-width: 600px; /* Prevents cell cramping on small screens */
        border-collapse: collapse;
    }}
    
    .responsive-table th, .responsive-table td {{
        text-align: center !important;
        padding: 12px 8px;
        border: 1px solid #e6e6e6;
        font-size: 0.95rem;
    }}
    
    .responsive-table th {{
        background-color: #f0f2f6;
        font-weight: 600;
    }}
    </style>
    
    <div class="table-container">
        {raw_table}
    </div>
""", unsafe_allow_html=True)
