"""
app.py
------
FastAPI application entry point for the Receipt Extractor backend.

Exposes a single endpoint:
    POST /extract  -> accepts an uploaded receipt image, returns extracted
                       vendor / date / total as JSON.

Run with:
    uvicorn app:app --reload --port 8000
"""

import logging

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from utils import is_allowed_extension, load_image_from_bytes, pil_to_cv2, preprocess_for_ocr
from receipt_extractor import extract_receipt_data

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("receipt-extractor")

app = FastAPI(
    title=" API",
    description="Offline OCR-based receipt data extraction using Tesseract.",
    version="1.0.0",
)

# Allow the Vite dev server (and any origin, for simplicity in this project)
# to call the API from the browser. In production you would restrict this
# to your actual frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB upload limit


def error_response(message: str, status_code: int = 400) -> JSONResponse:
    """
    Build a consistent error JSON response shape used across the API:
        {"success": false, "message": "..."}
    """
    return JSONResponse(status_code=status_code, content={"success": False, "message": message})


@app.get("/")
def read_root():
    """Simple health-check endpoint so you can confirm the server is running."""
    return {"status": "ok", "service": "Image information API"}


@app.post("/extract")
async def extract_receipt(file: UploadFile = File(...)):
    """
    Accept a receipt image upload and return extracted vendor/date/total.

    Steps:
      1. Validate the file extension (.jpg/.jpeg/.png only).
      2. Read the raw bytes and validate size / non-empty.
      3. Decode the bytes into an image, catching corrupted files.
      4. Pre-process the image (grayscale, denoise, threshold) for OCR.
      5. Run OCR + regex extraction.
      6. Return structured JSON, or a "Receipt not detected." error.

    Any unexpected failure is caught and returned as a clean 500 JSON error
    instead of leaking a stack trace to the client.
    """
    try:
        # --- 1. Validate file extension -----------------------------------
        if not file.filename or not is_allowed_extension(file.filename):
            return error_response(
                "Invalid file type. Only JPG, JPEG, and PNG images are supported."
            )

        # --- 2. Read bytes & validate they exist / aren't too large -------
        file_bytes = await file.read()

        if not file_bytes:
            return error_response("Uploaded file is empty.")

        if len(file_bytes) > MAX_FILE_SIZE_BYTES:
            return error_response("File is too large. Maximum allowed size is 10 MB.")

        # --- 3. Decode image (raises ValueError on corrupted files) -------
        try:
            image = load_image_from_bytes(file_bytes)
        except ValueError as decode_error:
            return error_response(str(decode_error))

        # --- 4. Pre-process for OCR ---------------------------------------
        cv2_image = pil_to_cv2(image)
        preprocessed = preprocess_for_ocr(cv2_image)

        # --- 5. Run OCR + regex extraction --------------------------------
        result = extract_receipt_data(preprocessed)

        # --- 6. Return result (success or "Receipt not detected.") -------
        if not result.get("success"):
            return JSONResponse(status_code=200, content=result)

        return JSONResponse(status_code=200, content=result)

    except Exception as exc:  # noqa: BLE001 - final safety net for the API
        logger.exception("Unexpected error while processing receipt upload")
        return error_response(f"Internal server error: {str(exc)}", status_code=500)
