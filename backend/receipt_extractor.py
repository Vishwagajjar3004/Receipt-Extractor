"""
receipt_extractor.py
---------------------
Core "business logic" of the app: turn a pre-processed receipt image into
structured data (vendor, date, total) using Tesseract OCR + regular
expressions. No cloud AI / paid API is used anywhere in this file.

High level pipeline (see extract_receipt_data()):
    image -> OCR text -> is-this-a-receipt check -> regex parsing -> dict
"""

import re
from typing import Optional, List

import pytesseract
import numpy as np

# ---------------------------------------------------------------------------
# Keywords that commonly appear on real-world receipts. We use these both to
# decide "is this actually a receipt?" and to help locate the total amount.
# ---------------------------------------------------------------------------
RECEIPT_KEYWORDS = [
    "total", "subtotal", "sub total", "grand total", "amount", "cash",
    "change", "receipt", "invoice", "bill", "tax", "gst", "vat", "cgst",
    "sgst", "qty", "quantity", "item", "paid", "balance", "thank you",
    "customer", "card", "visa", "mastercard", "upi", "date",
]

TOTAL_KEYWORDS = [
    "grand total", "net total", "net amount", "total amount", "amount due",
    "balance due", "total payable", "sub total", "subtotal", "total",
    "amount paid", "amount", "net payable",
]

# Currency symbols / codes we try to recognise so the amount is returned
# with its symbol attached, e.g. "₹520", "$45.00".
CURRENCY_SYMBOLS = r"₹|\$|€|£|Rs\.?|INR|USD|EUR|GBP"

# Matches numbers like 1,234.56 / 520 / 45.00
AMOUNT_PATTERN = r"(?:{currency})?\s*[\d]{{1,3}}(?:[,.\s]\d{{2,3}})*(?:\.\d{{1,2}})?".format(
    currency=CURRENCY_SYMBOLS
)

# A collection of common date formats found on receipts worldwide.
DATE_PATTERNS = [
    r"\b\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4}\b",              # 12/02/2026, 12-02-26
    r"\b\d{4}[\/\-.]\d{1,2}[\/\-.]\d{1,2}\b",                # 2026-02-12
    r"\b\d{1,2}\s?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
    r"[a-z]*\s?,?\s?\d{2,4}\b",                              # 12 Feb 2026 / 12-Feb-2026
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s\d{1,2},?\s\d{2,4}\b",  # Feb 12, 2026
]

MIN_TEXT_LENGTH_FOR_RECEIPT = 15  # Very short/empty OCR output => not a receipt.
MIN_KEYWORD_MATCHES_FOR_RECEIPT = 1  # At least one receipt-ish keyword must appear.


def run_ocr(preprocessed_image: np.ndarray) -> str:
    """
    Run Tesseract OCR on a pre-processed (grayscale/binary) image.

    Args:
        preprocessed_image: Output of utils.preprocess_for_ocr().

    Returns:
        Raw extracted text (may be empty if nothing is readable).
    """
    # --psm 6 tells Tesseract to assume a single uniform block of text,
    # which works well for the columnar layout of most receipts.
    custom_config = r"--oem 3 --psm 6"
    text = pytesseract.image_to_string(preprocessed_image, config=custom_config)
    return text


def looks_like_receipt(raw_text: str) -> bool:
    """
    Heuristic check: does this OCR text look like it came from a receipt?

    We don't have a cloud classifier, so we rely on simple, explainable
    signals:
      - There must be a reasonable amount of readable text.
      - The text should contain at least one common receipt keyword
        (total, tax, invoice, etc.) OR at least one currency/amount pattern.

    Args:
        raw_text: Text returned by run_ocr().

    Returns:
        True if the text plausibly represents a receipt, False otherwise.
    """
    if not raw_text or len(raw_text.strip()) < MIN_TEXT_LENGTH_FOR_RECEIPT:
        return False

    lower_text = raw_text.lower()

    keyword_hits = sum(1 for kw in RECEIPT_KEYWORDS if kw in lower_text)
    has_amount_pattern = re.search(AMOUNT_PATTERN, raw_text) is not None

    if keyword_hits >= MIN_KEYWORD_MATCHES_FOR_RECEIPT and has_amount_pattern:
        return True

    # Fallback: even without keyword hits, multiple currency-like numbers
    # stacked in a short document strongly suggests a price list / receipt.
    amount_matches = re.findall(AMOUNT_PATTERN, raw_text)
    if len(amount_matches) >= 3:
        return True

    return False


def extract_vendor(raw_text: str) -> Optional[str]:
    """
    Guess the vendor/store name.

    Heuristic: the vendor name is almost always in the first few lines of a
    receipt, printed in the largest font (often ALL CAPS). We scan the first
    handful of non-empty lines and skip ones that look like an address,
    phone number, date, or a line that's just numbers/symbols.

    Args:
        raw_text: Raw OCR text.

    Returns:
        Best-guess vendor name, or None if nothing plausible was found.
    """
    lines: List[str] = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]

    address_hint_pattern = re.compile(
        r"(street|st\.|road|rd\.|avenue|ave\.|block|floor|sector|pin\s?code|"
        r"zip|phone|tel|mobile|www\.|http|@|gstin|gst no|vat no)",
        re.IGNORECASE,
    )
    mostly_digits_pattern = re.compile(r"^[\d\s\-\/.,:;#()]+$")

    for line in lines[:6]:  # vendor name is almost always near the very top
        if len(line) < 2:
            continue
        if address_hint_pattern.search(line):
            continue
        if mostly_digits_pattern.match(line):
            continue
        if re.search(AMOUNT_PATTERN, line) and len(line) < 6:
            continue

        # Clean up stray OCR noise characters at line edges.
        cleaned = re.sub(r"^[^A-Za-z0-9]+|[^A-Za-z0-9]+$", "", line)
        if cleaned:
            return cleaned

    return None


def extract_date(raw_text: str) -> Optional[str]:
    """
    Find the receipt date using a list of common date regex patterns.

    Args:
        raw_text: Raw OCR text.

    Returns:
        The first matching date string found, or None if no date pattern matched.
    """
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            return match.group().strip()
    return None


def _parse_amount_value(amount_str: str) -> float:
    """
    Convert a matched amount string like '₹1,234.50' into a float (1234.50)
    so multiple candidate amounts can be compared numerically.
    """
    numeric_part = re.sub(r"[^\d.]", "", amount_str.replace(",", ""))
    try:
        return float(numeric_part) if numeric_part else -1.0
    except ValueError:
        return -1.0


def extract_total(raw_text: str) -> Optional[str]:
    """
    Find the total amount paid on the receipt.

    Strategy:
      1. Look line-by-line for a line containing a "total-like" keyword
         (grand total, total amount, subtotal, etc.) and pull the amount
         from that same line. Keywords are checked in priority order so
         "grand total" wins over a plain "total" if both exist.
      2. If no keyword line has a valid amount, fall back to the largest
         currency-like number found anywhere in the text (commonly the
         final/highest value on a receipt).

    Args:
        raw_text: Raw OCR text.

    Returns:
        Best-guess total amount as a string (keeping its currency symbol
        if present), or None if nothing plausible was found.
    """
    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
    lower_lines = [ln.lower() for ln in lines]

    for keyword in TOTAL_KEYWORDS:
        for line, lower_line in zip(lines, lower_lines):
            if keyword in lower_line:
                match = re.search(AMOUNT_PATTERN, line)
                if match:
                    return match.group().strip()

    # Fallback: pick the largest amount-like number anywhere in the receipt,
    # since the total is usually the biggest/last value printed.
    all_amounts = re.findall(AMOUNT_PATTERN, raw_text)
    if all_amounts:
        best = max(all_amounts, key=_parse_amount_value)
        if _parse_amount_value(best) > 0:
            return best.strip()

    return None


def extract_receipt_data(preprocessed_image: np.ndarray) -> dict:
    """
    Main entry point used by app.py.

    Runs OCR, verifies the image looks like a receipt, then parses out the
    vendor, date, and total using regular expressions.

    Args:
        preprocessed_image: Output of utils.preprocess_for_ocr().

    Returns:
        On success:  {"success": True, "vendor": ..., "date": ..., "total": ...}
        On failure:  {"success": False, "message": "Receipt not detected."}
    """
    raw_text = run_ocr(preprocessed_image)

    if not looks_like_receipt(raw_text):
        return {"success": False, "message": "Receipt not detected."}

    vendor = extract_vendor(raw_text)
    date = extract_date(raw_text)
    total = extract_total(raw_text)

    # Even if it "looks like" a receipt, if we truly found nothing useful,
    # it's more honest to tell the user we couldn't detect a receipt
    # than to return an empty/garbage JSON.
    if not vendor and not date and not total:
        return {"success": False, "message": "Receipt not detected."}

    return {
        "success": True,
        "vendor": vendor or "Not found",
        "date": date or "Not found",
        "total": total or "Not found",
    }
