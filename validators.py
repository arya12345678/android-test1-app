# -*- coding: utf-8 -*-
"""
Form input validation and conversion helpers.

These functions are completely independent of the GUI so they can be
tested on their own. Note: Persian/Arabic digits (e.g. entered by an IME
or pasted from elsewhere) are still normalized to ASCII digits in numeric
and date inputs, just in case.
"""

import datetime

_PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
_ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
_ASCII_DIGITS = "0123456789"

_DIGIT_TRANSLATION = {}
for _fa, _ar, _en in zip(_PERSIAN_DIGITS, _ARABIC_DIGITS, _ASCII_DIGITS):
    _DIGIT_TRANSLATION[_fa] = _en
    _DIGIT_TRANSLATION[_ar] = _en


class ValidationError(Exception):
    """Validation error with a user-facing message."""


def normalize_digits(text):
    """Converts Persian/Arabic digits in a string to ASCII digits."""
    if text is None:
        return text
    return "".join(_DIGIT_TRANSLATION.get(ch, ch) for ch in text)


def require_text(value, field_label):
    """Ensures a required text field isn't empty."""
    if value is None or not str(value).strip():
        raise ValidationError(f'"{field_label}" cannot be empty')
    return str(value).strip()


def parse_int(value, field_label, allow_empty=False, default=0, min_value=None):
    """
    Converts a string to an integer (with Persian digit support).
    If allow_empty=True and the input is empty, `default` is returned.
    """
    if value is None:
        value = ""
    text = normalize_digits(str(value)).strip()
    if not text:
        if allow_empty:
            return default
        raise ValidationError(f'"{field_label}" cannot be empty')
    try:
        result = int(text)
    except ValueError:
        raise ValidationError(f'"{field_label}" must be a whole number')
    if min_value is not None and result < min_value:
        raise ValidationError(f'"{field_label}" cannot be less than {min_value}')
    return result


def parse_float(value, field_label, allow_empty=True, default=None, min_value=None):
    """
    Converts a string to a float (with Persian digit support and ','
    treated as a thousands separator).
    """
    if value is None:
        value = ""
    text = normalize_digits(str(value)).strip().replace(",", "")
    if not text:
        if allow_empty:
            return default
        raise ValidationError(f'"{field_label}" cannot be empty')
    try:
        result = float(text)
    except ValueError:
        raise ValidationError(f'"{field_label}" must be a number')
    if min_value is not None and result < min_value:
        raise ValidationError(f'"{field_label}" cannot be less than {min_value}')
    return result


def parse_date(value, field_label, allow_empty=True):
    """
    Validates a date in YYYY-MM-DD format (simple and sorts correctly as
    text in the database). Persian digits are accepted too. If empty and
    allow_empty=True, today's date is returned.
    """
    if value is None:
        value = ""
    text = normalize_digits(str(value)).strip()
    if not text:
        if allow_empty:
            return datetime.date.today().isoformat()
        raise ValidationError(f'"{field_label}" cannot be empty')
    try:
        parsed = datetime.datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError(
            f'"{field_label}" must be in YYYY-MM-DD format, e.g. 2026-01-15'
        )
    return parsed.isoformat()


def validate_component_form(raw, technical_field_defs):
    """
    Validates the form's raw input (a dict of strings) and converts it
    into a clean dict ready for database.add_component / update_component.

    `raw` has the following keys (as strings, exactly as they come from
    the form):
        name, category_id, quantity, location, price, currency,
        entry_date, notes, low_stock_threshold,
        technical_data (already a dict, key -> raw string)

    `technical_field_defs`: the list of technical field definitions for
        the selected category (the output of database.get_technical_fields),
        needed to know each field's type (currently only used to keep
        "select"-type fields consistent; technical fields are optional
        by design).

    Returns: a clean, ready dict, or raises ValidationError with a
    suitable message.
    """
    result = {}
    result["name"] = require_text(raw.get("name"), "Component Name")
    result["category_id"] = raw.get("category_id") or None
    result["quantity"] = parse_int(
        raw.get("quantity"), "Quantity", allow_empty=True, default=0, min_value=0
    )
    result["location"] = (raw.get("location") or "").strip()
    result["price"] = parse_float(
        raw.get("price"), "Price", allow_empty=True, default=None, min_value=0
    )
    result["currency"] = (raw.get("currency") or "USD").strip()
    result["entry_date"] = parse_date(raw.get("entry_date"), "Entry Date", allow_empty=True)
    result["notes"] = (raw.get("notes") or "").strip() or None
    result["low_stock_threshold"] = parse_int(
        raw.get("low_stock_threshold"), "Low Stock Threshold",
        allow_empty=True, default=5, min_value=0,
    )

    tech_data_raw = raw.get("technical_data") or {}
    tech_data_clean = {}
    for field in technical_field_defs or []:
        key = field["key"]
        val = tech_data_raw.get(key)
        if val is not None and str(val).strip():
            tech_data_clean[key] = normalize_digits(str(val).strip())
    result["technical_data"] = tech_data_clean

    return result
