"""Parser service for extracting structured financial data from raw OCR text."""
import re
from dataclasses import dataclass


@dataclass
class ParsedResult:
    merchant_name: str | None
    date: str | None
    amount: str | None
    category: str | None


KEYWORD_RULES: dict[str, list[str]] = {
    "Food & Dining": [
        "coffee", "tea", "restaurant", "cafe", "burger", "pizza",
        "sushi", "bakery", "diner", "grill", "bistro", "takeaway", "takeout",
    ],
    "Transport": [
        "uber", "lyft", "taxi", "bus", "train", "metro", "subway",
        "fuel", "petrol", "parking", "toll",
    ],
    "Groceries": [
        "supermarket", "grocery", "groceries", "market", "tesco",
        "sainsbury", "waitrose", "aldi", "lidl", "asda",
    ],
    "Health": [
        "pharmacy", "chemist", "doctor", "clinic", "hospital",
        "dental", "optician", "prescription",
    ],
    "Entertainment": [
        "cinema", "theatre", "theater", "concert", "museum",
        "netflix", "spotify", "amazon prime", "disney",
    ],
    "Shopping": [
        "amazon", "ebay", "clothing", "fashion", "shoes",
        "electronics", "department store",
    ],
}

DATE_PATTERNS = [
    r"(?<!\d)\d{4}-\d{2}-\d{2}(?!\d)",   # YYYY-MM-DD
    r"(?<!\d)\d{2}/\d{2}/\d{4}(?!\d)",   # DD/MM/YYYY or MM/DD/YYYY
    r"(?<!\d)\d{2}-\d{2}-\d{4}(?!\d)",   # DD-MM-YYYY
]

AMOUNT_PATTERN = r"[£$€]?\s*(\d+\.\d{2})"


def _extract_merchant(lines: list[str]) -> str | None:
    candidates = [line.strip() for line in lines if line.strip()]
    for candidate in candidates[:2]:
        if len(candidate) >= 3:
            return candidate
    return None


def _extract_date(text: str) -> str | None:
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return match.group()
    return None


def _extract_amount(text: str) -> str | None:
    matches = re.findall(AMOUNT_PATTERN, text)
    if not matches:
        return None
    return str(max(float(m) for m in matches))


def _categorise(text: str) -> str:
    lower = text.lower()
    earliest: tuple[int, str] | None = None
    for category, keywords in KEYWORD_RULES.items():
        for kw in keywords:
            idx = lower.find(kw)
            if idx != -1:
                if earliest is None or idx < earliest[0]:
                    earliest = (idx, category)
    return earliest[1] if earliest else "Other"


def parse_receipt(raw_text: str) -> ParsedResult:
    if not raw_text or not raw_text.strip():
        return ParsedResult(merchant_name=None, date=None, amount=None, category=None)
    lines = raw_text.splitlines()
    return ParsedResult(
        merchant_name=_extract_merchant(lines),
        date=_extract_date(raw_text),
        amount=_extract_amount(raw_text),
        category=_categorise(raw_text),
    )
