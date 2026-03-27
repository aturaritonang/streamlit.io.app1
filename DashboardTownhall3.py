import streamlit as st 
import pandas as pd
import altair as alt
import gspread
from google.oauth2.service_account import Credentials

# st.markdown("""
#     <style>
#     .stDataFrame td {
#         white-space: normal !important;
#         word-wrap: break-word !important;
#     }
#     .stDataFrame th {
#         white-space: normal !important;
#         word-wrap: break-word !important;
#     }
#     </style>
# """, unsafe_allow_html=True)

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

dfQuiz = pd.DataFrame(client.open("Master Quiz").worksheet("Trial-Id").get_all_records())


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

answer_cols_alpabet = ["A", "B", "C", "D", "E"]

# Convert TRUE/FALSE → 1/0
df[answer_cols] = df[answer_cols].replace({
    "TRUE": 1,
    "FALSE": 0,
    True: 1,
    False: 0
})

# =====================
# PER QUIZ CHART
# =====================
quiz_list = df["Quiz"].unique()

for quiz in quiz_list:
    st.text(f"Quiz: {quiz}")
    
    quiz_df = df[df["Quiz"] == quiz]

    master_quiz_df = dfQuiz[dfQuiz["Quiz"] == quiz]

    totals = quiz_df[answer_cols].sum().reset_index()
    totals.columns = ["Level", "Answer"]

    # Ensure order tetap
    totals["Level"] = pd.Categorical(totals["Level"], categories=answer_cols, ordered=True)
    totals = totals.sort_values("Level")

    # =====================
    # CHART
    # =====================
    chart = alt.Chart(totals).mark_bar().encode(
        x=alt.X("Level:N", sort=answer_cols, title="Level"),
        y=alt.Y("Answer:Q", title="Total"),
        color=alt.Color("Level:N", legend=None)
    ).properties(height=300)

    st.altair_chart(chart, use_container_width=True)

    # =====================
    # TABLE (Level vs Answer)
    # =====================
    newTotals = totals
    # newTotals["Level"] = master_quiz_df[newTotals["Level:N"]]
    # st.text(newTotals["Level"].iloc[0])
    # newTotals["Level"] = master_quiz_df[newTotals["Level"].iloc[0]]
    # st.dataframe(master_quiz_df, use_container_width=True, hide_index=True)
    # st.dataframe(master_quiz_df["5 Role Model"], use_container_width=True, hide_index=True)

    newTotals["Level"] = newTotals["Level"].apply(
        lambda L: L + ":\n" + master_quiz_df.iloc[0][L] if L in master_quiz_df.columns else ""
    )
    
    # st.dataframe(newTotals, use_container_width=False, hide_index=True)
    st.table(newTotals.reset_index(drop=True))

    st.markdown("---")

# =====================
# TOTAL KESELURUHAN
# =====================
st.header("Total Overall")

totals_all = df[answer_cols].sum().reset_index()
totals_all.columns = ["Level", "Answer"]

totals_all["Level"] = pd.Categorical(totals_all["Level"], categories=answer_cols, ordered=True)
totals_all = totals_all.sort_values("Level")

chart_all = alt.Chart(totals_all).mark_bar().encode(
    x=alt.X("Level:N", sort=answer_cols, title="Level"),
    y=alt.Y("Answer:Q", title="Total"),
    color=alt.Color("Level:N", legend=None)
).properties(height=400)

st.altair_chart(chart_all, use_container_width=True)

st.dataframe(totals_all, use_container_width=True, hide_index=True)

# =====================
# RAW DATA
# =====================
# with st.expander("See Raw Data"):
#     st.dataframe(df)