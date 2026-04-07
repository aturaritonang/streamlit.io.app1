import streamlit as st 
import pandas as pd
import altair as alt
import gspread
from google.oauth2.service_account import Credentials

st.sidebar.title("🏛️ IBMC Townhall Survey")

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

sheet = client.open("Result Townhall").worksheet("Result")
data = sheet.get_all_records()
df = pd.DataFrame(data)

property = client.open("Result Townhall").worksheet("Property")
participants_value = property.cell(2, property.find("Participants").col).value

st.sidebar.header(f"👥 {participants_value} participants")

# st.markdown("---")

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

answer_cols_alpabet = {
    "5 Role Model" : "A", 
    "4 Fully Meets Expectations" : "B", 
    "3 Partially Meets Expectations" : "C", 
    "2 Needs Improvement" : "D", 
    "1 Does Not Meet Expectations" : "E"
}

rating_colors = {
    "5 Role Model": "#0f62fe",
    "4 Fully Meets Expectations": "#44ce1b",
    "3 Partially Meets Expectations": "#f7e379",
    "2 Needs Improvement": "#f2a134",
    "1 Does Not Meet Expectations": "#e51f1f"
}

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

    st.markdown("### ❓Quiz:")
    st.text(f"{quiz}")
    
    quiz_df = df[df["Quiz"] == quiz]

    master_quiz_df = dfQuiz[dfQuiz["Quiz"] == quiz]

    totals = quiz_df[answer_cols].sum().reset_index()
    totals.columns = ["Level", "Total"]

    # Ensure order tetap
    totals["Level"] = pd.Categorical(totals["Level"], categories=answer_cols, ordered=True)
    totals = totals.sort_values("Level")

    totals["Code"] = totals["Level"].map(answer_cols_alpabet)

    # =====================
    # CHART
    # =====================
    # chart = alt.Chart(totals).mark_bar().encode(
    #     # x=alt.X("Level:N", sort=answer_cols, title="Level"),
    #     x=alt.X("Code:N", sort=list(answer_cols_alpabet.values()), title="Code", axis=alt.Axis(labelAngle=0)),
    #     y=alt.Y("Total:Q", title="Total"),
    #     color=alt.Color("Level:N", scale=alt.Scale(
    #         domain=list(rating_colors.keys()),
    #         range=list(rating_colors.values())
    #         ), legend=None),
    #     tooltip=[
    #         alt.Tooltip("Level:N", title="Level"),
    #         # alt.Tooltip("Code:N", title="Code"),
    #         alt.Tooltip("Total:Q", title="Total")
    #     ]
    # ).properties(height=400)

    labels = alt.Chart(totals).mark_text(
        align='center',
        baseline='top',
        dy=5,              # move text upward
        fontSize=18,
        fontWeight="bolder"
    ).encode(
        x="Code:N",
        y="Total:Q",
        text="Total:Q"
    )

    chart = alt.Chart(totals).mark_bar().encode(
        x=alt.X("Code:N",
                sort=list(answer_cols_alpabet.values()),
                title="Code",
                axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Total:Q", title="Total"),
        color=alt.Color(
            "Level:N",
            scale=alt.Scale(
                domain=list(rating_colors.keys()),
                range=list(rating_colors.values())
            ),
            legend=None),
        tooltip=[
            alt.Tooltip("Level:N", title="Level"),
            alt.Tooltip("Total:Q", title="Total")
        ]
    ).properties(height=400)

    final_chart = chart + labels
    st.altair_chart(final_chart, use_container_width=True)

    # =====================
    # TABLE (Level vs Answer)
    # =====================
    newTotals = totals
    # newTotals["Level"] = master_quiz_df[newTotals["Level:N"]]
    # st.text(newTotals["Level"].iloc[0])
    # newTotals["Level"] = master_quiz_df[newTotals["Level"].iloc[0]]
    # st.dataframe(master_quiz_df, use_container_width=True, hide_index=True)
    # st.dataframe(master_quiz_df["5 Role Model"], use_container_width=True, hide_index=True)

    newTotals = newTotals.rename(columns={"Level": "Options"})

    newTotals["Options"] = newTotals["Options"].apply(
        lambda L: master_quiz_df.iloc[0][L] if L in master_quiz_df.columns else ""
    )

    # newTotals["Level"] = newTotals["Level"].apply(
    #     lambda L: f"{answer_cols_alpabet.get(L, '')} - {master_quiz_df.iloc[0][L]}"
    #           if L in master_quiz_df.columns else ""
    # )
    
    new_order = ["Code", "Options", "Total"]
    st.dataframe(newTotals[new_order], use_container_width=True, hide_index=True)
    # df_no_index = newTotals.reset_index().drop(columns=["index"])
    # st.table(df_no_index)
    # st.table(newTotals)

    st.markdown("---")

# =====================
# TOTAL KESELURUHAN
# =====================
st.header("⭐ Total Overall")

totals_all = df[answer_cols].sum().reset_index()
totals_all.columns = ["Level", "Total"]

participants = int(participants_value)  # Add this line
# Compute average per participant
totals_all["Average"] = totals_all["Total"] / participants

totals_all["Level"] = pd.Categorical(totals_all["Level"], categories=answer_cols, ordered=True)
totals_all = totals_all.sort_values("Level")

label_all = alt.Chart(totals_all).mark_text(
    align='center',
    baseline='top',
    dy=5,              # move text upward
    fontSize=18,
    fontWeight="bolder"
).encode(
    # x="Level:N",
    x=alt.X("Level:N", sort=answer_cols),
    y="Average:Q",
    text="Average:Q"
)

chart_all = alt.Chart(totals_all).mark_bar().encode(
    x=alt.X("Level:N", sort=answer_cols, title="Level", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("Average:Q", title="Avarage"),
    color=alt.Color("Level:N", scale=alt.Scale(
            domain=list(rating_colors.keys()),
            range=list(rating_colors.values())
            ), legend=None),
        tooltip=[
            alt.Tooltip("Level:N", title="Level"),
            alt.Tooltip("Average:Q", title="Average")
        ]
).properties(height=400)

final_chart_all = chart_all + label_all

st.altair_chart(final_chart_all, use_container_width=True)

st.dataframe(totals_all, use_container_width=True, hide_index=True)

# =====================
# RAW DATA
# =====================
# with st.expander("See Raw Data"):
#     st.dataframe(df)