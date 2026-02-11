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
serviceLineOptions = df['Service Line'].unique().tolist()
serviceLine = st.sidebar.selectbox(
    'Service line', options=serviceLineOptions, key='serviceLine')

bandOptions = df['Band'].unique().tolist()
band = st.sidebar.selectbox('Band', options=bandOptions, key='band')

genderOptions = df['Gender'].unique().tolist()
gender = st.sidebar.selectbox('Gender', options=genderOptions, key='gender')

answer_cols = ["Answer1", "Answer2", "Answer3", "Answer4", "Answer5"]
df[answer_cols] = df[answer_cols].replace({"TRUE": True, "FALSE": False})

filtered_df = df[
    (df["Gender"].isin(genderOptions)) &
    (df["Band"].isin(bandOptions)) &
    (df["Service Line"].isin(serviceLineOptions))
]

result = (
    filtered_df.groupby("Service Line")[answer_cols]
    .sum()
    .reset_index()
)

long_df = result.melt(
    id_vars="Service Line",
    value_vars=answer_cols,
    var_name="Answer",
    value_name="True Count"
)

st.bar_chart(long_df,
x="Answer",
y="True Count")
