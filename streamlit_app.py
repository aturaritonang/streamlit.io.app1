import os
import streamlit as st
# st.title("🎈 My new app")
# st.write(
#     "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
# )

import pandas as pd

st.title('Survey')
st.sidebar.header('Filter')
# st.write("""
# # My first app
# Hello *world!*
# """)
folder_path = 'data'  # Relative path to your folder
file_name = 'SurveyDummy.csv'
full_path = os.path.join(folder_path, file_name)

df = pd.read_csv(full_path, header=0)
# serviceLineOptions = df['Service Line'].unique().tolist()
serviceLineFilter = st.sidebar.multiselect(
    'Service line',
    options = df['Service Line'].unique()
)

# bandOptions = df['Band'].unique().tolist()
bandFilter = st.sidebar.multiselect(
    'Band',
    options = df['Band'].unique()
)

# genderOptions = df['Gender'].unique()
genderFilter = st.sidebar.multiselect(
    'Gender', 
    options = df['Gender'].unique()
    )

answer_cols = ["Answer1", "Answer2", "Answer3", "Answer4", "Answer5"]
df[answer_cols] = df[answer_cols].replace({"TRUE": True, "FALSE": False})

filtered_df = df[
    (df["Gender"].isin(genderFilter)) &
    (df["Band"].isin(bandFilter)) &
    (df["Service Line"].isin(serviceLineFilter))
]

result = (
    filtered_df.groupby("Service Line")[answer_cols]
    .sum()
    .reset_index()
)

long_df = result.melt(
    id_vars = "Service Line",
    value_vars = answer_cols,
    var_name = "Answer",
    value_name = "True Count"
)

st.bar_chart(long_df)
