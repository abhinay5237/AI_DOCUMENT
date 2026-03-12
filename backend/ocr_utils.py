import fitz  # PyMuPDF
import cv2
import pytesseract
import re
from pdf2image import convert_from_path
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\poppler1\poppler-23.11.0\Library\bin"


# ---------------- TEXT QUALITY CHECK ----------------
def is_text_good(text, min_chars=100, min_lines=10):
    if not text or len(text.strip()) < min_chars:
        return False
    lines = [l for l in text.split("\n") if len(l.strip()) > 5]
    return len(lines) >= min_lines


# ---------------- IMAGE PREPROCESS ----------------
def preprocess_image(img, upscale=1.4, clahe_clip=2.0):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, None, fx=upscale, fy=upscale, interpolation=cv2.INTER_CUBIC)

    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    img = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, None, 12, 7, 21)
    return gray

# ---------------- PAN SPECIAL PREPROCESS ---------------- 
def preprocess_pan(img): 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC) 
    gray = cv2.convertScaleAbs(gray, alpha=1.8, beta=20) 
    return gray


# ---------------- MAIN EXTRACTOR ----------------
def extract_text_from_pdf(pdf_path):
    """
    Extract text from any PDF (digital or scanned) or e-card like PAN/Voter ID.
    Uses adaptive DPI and preprocessing.
    """
    digital_text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            digital_text += page.get_text()
        doc.close()
    except:
        digital_text = ""

    if is_text_good(digital_text):
        print("✅ Using DIGITAL PDF text")
        return digital_text

    print("⚠ Digital text weak. Running OCR...")

    # ---------- Detect type by filename ----------
    filename = pdf_path.lower()
    is_pan_file = "pancard" in filename
    is_voter_file = "voter id" in filename


    # ---------- Set DPI & Preprocess ----------
    if is_pan_file or  is_voter_file:
        dpi_value = 350
        preprocess_fn = preprocess_pan
        psm_configs = [
            r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
            r'--oem 3 --psm 11 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
           
           
        ]

    else:
        dpi_value = 350  # moderate DPI works for most scanned/text PDFs
        preprocess_fn = preprocess_image
        psm_configs = [
            r'--oem 3 --psm 4 -l eng',
            r'--oem 3 --psm 6 -l eng',
            r'--oem 3 --psm 11 -l eng',
            r'--oem 3 --psm 7 -l eng'
        ]

    # ---------- Convert PDF to Images ----------
    pages = convert_from_path(pdf_path, dpi=dpi_value, poppler_path=POPPLER_PATH)
    ocr_text = ""

    for page in pages:
        img = np.array(page)
        img = preprocess_fn(img)

        best_text = ""
        best_length = 0

        for cfg in psm_configs:
            temp_text = pytesseract.image_to_string(img, config=cfg)

            if len(temp_text) > best_length:
                best_length = len(temp_text)
                best_text = temp_text

        ocr_text += best_text

        ocr_text += "\n"

    # ---------- Check OCR quality ----------
    if is_text_good(ocr_text):
        print("✅ OCR text looks good")
        return ocr_text

    print("⚠ OCR weak. Returning best available text")
    return digital_text if len(digital_text) > len(ocr_text) else ocr_text