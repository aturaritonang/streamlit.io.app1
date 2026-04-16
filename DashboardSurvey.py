import streamlit as st 
import pandas as pd
import altair as alt
import gspread
from google.oauth2.service_account import Credentials
# =====================
# APP TITLE
# =====================
st.sidebar.title("🏛️ IBMC Culture Survey")
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
dfQuiz = pd.DataFrame(client.open("Master Quiz").worksheet("Quiz-Id").get_all_records())
sheet = client.open("Result Survey 5").worksheet("Result")
data = sheet.get_all_records()
df = pd.DataFrame(data)
# =====================
# REPLACE participants_value WITH UNIQUE COUNT OF ID
# =====================
# initialize session_state for participants
# if "participants_value" not in st.session_state:
#     st.session_state.participants_value = df["ID"].nunique()
# # participants_value = df["ID"].nunique()
# st.sidebar.header(f"👥 {st.session_state.participants_value} participants")

participants_placeholder = st.sidebar.empty()
# initialize participants
if "participants_value" not in st.session_state:
    st.session_state.participants_value = df["ID"].nunique()
# initial display
participants_placeholder.header(f"👥 {st.session_state.participants_value} participants")

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
    "5 Role Model": "A", 
    "4 Fully Meets Expectations": "B", 
    "3 Partially Meets Expectations": "C", 
    "2 Needs Improvement": "D", 
    "1 Does Not Meet Expectations": "E"
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
# SIDEBAR FILTERS (2 columns) + BUTTONS
# =====================
with st.sidebar.form("filter_form"):
    st.sidebar.markdown("### 🔍 Filters")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        f_service_line = st.selectbox(
            "Service Line",
            ["All"] + sorted(df["Service Line"].dropna().unique().tolist()),
            key="service_line"
        )
        f_band = st.selectbox(
            "Band",
            ["All"] + sorted(df["Band"].dropna().unique().tolist()),
            key="band"
        )
        f_gender = st.selectbox(
            "Gender",
            ["All"] + sorted(df["Gender"].dropna().unique().tolist()),
            key="gender"
        )
        f_domain = st.selectbox(
            "Domain",
            ["All"] + sorted(df["Domain"].dropna().unique().tolist()),
            key="domain"
        )
    with col2:
        f_yos = st.selectbox(
            "Year of Service in IBM",
            ["All"] + sorted(df["Year of Service in IBM"].dropna().unique().tolist()),
            key="yos"
        )
        f_area = st.selectbox(
            "Area",
            ["All"] + sorted(df["Area"].dropna().unique().tolist()),
            key="area"
        )
        f_gen = st.selectbox(
            "Generation",
            ["All"] + sorted(df["Generation"].dropna().unique().tolist()),
            key="gen"
        )
    # apply_filter = st.form_submit_button("🔎 Apply Filter")

# ============================
# RESET Filter button (aligned with col2)
# ============================
colA, colB = st.sidebar.columns(2)
with colA:
    apply_filter = st.button("🔎 Apply Filter")
# with colB:    # right column
#     reset_filter = st.button("🔄 Reset Filter")
# =====================
# FILTER LOGIC
# =====================
df_filtered = df.copy()
# if reset_filter:
    # f_service_line = "All"
    # f_band = "All"
    # f_gender = "All"
    # f_yos = "All"
    # f_area = "All"
    # f_gen = "All"
    # f_domain = "All"
    # st.session_state.service_line = "All"
    # st.session_state.band = "All"
    # st.session_state.gender = "All"
    # st.session_state.domain = "All"
    # st.session_state.yos = "All"
    # st.session_state.area = "All"
    # st.session_state.gen = "All"
    # for key in ["service_line", "band", "gender", "domain", "yos", "area", "gen"]:
    #     st.session_state[key] = "All"
    # df_filtered = df.copy()
    # # participants_value = df_filtered["ID"].nunique()
# el
if apply_filter:
    if f_service_line != "All":
        df_filtered = df_filtered[df_filtered["Service Line"] == f_service_line]
    if f_band != "All":
        df_filtered = df_filtered[df_filtered["Band"] == f_band]
    if f_gender != "All":
        df_filtered = df_filtered[df_filtered["Gender"] == f_gender]
    if f_yos != "All":
        df_filtered = df_filtered[df_filtered["Year of Service in IBM"] == f_yos]
    if f_area != "All":
        df_filtered = df_filtered[df_filtered["Area"] == f_area]
    if f_gen != "All":
        df_filtered = df_filtered[df_filtered["Generation"] == f_gen]
    if f_domain != "All":
        df_filtered = df_filtered[df_filtered["Domain"] == f_domain]
    # participants_value = df_filtered["ID"].nunique()

st.session_state.participants_value = df_filtered["ID"].nunique()
participants_placeholder.header(f"👥 {st.session_state.participants_value} participants")
# =====================
# PER QUIZ CHART
# =====================
quiz_list = df_filtered["Quiz"].unique()
for i, quiz in enumerate(quiz_list, start=1):
    master_quiz_df = dfQuiz[dfQuiz["Quiz"] == quiz]
    domain_value = master_quiz_df["Domain"].iloc[0]
    quizA, quizB = st.columns(2)
    with quizA:
        st.markdown(f"### ❓Quiz: No. {i}")
    with quizB:
        st.markdown(f"<h3 style='text-align:right;'>Domain: {domain_value}</h3>", unsafe_allow_html=True)
        # st.markdown(f"### Domain: {domain_value}")

    st.text(f"{quiz}")
    quiz_df = df_filtered[df_filtered["Quiz"] == quiz]
    totals = quiz_df[answer_cols].sum().reset_index()
    totals.columns = ["Level", "Total"]
    totals["Level"] = pd.Categorical(totals["Level"], categories=answer_cols, ordered=True)
    totals = totals.sort_values("Level")
    totals["Code"] = totals["Level"].map(answer_cols_alpabet)
    labels = alt.Chart(totals).mark_text(
        align='center',
        baseline='top',
        dy=5,
        fontSize=18,
        fontWeight="bolder"
    ).encode(
        x="Code:N",
        y="Total:Q",
        text="Total:Q"
    )
    chart = alt.Chart(totals).mark_bar().encode(
        x=alt.X("Code:N", sort=list(answer_cols_alpabet.values()), title="Code", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Total:Q", title="Total"),
        color=alt.Color("Level:N", scale=alt.Scale(domain=list(rating_colors.keys()), range=list(rating_colors.values())), legend=None),
        tooltip=[
            alt.Tooltip("Level:N", title="Level"),
            alt.Tooltip("Total:Q", title="Total")
        ]
    ).properties(height=400)
    st.altair_chart(chart + labels, use_container_width=True)
    newTotals = totals.rename(columns={"Level": "Options"})
    newTotals["Options"] = newTotals["Options"].apply(
        lambda L: master_quiz_df.iloc[0][L] if L in master_quiz_df.columns else ""
    )
    st.dataframe(newTotals[["Code", "Options", "Total"]], use_container_width=True, hide_index=True)
    st.markdown("---")
# =====================
# TOTAL KESELURUHAN
# =====================
st.header("⭐ Total Overall")
totals_all = df_filtered[answer_cols].sum().reset_index()
totals_all.columns = ["Level", "Total"]
# =====================
# REPLACE "20" → number of unique Quiz
# =====================
unique_quiz_count = df_filtered["Quiz"].nunique()
participants = st.session_state.participants_value
totals_all["Percentage"] = ((totals_all["Total"] / unique_quiz_count) / participants) * 100
totals_all["Percentage"] = totals_all["Percentage"].round(1)
totals_all["PercentageStr"] = totals_all["Percentage"].astype(str) + "%"
totals_all["Level"] = pd.Categorical(totals_all["Level"], categories=answer_cols, ordered=True)
totals_all = totals_all.sort_values("Level")
label_all = alt.Chart(totals_all).mark_text(
    align='center',
    baseline='top',
    dy=5,
    fontSize=18,
    fontWeight="bolder"
).encode(
    x=alt.X("Level:N", sort=answer_cols),
    y="Percentage:Q",
    text="PercentageStr:N"
)
chart_all = alt.Chart(totals_all).mark_bar().encode(
    x=alt.X("Level:N", sort=answer_cols, title="Level", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("Percentage:Q", title="Percentage (%)"),
    color=alt.Color(
        "Level:N",
        scale=alt.Scale(domain=list(rating_colors.keys()), range=list(rating_colors.values())),
        legend=None
    ),
    tooltip=[
        alt.Tooltip("Level:N", title="Level"),
        alt.Tooltip("Total:Q", title="Total")
    ]
).properties(height=400)
st.altair_chart(chart_all + label_all, use_container_width=True)
totals_all["Percentage"] = totals_all["PercentageStr"]
totals_all.drop(columns=["PercentageStr"], inplace=True)
st.dataframe(totals_all, use_container_width=True, hide_index=True)