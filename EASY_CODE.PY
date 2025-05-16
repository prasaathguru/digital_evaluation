import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util

# Load sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# --- Utility Functions ---
def read_excel(file_path):
    return pd.read_excel(file_path)

def sentence_similarity(text1, text2):
    if pd.isna(text1) or pd.isna(text2) or not str(text1).strip() or not str(text2).strip():
        return 0.0
    embedding1 = model.encode(text1, convert_to_tensor=True)
    embedding2 = model.encode(text2, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embedding1, embedding2).item()
    return similarity * 100  # as percentage

def get_max_marks(question):
    if 'Part-A' in question:
        return 2
    elif 'Part-B' in question:
        return 5
    elif 'Part-C' in question:
        return 7
    return 1

def length_similarity(text1, text2):
    len1 = len(str(text1).split())
    len2 = len(str(text2).split())
    if len1 == 0 or len2 == 0:
        return 0.0
    return min(len1, len2) / max(len1, len2)

# --- Main Evaluation Logic ---
def evaluate_students_easy(student_answers, answer_key):
    results = []
    questions = [q for q in student_answers.columns if q != 'Roll Number']

    for _, student_row in student_answers.iterrows():
        roll_no = student_row['Roll Number']
        student_result = {'Roll Number': roll_no, 'Total Marks': 0}
        total_marks = 0

        for question in questions:
            max_mark = get_max_marks(question)
            student_answer = student_row.get(question, '')
            key_answer = answer_key.loc[0, question] if question in answer_key.columns else ''

            # --- Sentence-based base score ---
            similarity = sentence_similarity(student_answer, key_answer)

            # --- Add a small bonus if length is close to the key ---
            length_bonus = length_similarity(student_answer, key_answer)
            adjusted_similarity = similarity * (0.7 + 0.3 * length_bonus)  # 30% boost for length match

            # --- Convert to marks ---
            raw_mark = (adjusted_similarity / 100) * max_mark

            # --- Guarantee minimum score if something is written ---
            if str(student_answer).strip():
                raw_mark = max(raw_mark, 0.3 * max_mark)  # minimum 30%
            else:
                raw_mark = 0.0

            final_mark = round(min(raw_mark, max_mark), 2)
            total_marks += final_mark

            # Save detailed info
            student_result[f'{question} - Similarity %'] = round(similarity, 2)
            student_result[f'{question} - Final'] = final_mark

        student_result['Total Marks'] = round(total_marks, 2)
        results.append(student_result)

    return pd.DataFrame(results)

# --- Main Execution ---
if __name__ == "__main__":
    student_answers = read_excel("E:\\Major Project\\ANSWER_SCRIPT.xlsx")
    answer_key = read_excel("E:\\Major Project\\Answer_Key.xlsx")

    student_answers.fillna("", inplace=True)
    answer_key.fillna("", inplace=True)

    results_df = evaluate_students_easy(student_answers, answer_key)

    print("=== Easy Evaluation Results ===")
    print(results_df)

    results_df.to_excel("evaluated_results_easy.xlsx", index=False)
    print("\n✅ Easy version results saved to 'evaluated_results_easy.xlsx'")
