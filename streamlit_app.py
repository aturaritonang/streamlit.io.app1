import os
import streamlit as st

# st.title("🎈 My new app")
# st.write(
#     "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
# )

import pandas as pd

st.title('Survey')

st.write("""
# My first app
Hello *world!*
""")
folder_path = 'data' # Relative path to your folder
file_name = 'SurveyDummy.csv'
full_path = os.path.join(folder_path, file_name)

df = pd.read_csv(full_path, header=0)
serviceLineOptions = df['Service Line'].unique().tolist()
serviceLine = st.sidebar.selectbox('Service line', options=serviceLineOptions, key = 'serviceLine')

bandOptions = df['Band'].unique().tolist()
band = st.sidebar.selectbox('Band', options=bandOptions, key = 'band')

genderOptions = df['Gender'].unique().tolist()
gender = st.sidebar.selectbox('Gender', options=genderOptions, key = 'gender')

st.line_chart(df, x='Service Line', y='Answer1')