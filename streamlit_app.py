import os
import streamlit as st
import pandas as pd
import altair as alt

st.title('Survey')
st.sidebar.header('Filter')
# st.write("""
# # My first app
# Hello *world!*
# """)
folder_path = 'data'  # Relative path to your folder
file_name = 'SurveyDummy.csv'
full_path = os.path.join(folder_path, file_name)

df = pd.read_csv(full_path, header = 0)
# serviceLineOptions = df['Service Line'].unique().tolist()
serviceLineFilter = st.sidebar.selectbox(
    'Service line',
    options = df['Service Line'].unique().tolist(),
    index = 0
)

# bandOptions = df['Band'].unique().tolist()
bandFilter = st.sidebar.selectbox(
    'Band',
    options = df['Band'].unique().tolist(),
    index = 0
)

# genderOptions = df['Gender'].unique()
genderFilter = st.sidebar.selectbox(
    'Gender', 
    options = df['Gender'].unique().tolist(),
    index = 0
    )

# Bersihkan nama kolom
df.columns = df.columns.str.strip()

answer_cols = ["Answer1", "Answer2", "Answer3", "Answer4", "Answer5"]

# Convert TRUE/FALSE → 1/0
df[answer_cols] = df[answer_cols].replace({"TRUE": 1, "FALSE": 0})

# Group dan jumlahkan per Service Line
result = df.groupby("Service Line")[answer_cols].sum().reset_index()

# Ubah ke format long supaya bisa grouped bar
melted = result.melt(
    id_vars="Service Line",
    value_vars=answer_cols,
    var_name="Answer",
    value_name="TRUE_Count"
)

# Chart
chart = alt.Chart(melted).mark_bar().encode(
    x=alt.X("Service Line:N", title="Service Line"),
    y=alt.Y("TRUE_Count:Q", title="TRUE Count"),
    color="Answer:N",
    xOffset="Answer:N"  # <-- ini bikin bar terpisah dalam satu Service Line
).properties(
    width=600,
    height=400
)

st.altair_chart(chart, use_container_width=True)