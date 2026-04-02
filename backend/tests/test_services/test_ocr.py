"""Unit and property-based tests for app/services/ocr.py."""
import io
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image
from hypothesis import given, settings
from hypothesis import strategies as st

from app.services.ocr import extract_text


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_image_file(tmp_path: Path, text: str = "", fmt: str = "PNG") -> Path:
    """Create a minimal image file on disk and return its path."""
    img = Image.new("RGB", (200, 50), color=(255, 255, 255))
    suffix = ".png" if fmt == "PNG" else ".jpg"
    dest = tmp_path / f"test_image{suffix}"
    img.save(dest, format=fmt)
    return dest


# ---------------------------------------------------------------------------
# Unit tests — 2.1
# ---------------------------------------------------------------------------

class TestExtractTextHappyPath:
    def test_returns_string_for_valid_image(self, tmp_path):
        """extract_text returns a str for a valid image (Req 3.1, 3.2)."""
        img_path = _make_image_file(tmp_path)
        with patch("pytesseract.image_to_string", return_value="Hello World\n"):
            result = extract_text(str(img_path))
        assert isinstance(result, str)
        assert result == "Hello World\n"

    def test_returns_empty_or_whitespace_for_blank_image(self, tmp_path):
        """Blank white image produces empty or whitespace-only text (Req 3.5)."""
        img_path = _make_image_file(tmp_path)
        # Tesseract returns "\n\x0c" for blank images; we mock that here
        with patch("pytesseract.image_to_string", return_value="\n\x0c"):
            result = extract_text(str(img_path))
        assert result.strip() == ""


class TestExtractTextErrorCases:
    def test_raises_file_not_found_for_missing_path(self, tmp_path):
        """extract_text raises FileNotFoundError for a non-existent path (Req 3.3)."""
        missing = str(tmp_path / "does_not_exist.png")
        with pytest.raises(FileNotFoundError) as exc_info:
            extract_text(missing)
        assert missing in str(exc_info.value)

    def test_raises_runtime_error_when_tesseract_missing(self, tmp_path):
        """extract_text raises RuntimeError when Tesseract is not installed (Req 3.4)."""
        img_path = _make_image_file(tmp_path)
        with patch(
            "pytesseract.image_to_string",
            side_effect=Exception("tesseract is not installed"),
        ):
            # Patch TesseractNotFoundError to be the same exception class so
            # our handler catches it.
            import pytesseract as _pt
            original_exc = _pt.TesseractNotFoundError

            class _FakeTesseractNotFoundError(Exception):
                pass

            with patch.object(_pt, "TesseractNotFoundError", _FakeTesseractNotFoundError):
                with patch(
                    "pytesseract.image_to_string",
                    side_effect=_FakeTesseractNotFoundError("not found"),
                ):
                    with pytest.raises(RuntimeError) as exc_info:
                        extract_text(str(img_path))
                    assert "Tesseract" in str(exc_info.value)
                    assert "install" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# Property-based test — 2.2  (Property 5)
# ---------------------------------------------------------------------------

# Feature: smart-personal-cfo, Property 5: OCR service raises FileNotFoundError for missing files
@given(st.text(min_size=1))
@settings(max_examples=100)
def test_extract_text_raises_file_not_found_for_arbitrary_paths(path_str: str):
    """Property 5: For any path string that does not exist on disk,
    extract_text must raise FileNotFoundError.

    Validates: Requirements 3.3
    """
    # Ensure the path does not accidentally exist
    if Path(path_str).exists():
        return  # skip the rare case where the generated string is a real path

    with pytest.raises(FileNotFoundError):
        extract_text(path_str)
