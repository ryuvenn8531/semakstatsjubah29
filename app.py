import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Page branding
st.set_page_config(
    page_title="STATISTIK PENGAMBILAN JUBAH ISTIADAT KONVOKESYEN ADTEC JTM KALI KE-29 (WILAYAH TENGAH)",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 STATISTIK PENGAMBILAN JUBAH ISTIADAT KONVOKESYEN ADTEC JTM KALI KE-29 (WILAYAH TENGAH)")
st.caption("Dashboard statistik pengambilan jubah")
st.divider()

# 2. Google Sheet URL
sheet_url = "https://docs.google.com/spreadsheets/d/1QqTOt7yCjDXvDbUhZqWG1MbrH-lbFRAZ7aQ70qOxSGw/edit?gid=1445201158#gid=1445201158"

# 3. Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 4. Auto-refresh every 10 minutes via Fragment
@st.fragment(run_every="10m")
def load_and_display_data():
    df = conn.read(spreadsheet=sheet_url, worksheet=0, usecols=[0, 1, 2, 3, 4, 5], ttl=0)

    # Clean column names
    df.columns = ["KAMPUS", "SETUJU_HADIR", "JDA", "JBA", "JDH"]
    df = df.dropna(subset=["KAMPUS"])

    numeric_cols = ["SETUJU_HADIR", "JDA", "JBA", "JDH"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["JDA_PERCENT"] = (df["JDA"] / df["SETUJU_HADIR"]).fillna(0) * 100
    df["JDH_PERCENT"] = (df["JDH"] / df["JDA"]).fillna(0) * 100

    # 5. Top KPI Display
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Setuju Hadir", f"{int(df['SETUJU_HADIR'].sum()):,}")
    col2.metric("Total Jubah Telah Diambil", f"{int(df['JDA'].sum()):,}")
    col3.metric("Total Jubah Belum Diambil", f"{int(df['JBA'].sum()):,}")
    col4.metric("Total Jubah Telah Dipulangkan", f"{int(df['JDH'].sum()):,}")

    st.divider()

    # 6. Table Display
    st.subheader("Jumlah Mengikut Kampus")

    df_display = df.copy()
    df_display["SETUJU_HADIR"] = df_display["SETUJU_HADIR"].apply(lambda x: f"{int(x):,}")
    df_display["JDA"] = df_display["JDA"].apply(lambda x: f"{int(x):,}")
    df_display["JBA"] = df_display["JBA"].apply(lambda x: f"{int(x):,}")
    df_display["JDA_PERCENT"] = df_display["JDA_PERCENT"].apply(lambda x: f"{x:.2f}%")
    df_display["JDH_PERCENT"] = df_display["JDH_PERCENT"].apply(lambda x: f"{x:.2f}%")

    df_display = df_display.rename(columns={
        "KAMPUS": "Kampus / Location",
        "SETUJU_HADIR": "Setuju Hadir",
        "JDA": "Jubah Telah Diambil",
        "JBA": "Jubah Belum Diambil",
        "JDA_PERCENT": "Selesai Ambil Jubah",
        "JDH_PERCENT": "Selesai Pulang Jubah"
    })

    raw_table = df_display.to_html(index=False, classes="custom-centered-table")

    full_html = f"""
    <style>
    .table-container {{
        width: 100%;
        overflow-x: auto;
        margin-top: 10px;
    }}
    .custom-centered-table {{
        width: 100%;
        border-collapse: collapse;
    }}
    .custom-centered-table th, .custom-centered-table td {{
        text-align: center !important;
        padding: 10px;
        border: 1px solid #e6e6e6;
    }}
    .custom-centered-table th {{
        background-color: #f0f2f6;
        font-weight: bold;
    }}
    </style>
    <div class="table-container">
        {raw_table}
    </div>
    """

    # st.html prevents Markdown from converting HTML into plain text code blocks
    st.html(full_html)

# Execute fragment
load_and_display_data()
