import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util

# Load the pre-trained sentence transformer model once
model = SentenceTransformer('all-MiniLM-L6-v2')

# --- Utility Functions ---
def read_excel(file_path):
    return pd.read_excel(file_path)

def ngram_similarity(text1, text2, n=2):
    if pd.isna(text1) or pd.isna(text2) or not str(text1).strip() or not str(text2).strip():
        return 0.0
    vectorizer = CountVectorizer(ngram_range=(n, n)).fit([text1, text2])
    vec1, vec2 = vectorizer.transform([text1, text2])
    return cosine_similarity(vec1, vec2)[0][0] * 100  # As percentage

def mean_ngram_similarity(text1, text2):
    scores = [ngram_similarity(text1, text2, n) for n in [1, 2, 3]]
    return np.mean(scores)

def sentence_flow_score(text1, text2):
    if pd.isna(text1) or pd.isna(text2) or not str(text1).strip() or not str(text2).strip():
        return 0.0
    embedding1 = model.encode(text1, convert_to_tensor=True)
    embedding2 = model.encode(text2, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embedding1, embedding2).item()
    return similarity * 100  # convert to percentage

def get_max_marks(question):
    if 'Part-A' in question:
        return 2
    elif 'Part-B' in question:
        return 5
    elif 'Part-C' in question:
        return 7
    return 1

# --- Main Evaluation Logic ---
def evaluate_students(student_answers, answer_key):
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

            # Base mark
            base_similarity = mean_ngram_similarity(student_answer, key_answer)
            base_mark = (base_similarity / 100) * max_mark

            # Plagiarism and flow detection
            other_answers = student_answers[student_answers['Roll Number'] != roll_no][question].fillna("")
            plagiarism_scores = [mean_ngram_similarity(student_answer, ans) for ans in other_answers]
            flow_scores = [sentence_flow_score(student_answer, ans) for ans in other_answers]

            plagiarism_pct = 100 - np.mean(plagiarism_scores) if plagiarism_scores else 100
            flow_pct = np.mean(flow_scores) if flow_scores else 100

            # Final mark
            final_mark = base_mark * (plagiarism_pct / 100) * (flow_pct / 100)
            final_mark = round(final_mark, 2)
            total_marks += final_mark

            # Store results
            student_result[f'{question} - Base'] = round(base_mark, 2)
            student_result[f'{question} - Plagiarism %'] = round(plagiarism_pct, 2)
            student_result[f'{question} - Flow %'] = round(flow_pct, 2)
            student_result[f'{question} - Final'] = final_mark

        student_result['Total Marks'] = round(total_marks, 2)
        results.append(student_result)

    return pd.DataFrame(results)

# --- Main Execution ---
if __name__ == "__main__":
    # Step 1: Read the Excel files
    student_answers = read_excel("E:\\Major Project\\ANSWER_SCRIPT.xlsx")
    answer_key = read_excel("E:\\Major Project\\Answer_Key.xlsx")

    # Step 2: Clean NaNs
    student_answers.fillna("", inplace=True)
    answer_key.fillna("", inplace=True)

    # Step 3: Run evaluation
    results_df = evaluate_students(student_answers, answer_key)

    # Step 4: Output results
    print("=== Evaluation Results ===")
    print(results_df)

    # Step 5: Save to Excel
    results_df.to_excel("evaluated_results.xlsx", index=False)
    print("\n✅ Results saved to 'evaluated_results.xlsx'")
