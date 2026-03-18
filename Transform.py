import pandas as pd
import os
def transform():
    master_path = "./data/raw/MasterQuiz.csv"
    responses_path = "./data/raw/Responses.csv"
    output_path = "./data/final/NewResult.csv"
    # Load master quiz
    master_df = pd.read_csv(master_path)
    # Build mapping: question -> full master row
    question_map = {}
    for _, row in master_df.iterrows():
        q = row["Question :"]
        question_map[q] = row
    # Load responses
    resp_df = pd.read_csv(responses_path)
    meta_cols = ["ID", "Start time", "Completion time", "Email", "Name", "Last modified time"]
    # Identify response question columns that match the master quiz
    question_cols = [col for col in resp_df.columns if col in question_map]
    rows = []
    for _, r in resp_df.iterrows():
        for q in question_cols:
            answers_raw = r[q]
            if pd.isna(answers_raw) or answers_raw == "":
                continue
            # Split respondent multi-answers
            answers = [a.strip() for a in answers_raw.split(";") if a.strip() != ""]
            master_row = question_map[q]
            # Extract master rating options
            opt_5 = master_row["5 - Role Model"]
            opt_4 = master_row["4 ? Fully Meets Expectations"]
            opt_3 = master_row["3 ? Partially Meets Expectations"]
            opt_2 = master_row["2 ? Needs Improvement"]
            opt_1 = master_row["1 ? Does Not Meet Expectations"]
            # TRUE if contained, otherwise FALSE
            flag_5 = "TRUE" if opt_5 in answers else "FALSE"
            flag_4 = "TRUE" if opt_4 in answers else "FALSE"
            flag_3 = "TRUE" if opt_3 in answers else "FALSE"
            flag_2 = "TRUE" if opt_2 in answers else "FALSE"
            flag_1 = "TRUE" if opt_1 in answers else "FALSE"
            rows.append({
                "ID": r["ID"],
                "Start time": r["Start time"],
                "Completion time": r["Completion time"],
                "Email": r["Email"],
                "Name": r["Name"],
                "Last modified time": r["Last modified time"],
                "Quiz": q,
                "Answers": answers_raw,
                "5 ? Role Model": flag_5,
                "4 ? Fully Meets Expectations": flag_4,
                "3 ? Partially Meets Expectations": flag_3,
                "2 ? Needs Improvement": flag_2,
                "1 ? Does Not Meet Expectations": flag_1
            })
    out_df = pd.DataFrame(rows)
    os.makedirs("./data/final", exist_ok=True)
    out_df.to_csv(output_path, index=False)
    print("Saved:", output_path)
if __name__ == "__main__":
    transform()