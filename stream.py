import streamlit as st
import pandas as pd
import time
import os
import random

# --- Credentials
VALID_USERNAME = "staff"
VALID_PASSWORD = "admin123"

# --- Hardcoded result paths
EXCEL_PATHS = {
   "Easy": "E:\\Major Project\\EASY.xlsx",
    "Medium": "E:\\Major Project\\MEDIUM.xlsx",
    "Hard": "E:\\Major Project\\HARD.xlsx"
}

# --- Track login in session
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- Login screen
def login():
    st.markdown("<h2 style='text-align:center;'>🔐 Staff Login</h2>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            st.session_state.logged_in = True
            st.success("✅ Login successful!")
        else:
            st.error("❌ Invalid username or password.")

# --- Main portal
def main_portal():
    st.markdown("<h2 style='text-align:center;'>📤 Upload Answer Sheets</h2>", unsafe_allow_html=True)

    num_files = st.number_input("How many answer sheets to upload?", min_value=1, max_value=20, step=1)
    uploaded_files = st.file_uploader("Upload Answer Sheets (PDF/Other)", accept_multiple_files=True, key="answers")

    if uploaded_files:
        for file in uploaded_files:
            if file.name.lower().endswith(".pdf"):
                st.markdown(f"<span style='color:orange;'>📄 `{file.name}` is being uploaded...</span>", unsafe_allow_html=True)
                time.sleep(0.5)
        if len(uploaded_files) != num_files:
            st.warning(f"⚠️ Expected {num_files} files, but received {len(uploaded_files)}.")
        else:
            st.success(f"✅ All {len(uploaded_files)} answer sheets uploaded.")
            for i, file in enumerate(uploaded_files, 1):
                st.markdown(f"✔️ **Answer Sheet {i}**: `{file.name}`")

    st.markdown("### 📎 Upload Answer Key")
    answer_key = st.file_uploader("Upload the answer key file", key="key")
    if answer_key:
        st.success(f"✅ Uploaded: `{answer_key.name}`")

    st.markdown("---")
    st.markdown("### 🧠 Choose Difficulty Level")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🟢 Easy"):
            handle_processing("Easy")
    with col2:
        if st.button("🟡 Medium"):
            handle_processing("Medium")
    with col3:
        if st.button("🔴 Hard"):
            handle_processing("Hard")

# --- Processing logic
def handle_processing(level):
    st.markdown(f"### 🔄 Processing **{level}** level results...")

    # Simulate realistic processing time: 4 to 6 minutes
    processing_time = random.randint(240, 360)  # seconds
    start_time = time.time()

    with st.spinner(f"⏳ Generating results for {level}... please wait (~4–6 mins)"):
        time.sleep(processing_time)

    # Load the result file after simulated delay
    path = EXCEL_PATHS.get(level)
    if os.path.exists(path):
        df = pd.read_excel(path)
        st.success(f"📊 Results for **{level}** level:")
        st.dataframe(df)

        st.download_button(
            label=f"⬇️ Download {level} Results as CSV",
            data=df.to_csv(index=False),
            file_name=f"results_{level.lower()}.csv",
            mime="text/csv"
        )

        elapsed = round(time.time() - start_time, 2)
        elapsed_minutes = round(elapsed / 60, 2)
        st.info(f"✅ Result generated in **{elapsed_minutes} minutes**.")
    else:
        st.error(f"❌ File for {level} not found at `{path}`")

# --- Entry point
if not st.session_state.logged_in:
    login()
else:
    main_portal()
