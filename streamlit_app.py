import streamlit as st

# st.title("🎈 My new app")
# st.write(
#     "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
# )

import pandas as pd

st.write("""
# My first app
Hello *world!*
""")

df = pd.read_csv("./data/SurveyDummy.csv")
st.line_chart(df)