# -*- coding: utf-8 -*-
"""
شماره‌ی شناسه‌ی یکتای هر قطعه.

هر قطعه از قبل یک شناسه‌ی عددی داخلی در دیتابیس دارد (ستون id). این ماژول
یک قالب نمایشی/قابل‌چاپ برای همان شناسه می‌سازد (مثلا EI-000042) که هم:
  - در جدول نتایج و جزئیات قطعه نمایش داده می‌شود،
  - در جعبه‌ی جستجو قابل تایپ‌کردن و پیداکردن دقیق قطعه است،
  - محتوای QR Code و بارکد هر قطعه همین کد است،
  - با اسکن بارکد/QR (که مثل تایپ‌کردن با صفحه‌کلید عمل می‌کند)، همین رشته
    وارد جعبه‌ی جستجو می‌شود و بلافاصله قطعه پیدا می‌شود.
"""

import re

CODE_PREFIX = "EI"  # مخفف Electronics Inventory
CODE_DIGITS = 6

_CODE_RE = re.compile(rf"^{CODE_PREFIX}-?(\d+)$", re.IGNORECASE)
_HASH_NUMBER_RE = re.compile(r"^#?(\d+)$")


def format_component_code(component_id):
    """شناسه‌ی عددی داخلی را به قالب نمایشی تبدیل می‌کند، مثلا 42 -> 'EI-000042'."""
    return f"{CODE_PREFIX}-{int(component_id):0{CODE_DIGITS}d}"


def parse_component_code(text):
    """
    یک رشته‌ی وارد‌شده توسط کاربر (یا اسکن‌شده از بارکد/QR) را می‌گیرد و اگر
    با شناسه‌ی یک قطعه مطابقت داشت، همان عدد شناسه‌ی داخلی (id) را برمی‌گرداند.
    قالب‌های پذیرفته‌شده: "EI-000042"، "EI000042"، "ei-42"، "42"، "#42".
    اگر متن با هیچ‌کدام از این قالب‌ها مطابقت نداشت، None برمی‌گرداند.
    """
    if not text:
        return None
    text = text.strip()

    m = _CODE_RE.match(text)
    if m:
        return int(m.group(1))

    m = _HASH_NUMBER_RE.match(text)
    if m:
        return int(m.group(1))

    return None
