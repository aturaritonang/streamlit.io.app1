import streamlit as st
import pandas as pd
import random
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ==============================
# CONFIG
# ==============================
FOLDER_NAME = "Quiz Folder"
QUIZ_FILE = "Master Quiz"
AUDIENS_FILE = "Master Audiens"

# ==============================
# GOOGLE SHEETS CONNECT
# ==============================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "data/credential/custom-history-497-cf16fd3f136c.json", scope
)
client = gspread.authorize(creds)

# buka folder
folder = client.open(QUIZ_FILE)  # file tetap dibuka langsung

quiz_sheet = folder.sheet1  # Master Quiz
quiz_df = pd.DataFrame(quiz_sheet.get_all_records())

audien_sheet = client.open(AUDIENS_FILE).sheet1
audien_df = pd.DataFrame(audien_sheet.get_all_records())

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
        "Business Line", "Band", "Quiz", "Answer"
    ])

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
st.title("🔐 Login")

if not st.session_state.login:
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
        else:
            st.error("Email / Password salah")

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
    # DOMAIN NAVIGATION
    # ==============================
    domains = quiz_df["Domain"].unique()

    selected_domain = st.sidebar.radio(
        "Pilih Domain",
        domains
    )

    st.header(f"Domain: {selected_domain}")

    domain_df = quiz_df[quiz_df["Domain"] == selected_domain]

    # ==============================
    # FORM
    # ==============================
    with st.form(f"form_{selected_domain}"):

        for i, row in domain_df.iterrows():

            quiz = row["Quiz"]

            options = [
                row["Option1"],
                row["Option2"],
                row["Option3"],
                row["Option4"],
                row["Option5"]
            ]

            random.shuffle(options)

            key = f"{selected_domain}_{i}"
            default = st.session_state.answers.get(key, [])

            selected = st.multiselect(
                quiz,
                options,
                default=default,
                key=key,
                disabled=st.session_state.submitted
            )

            st.session_state.answers[key] = selected

        col1, col2 = st.columns(2)

        with col1:
            save_btn = st.form_submit_button("💾 Save")

        with col2:
            submit_btn = st.form_submit_button("✅ Submit")

    # ==============================
    # SAVE (DRAFT)
    # ==============================
    if save_btn:
        st.success("✅ Progress tersimpan (draft)")

    # ==============================
    # SUBMIT FINAL
    # ==============================
    if submit_btn:

        # VALIDASI STATIC FIELD
        if not st.session_state.band or not st.session_state.service_line:
            st.error("❌ Band dan Service Line wajib diisi")

        else:
            valid = True

            for key, val in st.session_state.answers.items():
                if key.startswith(selected_domain):
                    if len(val) < 3:
                        valid = False
                        break

            if not valid:
                st.error("❌ Setiap soal wajib minimal 3 jawaban")
            else:
                for i, row in domain_df.iterrows():

                    quiz = row["Quiz"]
                    key = f"{selected_domain}_{i}"
                    selected = st.session_state.answers.get(key, [])

                    response_sheet.append_row([
                        str(datetime.now()),
                        st.session_state.email,
                        st.session_state.name,
                        st.session_state.service_line,
                        st.session_state.band,
                        quiz,
                        ", ".join(selected)
                    ])

                st.session_state.submitted = True
                st.success("🎉 Submit berhasil! Data tidak bisa diubah lagi.")

# ==============================
# LOCK UI
# ==============================
if st.session_state.submitted:
    st.warning("⚠️ Jawaban sudah final dan tidak dapat diubah.")