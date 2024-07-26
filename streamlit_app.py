import streamlit as st
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract'
import numpy as np
import cv2


def main():
    logo_path = "D:\OCR\logo.png"
    st.set_page_config(
    page_title="G-AI-DIGITAL-EVALUATION",page_icon=logo_path)
    st.title("DIGITAL EVALUATION USING AI")
    # st.markdown("*Streamlit* is **really** ***cool***.")
    st.header("Choose an image")
    uploaded_file = st.file_uploader("Upload Your Image",type=["jpg","png"])
    if uploaded_file is not None:
        try:
            img = np.array(Image.open(uploaded_file))
            st.image(img)
            text = pytesseract.image_to_string(img)
            print(text)
            st.write(text)

        
        except Exception as e:
            print(e)






if __name__ == "__main__":
    main()
