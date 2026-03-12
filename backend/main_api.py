from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import os
from ai_engine import analyze_documents, download_drive_folder

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/analyze")
async def analyze(drive_link: str = Form(...)):

    print("\n===== API HIT =====")
    print("DRIVE LINK RECEIVED:", drive_link)

    # Clear uploads folder
    for f in os.listdir(UPLOAD_FOLDER):
        os.remove(os.path.join(UPLOAD_FOLDER, f))

    # Download files from drive
    downloaded_files = download_drive_folder(drive_link, UPLOAD_FOLDER)
    print("DOWNLOADED FILES:", downloaded_files)

    if not downloaded_files:
        return {"error": "No files found in Drive folder"}

    # Analyze
    result = analyze_documents(UPLOAD_FOLDER)

    return result