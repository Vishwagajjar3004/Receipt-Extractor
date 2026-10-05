# 🧾 Receipt Extractor

A full-stack web application that extracts **vendor name, date, and total
amount** from a photo of a receipt — entirely **offline**, using
**Tesseract OCR** and regular expressions. No cloud AI service, and no API
key, is used anywhere in this project.

---

## 📖 Project Overview

Upload a photo of a receipt (JPG/JPEG/PNG) through a modern drag-and-drop
web interface. The FastAPI backend pre-processes the image with OpenCV,
runs it through Tesseract OCR, and parses the resulting text with regular
expressions to pull out:

- **Vendor Name**
- **Receipt Date**
- **Total Amount**

The result is returned as clean JSON and displayed in the UI as a styled,
printed-receipt-style card.

If the uploaded image doesn't look like a receipt (e.g. a random photo),
the API responds with:

```json
{
  "success": false,
  "message": "Receipt not detected."
}
```

---

## ✨ Features

- 📤 Drag-and-drop or click-to-browse image upload
- 🖼️ Live image preview before extraction
- 🔒 100% offline — no cloud AI, no API keys, no internet dependency at runtime
- 🧠 OCR-based text extraction using Tesseract
- 🧾 Smart parsing of vendor / date / total using regex heuristics
- ✅ Validates file type, empty uploads, and corrupted images
- 🕵️ Detects non-receipt images and returns a clear error
- ⏳ Loading spinner while the backend processes the image
- ❌ Friendly error cards for failures
- 🔄 Reset button to start over
- 📱 Fully responsive, modern UI built with Tailwind CSS

---

## 🛠️ Technologies Used

**Backend**
- Python 3
- FastAPI
- pytesseract (Tesseract OCR wrapper)
- Pillow
- OpenCV (`opencv-python-headless`)
- Regular Expressions (`re`)
- Uvicorn (ASGI server)

**Frontend**
- React (Vite)
- Tailwind CSS
- Axios

---

## 📁 Project Structure

```
receipt-extractor/
├── backend/
│   ├── app.py                 # FastAPI app & /extract endpoint
│   ├── receipt_extractor.py   # OCR + regex extraction logic
│   ├── utils.py                # Validation & image pre-processing helpers
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DropZone.jsx
│   │   │   ├── ImagePreview.jsx
│   │   │   ├── ResultCard.jsx
│   │   │   ├── ErrorCard.jsx
│   │   │   └── Spinner.jsx
│   │   ├── pages/
│   │   │   └── Home.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── vite.config.js
│   └── .env.example
│
└── README.md
```

---

## ⚙️ Installation

### 1. Install Tesseract OCR (required — this is the OCR engine itself)

pytesseract is just a Python wrapper; the actual Tesseract OCR engine must
be installed separately on your machine.

**Windows**
1. Download the installer from the [UB-Mannheim Tesseract builds page](https://github.com/UB-Mannheim/tesseract/wiki).
2. Run the installer (default path is usually `C:\Program Files\Tesseract-OCR\tesseract.exe`).
3. Add that folder to your system `PATH`, **or** set the path explicitly in
   `backend/app.py` / `backend/receipt_extractor.py` by adding near the top:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
   ```

**macOS**
```bash
brew install tesseract
```

**Linux (Debian/Ubuntu)**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr
```

Verify installation:
```bash
tesseract --version
```

---

### 2. Backend Setup

```bash
cd backend

# (Recommended) create a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

---

## ▶️ How to Run

### Run the Backend (FastAPI)

```bash
cd backend
uvicorn app:app --reload --port 8000
```

The API will be available at: `http://127.0.0.1:8000`
Health check: `GET http://127.0.0.1:8000/`

### Run the Frontend (React + Vite)

In a separate terminal:

```bash
cd frontend
npm run dev
```

The app will be available at: `http://127.0.0.1:5173`

> If your backend runs on a different host/port, copy `frontend/.env.example`
> to `frontend/.env` and update `VITE_API_BASE_URL`.

---

## 📡 API Reference

### `POST /extract`

Accepts `multipart/form-data` with a single field named `file` (the image).

**Success response — `200 OK`**
```json
{
  "success": true,
  "vendor": "DMart",
  "date": "12/02/2026",
  "total": "₹520"
}
```

**Not a receipt — `200 OK`**
```json
{
  "success": false,
  "message": "Receipt not detected."
}
```

**Invalid file type — `400 Bad Request`**
```json
{
  "success": false,
  "message": "Invalid file type. Only JPG, JPEG, and PNG images are supported."
}
```

**Corrupted / unreadable image — `400 Bad Request`**
```json
{
  "success": false,
  "message": "Uploaded file is not a valid or readable image."
}
```

---

## 🧠 How Extraction Works

1. **Validation** — file extension, non-empty, decodable image.
2. **Pre-processing** (OpenCV) — grayscale conversion, denoising, adaptive
   thresholding to make text stand out clearly for OCR.
3. **OCR** (pytesseract) — extracts raw text from the cleaned image.
4. **Receipt detection** — checks for receipt-like keywords ("total",
   "tax", "invoice", etc.) and currency/amount patterns. If neither is
   present, the image is rejected as "not a receipt".
5. **Regex parsing**:
   - **Vendor**: taken from the first plausible non-address, non-numeric
     line near the top of the receipt (where store names are usually printed).
   - **Date**: matched against common date formats (`DD/MM/YYYY`,
     `YYYY-MM-DD`, `12 Feb 2026`, `Feb 12, 2026`, etc.).
   - **Total**: lines containing keywords like "grand total", "total
     amount", "subtotal" are searched first; if none match, the largest
     currency-like number in the text is used as a fallback.

---

## 🚫 Offline & Privacy

This project runs **completely offline** at runtime — no receipt image or
extracted data is ever sent to any third-party API or cloud service.
Internet access is only needed once, to download Python/npm packages
during installation.

No Docker is used — everything runs directly with Python and Node.js.

---

## 🧪 Tips for Best Results

- Use a well-lit, in-focus photo of the receipt.
- Try to keep the receipt flat and fully within the frame.
- Very faded thermal-paper receipts may reduce OCR accuracy — this is a
  limitation of OCR technology in general, not specific to this app.
