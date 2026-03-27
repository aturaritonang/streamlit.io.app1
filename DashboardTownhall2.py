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

sheet = client.open("Result Townhall").sheet1

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
df[answer_cols] = df[answer_cols].replace({
    "TRUE": 1,
    "FALSE": 0,
    True: 1,
    False: 0
})

# =====================
# PER QUIZ
# =====================
quiz_list = df["Quiz"].unique()

for quiz in quiz_list:
    st.text(f"Quiz: {quiz}")

    quiz_df = df[df["Quiz"] == quiz]

    totals = quiz_df[answer_cols].sum().reindex(answer_cols).reset_index()
    totals.columns = ["Answer", "Total"]

    # =====================
    # CHART PER QUIZ
    # =====================
    chart = alt.Chart(totals).mark_bar().encode(
        x=alt.X("Answer:N", sort=answer_cols, title="Answer"),
        y=alt.Y("Total:Q", title="Total"),
        color=alt.Color("Answer:N", legend=None)
    ).properties(height=300)

    st.altair_chart(chart, use_container_width=True)

    # =====================
    # TABLE VERTICAL
    # =====================
    st.table(totals)

    st.divider()

# =====================
# TOTAL KESELURUHAN
# =====================
st.header("Overall Summary")

overall = df[answer_cols].sum().reindex(answer_cols).reset_index()
overall.columns = ["Answer", "Total"]

chart_total = alt.Chart(overall).mark_bar().encode(
    x=alt.X("Answer:N", sort=answer_cols, title="Answer"),
    y=alt.Y("Total:Q", title="Total"),
    color=alt.Color("Answer:N", legend=None)
).properties(height=400)

st.altair_chart(chart_total, use_container_width=True)

st.table(overall)

# =====================
# RAW DATA
# =====================
with st.expander("See Data"):
    st.dataframe(df)