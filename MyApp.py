import os
import streamlit as st
import pandas as pd
import altair as alt

st.title("Survey Dashboard")
st.sidebar.header('Filter')
folder_path = 'data'  # Relative path to your folder
file_name = 'SurveyDummy.csv'
full_path = os.path.join(folder_path, file_name)

# uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if full_path is not None:
    df = pd.read_csv(full_path)

    df.columns = df.columns.str.strip()

    answer_cols = ["Answer1", "Answer2", "Answer3", "Answer4", "Answer5"]

    # Convert TRUE/FALSE → 1/0
    df[answer_cols] = df[answer_cols].replace({"TRUE": 1, "FALSE": 0})

    # =====================
    # FILTER
    # =====================
    st.sidebar.header("Filters")

    service_options = ["All"] + sorted(df["Service Line"].unique())
    gender_options = ["All"] + sorted(df["Gender"].unique())
    band_options = ["All"] + sorted(df["Band"].unique())

    service_filter = st.sidebar.selectbox("Service Line", service_options)
    gender_filter = st.sidebar.selectbox("Gender", gender_options)
    band_filter = st.sidebar.selectbox("Band", band_options)

    filtered_df = df.copy()

    if service_filter != "All":
        filtered_df = filtered_df[filtered_df["Service Line"] == service_filter]

    if gender_filter != "All":
        filtered_df = filtered_df[filtered_df["Gender"] == gender_filter]

    if band_filter != "All":
        filtered_df = filtered_df[filtered_df["Band"] == band_filter]

    # =====================
    # AGGREGATION (X = Answer)
    # =====================
    totals = filtered_df[answer_cols].sum().reset_index()
    totals.columns = ["Answer", "TRUE_Count"]

    # =====================
    # CHART
    # =====================
    chart = alt.Chart(totals).mark_bar().encode(
        x=alt.X("Answer:N", title="Answer"),
        y=alt.Y("TRUE_Count:Q", title="TRUE Count"),
        color="Answer:N"
    ).properties(height=400)

    st.altair_chart(chart, use_container_width=True)

    with st.expander("See Data"):
        st.dataframe(filtered_df)