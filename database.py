# -*- coding: utf-8 -*-
"""
لایه‌ی دسترسی به دیتابیس (SQLite) برای برنامه‌ی انبارداری قطعات الکترونیکی.

این ماژول هیچ وابستگی‌ای به رابط گرافیکی ندارد و کاملاً مستقل قابل تست است.
تمام عملیات دیتابیس (ساخت جدول‌ها، دسته‌بندی‌ها، قطعات، تاریخچه‌ی موجودی و
تنظیمات) در همین فایل قرار دارد.
"""

import sqlite3
import json
import os
import datetime

from categories import DEFAULT_CATEGORY_TREE
from component_code import parse_component_code
from category_translation_en import NAME_MAP as _EN_NAME_MAP, FIELD_MAP as _EN_FIELD_MAP

DB_FILENAME = "inventory.db"


def get_db_path(base_dir):
    """مسیر کامل فایل دیتابیس را برمی‌گرداند."""
    return os.path.join(base_dir, DB_FILENAME)


def get_connection(db_path):
    """یک اتصال جدید به دیتابیس برمی‌گرداند (با فعال بودن کلید خارجی)."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER,
    technical_fields TEXT NOT NULL DEFAULT '[]',
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER,
    quantity INTEGER NOT NULL DEFAULT 0,
    location TEXT,
    price REAL,
    currency TEXT DEFAULT 'USD',
    entry_date TEXT,
    image_path TEXT,
    datasheet_path TEXT,
    qr_path TEXT,
    barcode_path TEXT,
    notes TEXT,
    technical_data TEXT NOT NULL DEFAULT '{}',
    low_stock_threshold INTEGER DEFAULT 5,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS stock_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component_id INTEGER NOT NULL,
    change_amount INTEGER NOT NULL,
    resulting_quantity INTEGER NOT NULL,
    reason TEXT,
    date TEXT NOT NULL,
    FOREIGN KEY (component_id) REFERENCES components(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE INDEX IF NOT EXISTS idx_components_name ON components(name);
CREATE INDEX IF NOT EXISTS idx_components_category ON components(category_id);
CREATE INDEX IF NOT EXISTS idx_components_location ON components(location);
CREATE INDEX IF NOT EXISTS idx_history_component ON stock_history(component_id);
"""

DEFAULT_SETTINGS = {
    "default_currency": "USD",
    "default_low_stock_threshold": "5",
}


def init_db(db_path):
    """دیتابیس را می‌سازد (در صورت نبود) و دسته‌بندی‌های پیش‌فرض را بذرپاشی می‌کند."""
    is_new = not os.path.exists(db_path)
    conn = get_connection(db_path)
    try:
        conn.executescript(SCHEMA)
        if is_new:
            _seed_categories(conn)
            _seed_settings(conn)
        _migrate_schema(conn)
        _migrate_translate_seed_categories_to_english(conn)
        conn.commit()
    finally:
        conn.close()


def _migrate_schema(conn):
    """
    اضافه‌کردن ستون‌های جدیدی که در نسخه‌های بعدی برنامه اضافه شده‌اند، به
    دیتابیس‌هایی که از قبل (با نسخه‌ی قدیمی‌تر برنامه) ساخته شده‌اند - بدون
    از دست رفتن هیچ داده‌ای. CREATE TABLE IF NOT EXISTS به‌تنهایی ستون
    جدید را به جدول موجود اضافه نمی‌کند، پس این کار را اینجا انجام می‌دهیم.
    """
    existing_columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(components)")
    }
    if "barcode_path" not in existing_columns:
        conn.execute("ALTER TABLE components ADD COLUMN barcode_path TEXT")


def _migrate_translate_seed_categories_to_english(conn):
    """
    One-time migration: translate the built-in default categories (and their
    technical field labels/options) from the original Persian seed data to
    the current English seed data, for databases created before the app's
    UI was translated to English.

    Only categories/fields whose current text EXACTLY matches the original
    Persian default are touched, so anything the user renamed or added
    themselves is left completely alone. Runs only once, tracked via a
    settings flag.
    """
    if get_setting(conn, "categories_translated_en") == "1":
        return

    rows = conn.execute("SELECT id, name, technical_fields FROM categories").fetchall()
    for row in rows:
        old_name = row["name"]
        new_name = _EN_NAME_MAP.get(old_name)
        if new_name is None:
            continue  # این دسته یا از قبل انگلیسی است یا کاربر خودش ساخته/تغییر داده

        field_defs = _EN_FIELD_MAP.get(new_name, [])
        translation_by_key = {f["key"]: f for f in field_defs}

        try:
            current_fields = json.loads(row["technical_fields"])
        except (TypeError, ValueError):
            current_fields = []

        updated_fields = []
        for field in current_fields:
            translation = translation_by_key.get(field.get("key"))
            if translation and field.get("label") == translation["old_label"]:
                new_field = dict(field)
                new_field["label"] = translation["new_label"]
                if "old_options" in translation and field.get("options") == translation["old_options"]:
                    new_field["options"] = translation["new_options"]
                updated_fields.append(new_field)
            else:
                updated_fields.append(field)  # کاربر این فیلد را تغییر داده، دست‌نخورده می‌ماند

        conn.execute(
            "UPDATE categories SET name = ?, technical_fields = ? WHERE id = ?",
            (new_name, json.dumps(updated_fields, ensure_ascii=False), row["id"]),
        )

    set_setting(conn, "categories_translated_en", "1")


def _seed_categories(conn):
    def insert_node(node, parent_id):
        fields = json.dumps(node.get("fields", []), ensure_ascii=False)
        cur = conn.execute(
            "INSERT INTO categories (name, parent_id, technical_fields) VALUES (?, ?, ?)",
            (node["name"], parent_id, fields),
        )
        new_id = cur.lastrowid
        for child in node.get("children", []):
            insert_node(child, new_id)

    for root_node in DEFAULT_CATEGORY_TREE:
        insert_node(root_node, None)


def _seed_settings(conn):
    for key, value in DEFAULT_SETTINGS.items():
        conn.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value)
        )


# ---------------------------------------------------------------------------
# تنظیمات (Settings)
# ---------------------------------------------------------------------------

def get_setting(conn, key, default=None):
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def set_setting(conn, key, value):
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, str(value)),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# دسته‌بندی‌ها (Categories)
# ---------------------------------------------------------------------------

def add_category(conn, name, parent_id=None, technical_fields=None):
    fields_json = json.dumps(technical_fields or [], ensure_ascii=False)
    cur = conn.execute(
        "INSERT INTO categories (name, parent_id, technical_fields) VALUES (?, ?, ?)",
        (name.strip(), parent_id, fields_json),
    )
    conn.commit()
    return cur.lastrowid


def update_category(conn, category_id, name=None, technical_fields=None):
    if name is not None:
        conn.execute(
            "UPDATE categories SET name = ? WHERE id = ?", (name.strip(), category_id)
        )
    if technical_fields is not None:
        conn.execute(
            "UPDATE categories SET technical_fields = ? WHERE id = ?",
            (json.dumps(technical_fields, ensure_ascii=False), category_id),
        )
    conn.commit()


def delete_category(conn, category_id):
    """
    حذف یک دسته. اگر زیردسته یا قطعه‌ای به آن وابسته باشد، دسته‌های فرزند
    به‌صورت آبشاری حذف می‌شوند (طبق ON DELETE CASCADE) و قطعات وابسته،
    category_id آن‌ها NULL می‌شود (طبق ON DELETE SET NULL) تا هیچ داده‌ای
    از بین نرود.
    """
    conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    conn.commit()


def get_all_categories(conn):
    """تمام دسته‌ها را به‌صورت لیست ردیف (flat) برمی‌گرداند."""
    return conn.execute("SELECT * FROM categories ORDER BY parent_id, name").fetchall()


def get_category(conn, category_id):
    return conn.execute(
        "SELECT * FROM categories WHERE id = ?", (category_id,)
    ).fetchone()


def get_children(conn, parent_id):
    return conn.execute(
        "SELECT * FROM categories WHERE parent_id IS ? ORDER BY name", (parent_id,)
    ).fetchall()


def is_leaf(conn, category_id):
    row = conn.execute(
        "SELECT COUNT(*) AS c FROM categories WHERE parent_id = ?", (category_id,)
    ).fetchone()
    return row["c"] == 0


def get_category_path(conn, category_id):
    """مسیر کامل دسته را به‌صورت رشته برمی‌گرداند، مثلا: «مقاومت > کربنی / فیلمی»."""
    names = []
    current_id = category_id
    visited = set()
    while current_id is not None and current_id not in visited:
        visited.add(current_id)
        row = get_category(conn, current_id)
        if row is None:
            break
        names.append(row["name"])
        current_id = row["parent_id"]
    return " > ".join(reversed(names))


def get_technical_fields(conn, category_id):
    """فیلدهای فنی یک دسته را به شکل لیست دیکشنری برمی‌گرداند."""
    row = get_category(conn, category_id)
    if row is None:
        return []
    try:
        return json.loads(row["technical_fields"])
    except (TypeError, ValueError):
        return []


def build_category_tree(conn):
    """
    درخت کامل دسته‌ها را به شکل تودرتو برمی‌گرداند تا برای نمایش در
    درخت‌های GUI (مثلا ttk.Treeview) قابل استفاده باشد.
    خروجی: لیستی از دیکشنری {id, name, fields, children: [...]}
    """
    rows = get_all_categories(conn)
    nodes = {}
    for r in rows:
        nodes[r["id"]] = {
            "id": r["id"],
            "name": r["name"],
            "parent_id": r["parent_id"],
            "fields": json.loads(r["technical_fields"]),
            "children": [],
        }
    roots = []
    for node in nodes.values():
        if node["parent_id"] is None:
            roots.append(node)
        else:
            parent = nodes.get(node["parent_id"])
            if parent is not None:
                parent["children"].append(node)
            else:
                roots.append(node)

    def sort_children(node):
        node["children"].sort(key=lambda n: n["name"])
        for c in node["children"]:
            sort_children(c)

    roots.sort(key=lambda n: n["name"])
    for r in roots:
        sort_children(r)
    return roots


def get_descendant_ids(conn, category_id):
    """شناسه‌ی خود دسته به‌همراه تمام زیردسته‌هایش (برای جستجوی سلسله‌مراتبی)."""
    result = [category_id]
    children = get_children(conn, category_id)
    for child in children:
        result.extend(get_descendant_ids(conn, child["id"]))
    return result


# ---------------------------------------------------------------------------
# قطعات (Components)
# ---------------------------------------------------------------------------

def _now_iso():
    # دقت میکروثانیه‌ای برای جلوگیری از تداخل ترتیب رکوردهای هم‌زمان
    # (مثلا چند تغییر موجودی در کمتر از یک ثانیه)
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


def add_component(conn, data):
    """
    یک قطعه‌ی جدید ثبت می‌کند.
    data باید شامل کلیدهای زیر باشد (موارد اختیاری می‌توانند None باشند):
        name, category_id, quantity, location, price, currency,
        entry_date, image_path, datasheet_path, notes,
        technical_data (dict), low_stock_threshold
    مقدار qr_path بعدا (بعد از ساخته‌شدن QR که به id قطعه نیاز دارد) ست می‌شود.
    خروجی: id قطعه‌ی تازه ثبت‌شده.
    """
    now = _now_iso()
    cur = conn.execute(
        """
        INSERT INTO components (
            name, category_id, quantity, location, price, currency,
            entry_date, image_path, datasheet_path, qr_path, notes,
            technical_data, low_stock_threshold, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["name"].strip(),
            data.get("category_id"),
            int(data.get("quantity") or 0),
            (data.get("location") or "").strip(),
            data.get("price"),
            data.get("currency") or "USD",
            data.get("entry_date") or now[:10],
            data.get("image_path"),
            data.get("datasheet_path"),
            None,
            data.get("notes"),
            json.dumps(data.get("technical_data") or {}, ensure_ascii=False),
            int(data.get("low_stock_threshold") or 5),
            now,
            now,
        ),
    )
    component_id = cur.lastrowid
    conn.commit()

    initial_qty = int(data.get("quantity") or 0)
    if initial_qty != 0:
        log_stock_change(
            conn, component_id, initial_qty, initial_qty,
            reason="Initial stock entry",
        )
    return component_id


def update_component(conn, component_id, data):
    """
    بروزرسانی اطلاعات یک قطعه‌ی موجود.
    توجه: این تابع برای تغییر مستقیم تعداد استفاده نمی‌شود (از adjust_quantity
    استفاده کنید تا در تاریخچه هم ثبت شود)؛ اما اگر quantity در data باشد،
    به‌عنوان یک اصلاح دستی با ثبت در تاریخچه اعمال می‌شود.
    """
    current = get_component(conn, component_id)
    if current is None:
        raise ValueError("Component not found")

    fields_to_update = {
        "name": lambda v: v.strip(),
        "category_id": lambda v: v,
        "location": lambda v: (v or "").strip(),
        "price": lambda v: v,
        "currency": lambda v: v,
        "entry_date": lambda v: v,
        "image_path": lambda v: v,
        "datasheet_path": lambda v: v,
        "notes": lambda v: v,
        "low_stock_threshold": lambda v: int(v) if v is not None else None,
    }

    set_clauses = []
    values = []
    for key, transform in fields_to_update.items():
        if key in data:
            set_clauses.append(f"{key} = ?")
            values.append(transform(data[key]))

    if "technical_data" in data:
        set_clauses.append("technical_data = ?")
        values.append(json.dumps(data["technical_data"] or {}, ensure_ascii=False))

    set_clauses.append("updated_at = ?")
    values.append(_now_iso())

    values.append(component_id)
    conn.execute(
        f"UPDATE components SET {', '.join(set_clauses)} WHERE id = ?", values
    )
    conn.commit()

    if "quantity" in data and data["quantity"] is not None:
        new_qty = int(data["quantity"])
        old_qty = current["quantity"]
        delta = new_qty - old_qty
        if delta != 0:
            adjust_quantity(conn, component_id, delta, reason="Manual quantity correction")


def set_qr_path(conn, component_id, qr_path):
    conn.execute(
        "UPDATE components SET qr_path = ?, updated_at = ? WHERE id = ?",
        (qr_path, _now_iso(), component_id),
    )
    conn.commit()


def set_barcode_path(conn, component_id, barcode_path):
    conn.execute(
        "UPDATE components SET barcode_path = ?, updated_at = ? WHERE id = ?",
        (barcode_path, _now_iso(), component_id),
    )
    conn.commit()


def delete_component(conn, component_id):
    conn.execute("DELETE FROM components WHERE id = ?", (component_id,))
    conn.commit()


def get_component(conn, component_id):
    return conn.execute(
        "SELECT * FROM components WHERE id = ?", (component_id,)
    ).fetchone()


def get_component_technical_data(row):
    try:
        return json.loads(row["technical_data"])
    except (TypeError, ValueError):
        return {}


def get_distinct_locations(conn):
    rows = conn.execute(
        "SELECT DISTINCT location FROM components "
        "WHERE location IS NOT NULL AND TRIM(location) != '' "
        "ORDER BY location"
    ).fetchall()
    return [r["location"] for r in rows]


def search_components(conn, keyword=None, category_id=None, location=None,
                       min_price=None, max_price=None, low_stock_only=False,
                       include_subcategories=True):
    """
    جستجوی چندمنظوره‌ی قطعات.
    keyword در نام قطعه، محل قرارگیری، یادداشت‌ها و فیلدهای فنی (JSON)
    جستجو می‌شود؛ اگر keyword دقیقا با قالب شماره‌ی شناسه‌ی یکتای یک قطعه
    مطابقت داشته باشد (مثلا "EI-000042"، "42" یا کدی که از اسکن بارکد/QR
    آمده)، همان قطعه با تطابق دقیق شناسه هم در نتیجه لحاظ می‌شود.
    """
    query = "SELECT * FROM components WHERE 1=1"
    params = []

    if keyword:
        keyword = keyword.strip()
        like = f"%{keyword}%"
        exact_id = parse_component_code(keyword)
        if exact_id is not None:
            query += (
                " AND (name LIKE ? OR location LIKE ? OR notes LIKE ? "
                "OR technical_data LIKE ? OR id = ?)"
            )
            params.extend([like, like, like, like, exact_id])
        else:
            query += (
                " AND (name LIKE ? OR location LIKE ? OR notes LIKE ? "
                "OR technical_data LIKE ?)"
            )
            params.extend([like, like, like, like])

    if category_id is not None:
        if include_subcategories:
            ids = get_descendant_ids(conn, category_id)
            placeholders = ",".join("?" for _ in ids)
            query += f" AND category_id IN ({placeholders})"
            params.extend(ids)
        else:
            query += " AND category_id = ?"
            params.append(category_id)

    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location.strip()}%")

    if min_price is not None:
        query += " AND price >= ?"
        params.append(min_price)

    if max_price is not None:
        query += " AND price <= ?"
        params.append(max_price)

    if low_stock_only:
        query += " AND quantity <= low_stock_threshold"

    query += " ORDER BY name"
    return conn.execute(query, params).fetchall()


def get_all_components(conn):
    return conn.execute("SELECT * FROM components ORDER BY name").fetchall()


def count_low_stock(conn):
    row = conn.execute(
        "SELECT COUNT(*) AS c FROM components WHERE quantity <= low_stock_threshold"
    ).fetchone()
    return row["c"]


# ---------------------------------------------------------------------------
# تاریخچه‌ی موجودی (Stock History)
# ---------------------------------------------------------------------------

def log_stock_change(conn, component_id, change_amount, resulting_quantity, reason=""):
    conn.execute(
        """
        INSERT INTO stock_history
            (component_id, change_amount, resulting_quantity, reason, date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (component_id, change_amount, resulting_quantity, reason, _now_iso()),
    )
    conn.commit()


def adjust_quantity(conn, component_id, delta, reason=""):
    """
    تعداد یک قطعه را به‌اندازه‌ی delta تغییر می‌دهد (مثبت = افزودن، منفی = کسر)
    و تغییر را در تاریخچه ثبت می‌کند. مقدار جدید نمی‌تواند منفی شود.
    """
    component = get_component(conn, component_id)
    if component is None:
        raise ValueError("Component not found")

    new_qty = component["quantity"] + delta
    if new_qty < 0:
        raise ValueError("Stock quantity cannot go negative")

    conn.execute(
        "UPDATE components SET quantity = ?, updated_at = ? WHERE id = ?",
        (new_qty, _now_iso(), component_id),
    )
    conn.commit()
    log_stock_change(conn, component_id, delta, new_qty, reason=reason)
    return new_qty


def get_history(conn, component_id):
    return conn.execute(
        "SELECT * FROM stock_history WHERE component_id = ? ORDER BY date DESC, id DESC",
        (component_id,),
    ).fetchall()
