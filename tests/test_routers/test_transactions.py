"""Unit and property-based tests for POST /transactions/upload/."""
import io
import struct
import zlib
from unittest.mock import patch

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

# ---------------------------------------------------------------------------
# Minimal valid image byte helpers
# ---------------------------------------------------------------------------

# Minimal valid JPEG (1x1 white pixel)
MINIMAL_JPEG = bytes([
    0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
    0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
    0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
    0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
    0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
    0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
    0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
    0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
    0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00,
    0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
    0x09, 0x0A, 0x0B, 0xFF, 0xC4, 0x00, 0xB5, 0x10, 0x00, 0x02, 0x01, 0x03,
    0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04, 0x04, 0x00, 0x00, 0x01, 0x7D,
    0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12, 0x21, 0x31, 0x41, 0x06,
    0x13, 0x51, 0x61, 0x07, 0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xA1, 0x08,
    0x23, 0x42, 0xB1, 0xC1, 0x15, 0x52, 0xD1, 0xF0, 0x24, 0x33, 0x62, 0x72,
    0x82, 0x09, 0x0A, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x25, 0x26, 0x27, 0x28,
    0x29, 0x2A, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x43, 0x44, 0x45,
    0x46, 0x47, 0x48, 0x49, 0x4A, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59,
    0x5A, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A, 0x73, 0x74, 0x75,
    0x76, 0x77, 0x78, 0x79, 0x7A, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89,
    0x8A, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9A, 0xA2, 0xA3, 0xA4,
    0xA5, 0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xB2, 0xB3, 0xB4, 0xB5, 0xB6, 0xB7,
    0xB8, 0xB9, 0xBA, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8, 0xC9, 0xCA,
    0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9, 0xDA, 0xE1, 0xE2, 0xE3,
    0xE4, 0xE5, 0xE6, 0xE7, 0xE8, 0xE9, 0xEA, 0xF1, 0xF2, 0xF3, 0xF4, 0xF5,
    0xF6, 0xF7, 0xF8, 0xF9, 0xFA, 0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01, 0x00,
    0x00, 0x3F, 0x00, 0xFB, 0xD2, 0x8A, 0x28, 0x03, 0xFF, 0xD9,
])


def _make_png(width: int = 1, height: int = 1) -> bytes:
    """Build a minimal valid PNG with the given dimensions (grayscale)."""
    def chunk(name: bytes, data: bytes) -> bytes:
        c = struct.pack(">I", len(data)) + name + data
        return c + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF)

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    ihdr = chunk(b"IHDR", ihdr_data)
    raw_row = b"\x00" + b"\xFF" * width
    raw_data = raw_row * height
    idat = chunk(b"IDAT", zlib.compress(raw_data))
    iend = chunk(b"IEND", b"")
    return signature + ihdr + idat + iend


MINIMAL_PNG = _make_png()

# ---------------------------------------------------------------------------
# Unit tests — 4.1
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_upload_valid_jpeg_returns_200(client_connected):
    """Valid JPEG upload → HTTP 200 with all six response fields."""
    with patch("app.routers.transactions.extract_text", return_value="Starbucks\n2024-01-15\nTotal £4.50\ncoffee"):
        response = await client_connected.post(
            "/transactions/upload/",
            files={"file": ("receipt.jpg", io.BytesIO(MINIMAL_JPEG), "image/jpeg")},
        )
    assert response.status_code == 200
    body = response.json()
    # All six fields must be present
    assert "file_path" in body
    assert "raw_text" in body
    assert "merchant" in body
    assert "date" in body
    assert "amount" in body
    assert "category" in body
    assert isinstance(body["file_path"], str)
    assert isinstance(body["raw_text"], str)


@pytest.mark.asyncio
async def test_upload_txt_file_returns_400(client_connected):
    """Uploading a .txt file → HTTP 400."""
    response = await client_connected.post(
        "/transactions/upload/",
        files={"file": ("document.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_blank_image_returns_200_empty_raw_text(client_connected):
    """Blank image with mocked extract_text returning '' → HTTP 200, raw_text == '', parsed fields null."""
    with patch("app.routers.transactions.extract_text", return_value=""):
        response = await client_connected.post(
            "/transactions/upload/",
            files={"file": ("blank.jpg", io.BytesIO(MINIMAL_JPEG), "image/jpeg")},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["raw_text"] == ""
    assert body["merchant"] is None
    assert body["date"] is None
    assert body["amount"] is None
    assert body["category"] is None


# ---------------------------------------------------------------------------
# Property 1: Valid image uploads return required response fields
# Feature: smart-personal-cfo, Property 1: Valid image uploads return required response fields
# Validates: Requirements 1.2, 1.5, 4.1
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(mime=st.sampled_from(["image/jpeg", "image/png"]))
async def test_property_1_valid_image_uploads_return_required_fields(mime, client_connected):
    """Property 1: Valid JPEG/PNG uploads → HTTP 200 with file_path (str) and raw_text (str)."""
    if mime == "image/jpeg":
        img_bytes = MINIMAL_JPEG
        filename = "test.jpg"
    else:
        img_bytes = MINIMAL_PNG
        filename = "test.png"

    with patch("app.routers.transactions.extract_text", return_value=""):
        response = await client_connected.post(
            "/transactions/upload/",
            files={"file": (filename, io.BytesIO(img_bytes), mime)},
        )
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body.get("file_path"), str)
    assert isinstance(body.get("raw_text"), str)


# ---------------------------------------------------------------------------
# Property 2: Unsupported MIME types are rejected
# Feature: smart-personal-cfo, Property 2: Unsupported MIME types are rejected
# Validates: Requirements 1.3
# ---------------------------------------------------------------------------

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}

_mime_alphabet = st.text(
    alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"), whitelist_characters="/-+."),
    min_size=1,
    max_size=40,
).filter(lambda s: s not in ALLOWED_MIME_TYPES)


@pytest.mark.asyncio
@settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(bad_mime=_mime_alphabet)
async def test_property_2_unsupported_mime_types_rejected(bad_mime, client_connected):
    """Property 2: Any MIME type outside {image/jpeg, image/png} → HTTP 400."""
    response = await client_connected.post(
        "/transactions/upload/",
        files={"file": ("file.bin", io.BytesIO(b"\x00"), bad_mime)},
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Property 3: Uploaded files are persisted with correct extension
# Feature: smart-personal-cfo, Property 3: Uploaded files are persisted with correct extension
# Validates: Requirements 2.1, 2.4, 2.5
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(ext_and_mime=st.sampled_from([(".jpg", "image/jpeg"), (".png", "image/png")]))
async def test_property_3_file_persisted_with_correct_extension(ext_and_mime, client_connected):
    """Property 3: file_path ends with correct extension and file exists on disk."""
    from pathlib import Path
    ext, mime = ext_and_mime
    img_bytes = MINIMAL_JPEG if mime == "image/jpeg" else MINIMAL_PNG

    with patch("app.routers.transactions.extract_text", return_value=""):
        response = await client_connected.post(
            "/transactions/upload/",
            files={"file": (f"upload{ext}", io.BytesIO(img_bytes), mime)},
        )
    assert response.status_code == 200
    file_path = response.json()["file_path"]
    assert file_path.endswith(ext), f"Expected extension {ext}, got {file_path}"
    assert Path(file_path).exists(), f"File not found on disk: {file_path}"


# ---------------------------------------------------------------------------
# Property 4: Concurrent uploads produce unique file paths
# Feature: smart-personal-cfo, Property 4: Concurrent uploads produce unique file paths
# Validates: Requirements 2.2
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_property_4_unique_filenames(client_connected):
    """Property 4: Uploading the same image N>=10 times yields all distinct file_path values."""
    n = 10
    paths = []
    with patch("app.routers.transactions.extract_text", return_value=""):
        for _ in range(n):
            response = await client_connected.post(
                "/transactions/upload/",
                files={"file": ("receipt.jpg", io.BytesIO(MINIMAL_JPEG), "image/jpeg")},
            )
            assert response.status_code == 200
            paths.append(response.json()["file_path"])

    assert len(paths) == len(set(paths)), "Duplicate file paths detected across uploads"


# ---------------------------------------------------------------------------
# Property 7: Upload endpoint always returns HTTP 200 with all six response fields
# Feature: smart-personal-cfo, Property 7: Upload endpoint always returns HTTP 200 with all six response fields for valid images
# Validates: Requirements 6.1, 6.2, 6.4, 7.1
# ---------------------------------------------------------------------------

_SIX_FIELDS = {"file_path", "raw_text", "merchant", "date", "amount", "category"}


@pytest.mark.asyncio
@settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(ext_and_mime=st.sampled_from([(".jpg", "image/jpeg"), (".png", "image/png")]))
async def test_property_7_upload_returns_all_six_fields(ext_and_mime, client_connected):
    """Property 7: Valid JPEG/PNG upload → HTTP 200 and all six fields present in response JSON."""
    ext, mime = ext_and_mime
    img_bytes = MINIMAL_JPEG if mime == "image/jpeg" else MINIMAL_PNG

    with patch("app.routers.transactions.extract_text", return_value=""):
        response = await client_connected.post(
            "/transactions/upload/",
            files={"file": (f"receipt{ext}", io.BytesIO(img_bytes), mime)},
        )
    assert response.status_code == 200
    body = response.json()
    assert _SIX_FIELDS.issubset(body.keys()), (
        f"Missing fields: {_SIX_FIELDS - body.keys()}"
    )
    # file_path and raw_text must be strings
    assert isinstance(body["file_path"], str)
    assert isinstance(body["raw_text"], str)
    # parsed fields must be str or null
    for field in ("merchant", "date", "amount", "category"):
        assert body[field] is None or isinstance(body[field], str), (
            f"Field '{field}' has unexpected type: {type(body[field])}"
        )
