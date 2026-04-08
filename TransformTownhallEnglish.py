import pandas as pd
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

# ==============================
# GOOGLE AUTH
# ==============================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

# ==============================
# LOAD SHEETS
# ==============================
master_sheet = client.open("Master Quiz").worksheet("Trial-En")
responses_sheet = client.open("Survey Townhall English").sheet1

# create / open output
try:
    result_sheet = client.open("Result Townhall English").worksheet("Result")
    result_sheet.clear()
except:
    result_file = client.create("Result Townhall English")
    result_sheet = result_file.worksheet("Result")

try:
    property_sheet = client.open("Result Townhall English").worksheet("Property")
    property_sheet.clear()
except:
    property_file = client.create("Result Townhall")
    property_sheet = property_file.worksheet("Property")

# ==============================
# TRANSFORM FUNCTION
# ==============================
def transform():

    # ==============================
    # LOAD DATA FROM GOOGLE SHEETS
    # ==============================
    master_df = pd.DataFrame(master_sheet.get_all_records())
    resp_df = pd.DataFrame(responses_sheet.get_all_records())

    participants = resp_df["ID"].count() 

    # ==============================
    # BUILD MAPPING
    # ==============================
    question_map = {}
    for _, row in master_df.iterrows():
        q = row["Quiz"]
        question_map[q] = row

    # ==============================
    # IDENTIFY QUESTION COLUMNS
    # ==============================
    question_cols = [col for col in resp_df.columns if col in question_map]

    rows = []
    propertyRow = []

    # ==============================
    # TRANSFORM LOOP
    # ==============================
    for _, r in resp_df.iterrows():
        for q in question_cols:

            answers_raw = r[q]

            if pd.isna(answers_raw) or answers_raw == "":
                continue

            answers = [a.strip() for a in answers_raw.split(";") if a.strip()]

            master_row = question_map[q]

            opt_5 = master_row["5 Role Model"]
            opt_4 = master_row["4 Fully Meets Expectations"]
            opt_3 = master_row["3 Partially Meets Expectations"]
            opt_2 = master_row["2 Needs Improvement"]
            opt_1 = master_row["1 Does Not Meet Expectations"]

            # opt_1 = master_row["Option1"]
            # opt_2 = master_row["Option2"]
            # opt_3 = master_row["Option3"]
            # opt_4 = master_row["Option4"]
            # opt_5 = master_row["Option5"]

            rows.append({
                "ID": r["ID"],
                # "Start time": r["Start time"],
                # "Completion time": r["Completion time"],
                # "Email": r["Email"],
                # "Name": r["Name"],
                # "Band": r["Band"],
                # "Gender": r["Gender"],
                # "Last modified time": r["Last modified time"],
                "Domain": master_row["Domain"],
                "Quiz": q,
                # "Answers": answers_raw,
                "5 Role Model": "TRUE" if opt_5 in answers else "FALSE",
                "4 Fully Meets Expectations": "TRUE" if opt_4 in answers else "FALSE",
                "3 Partially Meets Expectations": "TRUE" if opt_3 in answers else "FALSE",
                "2 Needs Improvement": "TRUE" if opt_2 in answers else "FALSE",
                "1 Does Not Meet Expectations": "TRUE" if opt_1 in answers else "FALSE"
            })

    out_df = pd.DataFrame(rows)

    # ==============================
    # WRITE TO GOOGLE SHEETS
    # ==============================
    if not out_df.empty:
        result_sheet.append_row(out_df.columns.tolist())
        result_sheet.append_rows(out_df.values.tolist())

    propertyRow.append({
        "Participants": participants
    })

    property_df = pd.DataFrame(propertyRow)

    property_sheet.append_row(property_df.columns.tolist())
    property_sheet.append_rows(property_df.values.tolist())

    print("Saved to Google Sheets:", "New Response")


# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    transform()