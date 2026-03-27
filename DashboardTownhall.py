import streamlit as st
import pandas as pd
import altair as alt
import gspread
from google.oauth2.service_account import Credentials

st.title("Survey Dashboard")

# =====================
# CONNECT TO GOOGLE SHEET
# =====================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

# Ganti dengan nama Google Sheet kamu
sheet = client.open("Result Townhall").sheet1

# Ambil semua data
data = sheet.get_all_records()
df = pd.DataFrame(data)

# =====================
# DATA CLEANING
# =====================
df.columns = df.columns.str.strip()

answer_cols = [
    "5 Role Model",
    "4 Fully Meets Expectations",
    "3 Partially Meets Expectations",
    "2 Needs Improvement",
    "1 Does Not Meet Expectations"
]

# Convert TRUE/FALSE → 1/0
df[answer_cols] = df[answer_cols].replace({"TRUE": True, "FALSE": False})

# =====================
# AGGREGATION
# =====================
totals = df[answer_cols].sum().reset_index()
totals.columns = ["Answer", "TRUE_Count"]

# =====================
# CHART
# =====================
chart = alt.Chart(totals).mark_bar().encode(
    x=alt.X("Answer:N", title="Answer"),
    y=alt.Y("TRUE_Count:Q", title="TRUE Count"),
    color=alt.Color("Answer:N", legend=None)
).properties(height=400)

st.altair_chart(chart, use_container_width=True)

# =====================
# SHOW DATA
# =====================
with st.expander("See Data"):
    st.dataframe(df)