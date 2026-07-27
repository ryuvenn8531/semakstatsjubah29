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

# 4. Wrap the display logic in a fragment (Auto-refresh every 10 minutes)
@st.fragment(run_every="10m")
def load_and_display_data():
    # Read data cleanly
    df = conn.read(spreadsheet=sheet_url, worksheet=0, usecols=[0, 1, 2, 3, 4], ttl=0)

    # Clean column names
    df.columns = ["KAMPUS", "SETUJU_HADIR", "TIDAK_HADIR", "JDA", "JBA"]
    df = df.dropna(subset=["KAMPUS"])

    # Convert numeric columns safely
    numeric_cols = ["SETUJU_HADIR", "TIDAK_HADIR", "JDA", "JBA"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Calculate percentage of Column D (JDA) over Column E (JBA)
    df["JDA_PERCENT"] = (df["JDA"] / df["JBA"]).fillna(0) * 100

    # 5. Top Metrics Display
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Setuju Hadir", f"{int(df['SETUJU_HADIR'].sum()):,}")
    col2.metric("Total Tidak Hadir", f"{int(df['TIDAK_HADIR'].sum()):,}")
    col3.metric("Total Jubah Telah Diambil", f"{int(df['JDA'].sum()):,}")
    col4.metric("Total Jubah Belum Diambil", f"{int(df['JBA'].sum()):,}")

    st.divider()

# 6. Center-aligned HTML Table display
    st.subheader("Jumlah Mengikut Kampus")

    # Prepare display dataframe
    df_display = df.copy()

    # Format numbers nicely
    df_display["SETUJU_HADIR"] = df_display["SETUJU_HADIR"].apply(lambda x: f"{int(x):,}")
    df_display["TIDAK_HADIR"] = df_display["TIDAK_HADIR"].apply(lambda x: f"{int(x):,}")
    df_display["JDA"] = df_display["JDA"].apply(lambda x: f"{int(x):,}")
    df_display["JBA"] = df_display["JBA"].apply(lambda x: f"{int(x):,}")
    df_display["JDA_PERCENT"] = df_display["JDA_PERCENT"].apply(lambda x: f"{x:.2f}%")

    # Rename column headers
    df_display = df_display.rename(columns={
        "KAMPUS": "Kampus / Location",
        "SETUJU_HADIR": "Setuju Hadir",
        "TIDAK_HADIR": "Tidak Hadir",
        "JDA": "Jubah Telah Diambil",
        "JBA": "Jubah Belum Diambil",
        "JDA_PERCENT": "Selesai Ambil Jubah"
    })

    # Generate raw HTML table
    raw_table = df_display.to_html(index=False, classes="custom-centered-table")

    # Single HTML string containing both style and table markup
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

    # Render table properly
    st.markdown(full_html, unsafe_allow_html=True)

# 7. Call the fragment function to execute
load_and_display_data()
