"""
utils.py
--------
Small helper functions used by app.py and receipt_extractor.py.

Responsibilities of this file:
1. Validate that an uploaded file has an allowed extension (jpg/jpeg/png).
2. Safely load raw upload bytes into a Pillow Image (and catch corrupted files).
3. Convert a Pillow Image into an OpenCV (numpy) image.
4. Pre-process the image (grayscale, denoise, threshold) to make OCR more accurate.

Keeping these as small, single-purpose functions makes the code easy to test
and easy to read for beginners.
"""

import io
import numpy as np
import cv2
from PIL import Image, UnidentifiedImageError

# Only these file extensions are accepted by the API.
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}


def is_allowed_extension(filename: str) -> bool:
    """
    Check whether the uploaded file's name ends with an allowed extension.

    Args:
        filename: The original filename sent by the client (e.g. "bill.jpg").

    Returns:
        True if the extension is jpg/jpeg/png (case-insensitive), else False.
    """
    if not filename or "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[-1].lower()
    return extension in ALLOWED_EXTENSIONS


def load_image_from_bytes(file_bytes: bytes) -> Image.Image:
    """
    Convert raw uploaded bytes into a Pillow Image object.

    This is where we detect "corrupted image" uploads: if the bytes are not
    a valid image, Pillow raises UnidentifiedImageError, which we convert
    into a ValueError with a friendly message so app.py can turn it into a
    clean HTTP error response.

    Args:
        file_bytes: Raw bytes read from the uploaded file.

    Returns:
        A Pillow Image object in RGB mode.

    Raises:
        ValueError: If the bytes are empty or not a valid/decodable image.
    """
    if not file_bytes:
        raise ValueError("Uploaded file is empty.")

    try:
        image = Image.open(io.BytesIO(file_bytes))
        # Force Pillow to actually decode the pixel data now (not lazily),
        # so that truncated/corrupted files fail here instead of later.
        image.load()
    except (UnidentifiedImageError, OSError):
        raise ValueError("Uploaded file is not a valid or readable image.")

    # Normalize to RGB so downstream OpenCV conversion is consistent
    # (handles PNGs with alpha channels, grayscale images, etc.)
    if image.mode != "RGB":
        image = image.convert("RGB")

    return image


def pil_to_cv2(image: Image.Image) -> np.ndarray:
    """
    Convert a Pillow (RGB) image into an OpenCV (BGR) numpy array.

    OpenCV internally expects BGR channel order, while Pillow uses RGB,
    so we must flip the channel order during conversion.
    """
    rgb_array = np.array(image)
    bgr_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
    return bgr_array


def preprocess_for_ocr(cv2_image: np.ndarray) -> np.ndarray:
    """
    Clean up a receipt photo so Tesseract can read it more reliably.

    Typical phone photos of receipts suffer from: uneven lighting, noise,
    and low contrast between text and paper. This pipeline:
      1. Converts to grayscale (OCR doesn't need color).
      2. Removes noise using a fast non-local-means denoiser.
      3. Applies adaptive thresholding to turn the image into crisp black
         text on a white background, which Tesseract handles best.

    Args:
        cv2_image: BGR image as loaded by pil_to_cv2().

    Returns:
        A single-channel (grayscale) binary image ready for pytesseract.
    """
    gray = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2GRAY)

    # Denoise while preserving edges/text strokes.
    denoised = cv2.fastNlMeansDenoising(gray, h=15)

    # Adaptive threshold handles receipts photographed under uneven light
    # better than a single global threshold value would.
    binary = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=31,
        C=15,
    )

    return binary
