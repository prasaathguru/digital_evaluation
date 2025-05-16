import os
import re
from pdf2image import convert_from_path
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

# Azure credentials
endpoint = "https://evaocr.cognitiveservices.azure.com/"
key = "7nbxrWadDbhBnx2U3qABcbymInmmNfi694uzPcMM5lQCSPezXRU0JQQJ99BBACYeBjFXJ3w3AAAEACOGnnLF"

# Initialize client
client = ImageAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

def extract_text_from_image(image_path):
    """Extracts text from an image using Azure's OCR service."""
    with open(image_path, "rb") as f:
        image_data = f.read()
    result = client.analyze(image_data=image_data, visual_features=[VisualFeatures.READ])
    extracted_text = ""
    if result.read is not None:
        for block in result.read.blocks:
            for line in block.lines:
                extracted_text += line.text + " "
    return extracted_text.strip()

def clean_text(text):
    """Cleans unwanted elements and normalizes parts."""
    # Remove page numbers like P.No. 41 or P.No. J .. 41
    text = re.sub(r'P\.?\s*No\.?\s*\S*\s*\.*\s*\d*', '', text, flags=re.IGNORECASE)

    # Normalize known OCR mistakes for part headers
    text = re.sub(r'D[\s\-–]?A[\s\-–]?R[\s\-–]?T[\s\-–]?[\-–]?\s*C[.:)]?', 'PART C', text, flags=re.IGNORECASE)
    text = re.sub(r'PART[\s\-–]?B[.:)]?', 'PART B', text, flags=re.IGNORECASE)
    text = re.sub(r'PART[\s\-–]?A[.:)]?', 'PART A', text, flags=re.IGNORECASE)

    return text

def split_by_parts(text):
    """Splits the text into PART A, PART B, and PART C using OCR-tolerant rules."""

    # Normalize common OCR mistakes before splitting
    text = re.sub(r'D[\s\-–]?A[\s\-–]?R[\s\-–]?T[\s\-–]?\s*A', 'PART A', text, flags=re.IGNORECASE)
    text = re.sub(r'D[\s\-–]?A[\s\-–]?R[\s\-–]?T[\s\-–]?\s*B', 'PART B', text, flags=re.IGNORECASE)
    text = re.sub(r'D[\s\-–]?A[\s\-–]?R[\s\-–]?T[\s\-–]?\s*C', 'PART C', text, flags=re.IGNORECASE)

    # Insert markers before parts to split later
    text = re.sub(r'\bPART\s*[-–]?\s*A\b', '@@PART A', text, flags=re.IGNORECASE)
    text = re.sub(r'\bPART\s*[-–]?\s*B\b', '@@PART B', text, flags=re.IGNORECASE)
    text = re.sub(r'\bPART\s*[-–]?\s*C\b', '@@PART C', text, flags=re.IGNORECASE)

    parts = re.split(r'@@(PART\s*[ABC])', text, flags=re.IGNORECASE)
    structured = {}
    current_part = None

    for part in parts:
        if re.match(r'PART\s*[ABC]', part, re.IGNORECASE):
            current_part = part.strip().upper()
            structured[current_part] = ""
        elif current_part:
            structured[current_part] += part.strip() + " "

    return structured

def process_pdf(pdf_path):
    """Converts PDF to images, extracts text using OCR, and structures it by parts and questions."""
    images = convert_from_path(pdf_path)
    full_text = ""

    # Convert each PDF page to image and extract text
    for i, image in enumerate(images):
        image_path = f"temp_page_{i+1}.png"
        image.save(image_path, "PNG")
        text = extract_text_from_image(image_path)
        full_text += f"{text} "
        os.remove(image_path)
    print("======= RAW OCR TEXT =======")
    print(full_text)

    # Clean OCR issues and noise
    full_text = clean_text(full_text)

    # ✅ Split into structured parts (A, B, C)
    structured_parts = split_by_parts(full_text)

    # Split and print questions under each part
    for part_name, part_content in structured_parts.items():
        print(f"\n{'='*10} {part_name} {'='*10}")

        # Split main questions like 1), 2), 3), etc.
        major_questions = re.split(r'(?=\b\d+\s*[).])', part_content.strip())

        for q in major_questions:
            q = q.strip()
            if q:
                print(f"\nQuestion:\n{q}")
                
                # Optional: further split subquestions like (a), (b)
                subquestions = re.split(r'(?=\([a-z]\))', q)
                if len(subquestions) > 1:
                    for sub in subquestions:
                        if sub.strip():
                            print(f"  Subquestion:\n  {sub.strip()}")

if __name__ == "__main__":
    pdf_path = "E:\\Major Project\\REAL_WORLD_IMAGES\\PDF\\1191030603201142.pdf"
    process_pdf(pdf_path)
