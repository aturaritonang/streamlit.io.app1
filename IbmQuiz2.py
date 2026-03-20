import streamlit as st
import pandas as pd
import random
from datetime import datetime
import os
import gspread
from oauth2client.service_account import Credential
# from oauth2client.service_account import ServiceAccountCredentials

# ==============================
# CONFIG FILE PATH
# ==============================
QUIZ_PATH = "data/raw/MasterQuiz.csv"
AUDIENS_PATH = "data/raw/MasterAudiens.csv"

# ==============================
# GOOGLE SHEETS CONNECT
# ==============================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# creds = ServiceAccountCredentials.from_json_keyfile_name(
#     "data/credential/credential.json", scope
# )

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

# ==============================
# RESPONSE SHEET
# ==============================
try:
    response_sheet = client.open("Responses").sheet1
except:
    response_file = client.create("Responses")
    response_sheet = response_file.sheet1
    response_sheet.append_row([
        "Timestamp", "Email", "Name",
        "Business Line", "Band", "Domain", "Quiz", "Answer"
    ])

# ==============================
# LOAD DATA
# ==============================
quiz_df = pd.read_csv(QUIZ_PATH)
audien_df = pd.read_csv(AUDIENS_PATH)

# ==============================
# SESSION STATE
# ==============================
if "login" not in st.session_state:
    st.session_state.login = False

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "band" not in st.session_state:
    st.session_state.band = None

if "service_line" not in st.session_state:
    st.session_state.service_line = None

# ==============================
# LOGIN
# ==============================
with st.container(border=True):
    if not st.session_state.get("login", False):
        st.title("🔐 Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = audien_df[
                (audien_df["Email"] == email) &
                (audien_df["Password"] == password)
            ]

            if not user.empty:
                st.session_state.login = True
                st.session_state.email = email
                st.session_state.name = user.iloc[0]["Name"]

                st.success("Login berhasil")
                st.rerun()
            else:
                st.error("Email / Password salah")
    else:
        st.success(f"Welcome, {st.session_state.name} 👋")

# ==============================
# MAIN APP
# ==============================
if st.session_state.login:

    st.title("📊 Quiz Survey")
    st.write(f"Halo, {st.session_state.name}")

    # ==============================
    # STATIC SELECTION
    # ==============================
    st.subheader("📌 Informasi Wajib")

    st.session_state.band = st.selectbox(
        "Band",
        ["Band 5", "Band 6", "Band 7", "Band 8", "Band 9", "Band 10"],
        disabled=st.session_state.submitted
    )

    st.session_state.service_line = st.selectbox(
        "Service Line",
        ["Applicationn Operations", "Hybrid Cloud and Data"],
        disabled=st.session_state.submitted
    )

    # ==============================
    # ALL DOMAINS
    # ==============================
    domains = quiz_df["Domain"].unique()

    with st.form("main_form"):

        for domain in domains:

            st.header(f"📂 {domain}")

            domain_df = quiz_df[quiz_df["Domain"] == domain]

            for i, row in domain_df.iterrows():

                quiz = row["Quiz"]

                options = [
                    row["Option1"],
                    row["Option2"],
                    row["Option3"],
                    row["Option4"],
                    row["Option5"]
                ]

                # random.shuffle(options)

                key = f"{domain}_{i}"

                options_key = f"{key}_options"

                if options_key not in st.session_state:
                    shuffled = options.copy()
                    random.shuffle(shuffled)
                    st.session_state[options_key] = shuffled

                options = st.session_state[options_key]

                default = st.session_state.answers.get(key, [])

                with st.container(border=True):
                    st.write(quiz)

                    selected = []

                    for opt_idx, option in enumerate(options):
                        checkbox_key = f"{key}_{opt_idx}"

                        checked = st.checkbox(
                            option,
                            value=option in default,
                            key=checkbox_key,
                            disabled=st.session_state.submitted
                        )

                        if checked:
                            selected.append(option)

                    st.session_state.answers[key] = selected

        submit_btn = st.form_submit_button("✅ Submit")
        # st.write(st.session_state.answers)

    # ==============================
    # SUBMIT
    # ==============================
    if submit_btn:

        if not st.session_state.band or not st.session_state.service_line:
            st.error("❌ Band dan Service Line wajib diisi")

        else:
            valid = True

            for val in st.session_state.answers.values():
                if len(val) < 3:
                    valid = False
                    break

            if not valid:
                st.error("❌ Setiap soal wajib minimal 3 jawaban")
            else:
                timeStamp = datetime.now()
                for domain in domains:
                    domain_df = quiz_df[quiz_df["Domain"] == domain]
                    for i, row in domain_df.iterrows():

                        domain = row["Domain"] 
                        quiz = row["Quiz"]
                        key = f"{domain}_{i}"
                        selected = st.session_state.answers.get(key, [])

                        response_sheet.append_row([
                            str(timeStamp),
                            st.session_state.email,
                            st.session_state.name,
                            st.session_state.service_line,
                            st.session_state.band,
                            domain,
                            quiz,
                            "; ".join(selected)
                        ])

                st.session_state.submitted = valid
                st.success("🎉 Submit berhasil!")

# ==============================
# LOCK UI
# ==============================
if st.session_state.submitted:
    st.warning("⚠️ Jawaban sudah disubmit")