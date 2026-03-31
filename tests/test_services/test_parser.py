"""Unit and property-based tests for app/services/parser.py."""
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.services.parser import ParsedResult, parse_receipt, KEYWORD_RULES


# ---------------------------------------------------------------------------
# Unit tests — Task 1.1
# ---------------------------------------------------------------------------

class TestParseReceiptEmptyInput:
    def test_empty_string_returns_all_none(self):
        result = parse_receipt("")
        assert result.merchant_name is None
        assert result.date is None
        assert result.amount is None
        assert result.category is None

    def test_whitespace_only_returns_all_none(self):
        result = parse_receipt("  \n  ")
        assert result.merchant_name is None
        assert result.date is None
        assert result.amount is None
        assert result.category is None

    def test_newlines_only_returns_all_none(self):
        result = parse_receipt("\n\n\n")
        assert result.merchant_name is None
        assert result.date is None
        assert result.amount is None
        assert result.category is None


class TestParseReceiptHappyPath:
    def test_full_receipt_extracts_all_fields(self):
        text = "Starbucks\n2024-01-15\nTotal £4.50\ncoffee"
        result = parse_receipt(text)
        assert result.merchant_name == "Starbucks"
        assert result.date == "2024-01-15"
        assert result.amount == "4.5"
        assert result.category == "Food & Dining"

    def test_merchant_is_first_non_empty_line_stripped(self):
        result = parse_receipt("  Costa Coffee  \n2024-03-01\n£2.50\ncoffee")
        assert result.merchant_name == "Costa Coffee"

    def test_merchant_falls_back_to_second_line_when_first_too_short(self):
        result = parse_receipt("AB\nMcDonalds\n2024-01-01\n£5.99\nburger")
        assert result.merchant_name == "McDonalds"

    def test_merchant_none_when_no_line_has_3_chars(self):
        result = parse_receipt("AB\nCD\n2024-01-01")
        assert result.merchant_name is None


class TestParseReceiptDateExtraction:
    def test_iso_date_format(self):
        result = parse_receipt("Shop\n2024-06-15\n£10.00")
        assert result.date == "2024-06-15"

    def test_dd_mm_yyyy_format(self):
        result = parse_receipt("Shop\n15/06/2024\n£10.00")
        assert result.date == "15/06/2024"

    def test_dd_mm_yyyy_dash_format(self):
        result = parse_receipt("Shop\n15-06-2024\n£10.00")
        assert result.date == "15-06-2024"

    def test_no_date_returns_none(self):
        result = parse_receipt("Starbucks\ncoffee £4.50")
        assert result.date is None

    def test_iso_date_takes_priority_over_other_formats(self):
        # ISO pattern is tried first
        result = parse_receipt("2024-01-15 and 15/01/2024")
        assert result.date == "2024-01-15"


class TestParseReceiptAmountExtraction:
    def test_single_amount(self):
        result = parse_receipt("Shop\n£12.50")
        assert result.amount == "12.5"

    def test_largest_amount_returned(self):
        result = parse_receipt("Item 1: £3.99\nItem 2: £7.50\nTotal: £11.49")
        assert result.amount == "11.49"

    def test_amount_without_currency_symbol(self):
        result = parse_receipt("Shop\n9.99")
        assert result.amount == "9.99"

    def test_dollar_and_euro_symbols(self):
        result = parse_receipt("$5.00 and €8.00")
        assert result.amount == "8.0"

    def test_no_amount_returns_none(self):
        result = parse_receipt("Starbucks\ncoffee")
        assert result.amount is None


class TestParseReceiptCategorisation:
    def test_no_keyword_returns_other(self):
        result = parse_receipt("XYZ Corp\n2024-01-01\n£50.00")
        assert result.category == "Other"

    def test_food_keyword(self):
        result = parse_receipt("Local Cafe\ncoffee £3.50")
        assert result.category == "Food & Dining"

    def test_transport_keyword(self):
        result = parse_receipt("City Parking\nparking £8.00")
        assert result.category == "Transport"

    def test_groceries_keyword(self):
        result = parse_receipt("Tesco Express\ntesco £25.00")
        assert result.category == "Groceries"

    def test_earliest_keyword_wins(self):
        # "uber" (Transport) appears before "coffee" (Food & Dining)
        result = parse_receipt("uber coffee shop £5.00")
        assert result.category == "Transport"

    def test_earliest_keyword_wins_reversed(self):
        # "coffee" (Food & Dining) appears before "uber" (Transport)
        result = parse_receipt("coffee uber £5.00")
        assert result.category == "Food & Dining"

    def test_case_insensitive_matching(self):
        result = parse_receipt("COFFEE shop £3.00")
        assert result.category == "Food & Dining"


# ---------------------------------------------------------------------------
# Property-based tests
# ---------------------------------------------------------------------------

# Feature: smart-personal-cfo, Property 1: Empty input returns all-None result
# Use only characters that Python's str.strip() considers whitespace
_WHITESPACE_CHARS = " \t\n\r\x0b\x0c\xa0\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u202f\u205f\u3000"

@given(st.text(alphabet=st.sampled_from(list(_WHITESPACE_CHARS))))
@settings(max_examples=100)
def test_property1_whitespace_input_returns_all_none(text: str):
    """Property 1: For any whitespace-only string, parse_receipt returns all-None fields.
    Validates: Requirements 1.3
    """
    result = parse_receipt(text)
    assert result.merchant_name is None
    assert result.date is None
    assert result.amount is None
    assert result.category is None


# Feature: smart-personal-cfo, Property 2: Merchant extraction uses first substantial line, stripped of whitespace
@given(
    merchant=st.text(
        alphabet=st.characters(blacklist_categories=("Cc",)),  # no control chars (incl. \r, \n)
        min_size=3,
        max_size=50,
    ).filter(lambda s: s.strip() and len(s.strip()) >= 3),
    suffix=st.text(max_size=100),
)
@settings(max_examples=100)
def test_property2_merchant_extraction_first_substantial_line(merchant: str, suffix: str):
    """Property 2: First non-empty line with >= 3 chars becomes merchant_name (stripped).
    Validates: Requirements 2.1, 2.4
    """
    # Build text where the first non-empty line is `merchant`
    raw_text = merchant + "\n" + suffix
    result = parse_receipt(raw_text)
    assert result.merchant_name == merchant.strip()


# Feature: smart-personal-cfo, Property 3: Date extraction finds the first matching date and preserves its format
@given(
    date_str=st.one_of(
        # YYYY-MM-DD
        st.builds(
            lambda y, m, d: f"{y:04d}-{m:02d}-{d:02d}",
            y=st.integers(min_value=1000, max_value=9999),
            m=st.integers(min_value=1, max_value=12),
            d=st.integers(min_value=1, max_value=28),
        ),
        # DD/MM/YYYY
        st.builds(
            lambda y, m, d: f"{d:02d}/{m:02d}/{y:04d}",
            y=st.integers(min_value=1000, max_value=9999),
            m=st.integers(min_value=1, max_value=12),
            d=st.integers(min_value=1, max_value=28),
        ),
        # DD-MM-YYYY
        st.builds(
            lambda y, m, d: f"{d:02d}-{m:02d}-{y:04d}",
            y=st.integers(min_value=1000, max_value=9999),
            m=st.integers(min_value=1, max_value=12),
            d=st.integers(min_value=1, max_value=28),
        ),
    ),
    prefix=st.text(
        alphabet=st.characters(blacklist_categories=("Nd",), blacklist_characters="-/"),
        max_size=20,
    ),
    suffix=st.text(
        alphabet=st.characters(blacklist_categories=("Nd",), blacklist_characters="-/"),
        max_size=20,
    ),
)
@settings(max_examples=100)
def test_property3_date_extraction_preserves_format(date_str: str, prefix: str, suffix: str):
    """Property 3: Date extraction finds the first matching date and preserves its format.
    Validates: Requirements 3.1, 3.2, 3.4
    """
    # Wrap date with spaces to ensure no adjacent digits interfere
    raw_text = f"Merchant\n{prefix} {date_str} {suffix}"
    result = parse_receipt(raw_text)
    assert result.date == date_str


# Feature: smart-personal-cfo, Property 4: Amount extraction returns the largest currency value as a numeric string without symbol
@given(
    amounts=st.lists(
        st.floats(min_value=0.01, max_value=9999.99).map(lambda x: round(x, 2)),
        min_size=1,
        max_size=5,
    ),
)
@settings(max_examples=100)
def test_property4_amount_extraction_returns_largest(amounts: list[float]):
    """Property 4: Amount extraction returns the largest currency value as a numeric string.
    Validates: Requirements 4.1, 4.2, 4.4
    """
    # Build text with all amounts as bare decimals
    lines = [f"{a:.2f}" for a in amounts]
    raw_text = "Merchant\n" + "\n".join(lines)
    result = parse_receipt(raw_text)
    expected = str(max(amounts))
    assert result.amount == expected


# Feature: smart-personal-cfo, Property 5: Keyword categorization is case-insensitive
@given(
    category=st.sampled_from(list(KEYWORD_RULES.keys())),
)
@settings(max_examples=100)
def test_property5_categorisation_is_case_insensitive(category: str):
    """Property 5: Keyword categorization is case-insensitive.
    Validates: Requirements 5.1, 5.5
    """
    # Pick the first keyword for the category
    keyword = KEYWORD_RULES[category][0]

    # Generate a mixed-case version of the keyword
    mixed = "".join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(keyword))

    raw_text = f"Some receipt\n{mixed}\n£10.00"
    result = parse_receipt(raw_text)
    assert result.category == category


# Feature: smart-personal-cfo, Property 6: Earliest keyword wins when multiple categories match
@given(
    cat_a=st.sampled_from(list(KEYWORD_RULES.keys())),
    cat_b=st.sampled_from(list(KEYWORD_RULES.keys())),
)
@settings(max_examples=100)
def test_property6_earliest_keyword_wins(cat_a: str, cat_b: str):
    """Property 6: Earliest keyword wins when multiple categories match.
    Validates: Requirements 5.3
    """
    if cat_a == cat_b:
        return  # skip same-category pairs

    kw_a = KEYWORD_RULES[cat_a][0]
    kw_b = KEYWORD_RULES[cat_b][0]

    # Place kw_a before kw_b with a clear separator
    raw_text = f"{kw_a} then {kw_b}"
    result = parse_receipt(raw_text)

    # kw_a is at index 0, kw_b is later — cat_a should win
    assert result.category == cat_a
