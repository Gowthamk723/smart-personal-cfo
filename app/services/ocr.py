from pathlib import Path

from PIL import Image
import pytesseract


def extract_text(file_path: str) -> str:
    """Extract raw text from an image file using Tesseract OCR.

    Args:
        file_path: Path to the image file (JPEG or PNG).

    Returns:
        Raw text extracted by Tesseract, or an empty string if no text is found.

    Raises:
        FileNotFoundError: If the file at the given path does not exist.
        RuntimeError: If Tesseract is not installed or not found on PATH.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {file_path}")
    try:
        image = Image.open(path)
        return pytesseract.image_to_string(image)
    except pytesseract.TesseractNotFoundError as exc:
        raise RuntimeError(
            "Tesseract is not installed or not found on PATH. "
            "Install it via your OS package manager."
        ) from exc
