# -*- coding: utf-8 -*-
"""
Electronics Component Inventory - Android (Kivy) version.

Milestone 1: core only - database, "Add Component" screen, "Search" screen.
Categories management, barcode/QR, and backup/restore are added in later
milestones, once this core is confirmed working on the actual phone.
"""

import os

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.core.window import Window

import database as db
import validators as v
from storage import get_data_dir

# ---------------------------------------------------------------------------
# Small reusable widgets
# ---------------------------------------------------------------------------

class LabeledInput(BoxLayout):
    """A row with a label on the left and a text input on the right."""

    def __init__(self, label_text, **kwargs):
        multiline = kwargs.pop("multiline", False)
        super().__init__(orientation="horizontal", size_hint_y=None,
                          height=dp(80) if multiline else dp(44), spacing=dp(8), **kwargs)
        self.add_widget(Label(text=label_text, size_hint_x=0.4, halign="left",
                               valign="middle", text_size=(dp(120), None)))
        self.input = TextInput(multiline=multiline, size_hint_x=0.6)
        self.add_widget(self.input)

    def get(self):
        return self.input.text

    def set(self, value):
        self.input.text = "" if value is None else str(value)

    def clear(self):
        self.input.text = ""


def make_popup_message(title, message):
    content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
    content.add_widget(Label(text=message))
    popup = Popup(title=title, content=content, size_hint=(0.85, 0.4))
    close_btn = Button(text="OK", size_hint_y=None, height=dp(44))
    content.add_widget(close_btn)
    close_btn.bind(on_press=popup.dismiss)
    popup.open()
    return popup


def make_confirm_popup(title, message, on_yes):
    content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
    content.add_widget(Label(text=message))
    btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
    content.add_widget(btn_row)
    popup = Popup(title=title, content=content, size_hint=(0.85, 0.5))

    def _yes(instance):
        popup.dismiss()
        on_yes()

    yes_btn = Button(text="Yes")
    no_btn = Button(text="Cancel")
    yes_btn.bind(on_press=_yes)
    no_btn.bind(on_press=popup.dismiss)
    btn_row.add_widget(yes_btn)
    btn_row.add_widget(no_btn)
    popup.open()
    return popup


# ---------------------------------------------------------------------------
# Category picker popup
# ---------------------------------------------------------------------------

class CategoryPickerPopup(Popup):
    """
    Shows the full category tree (indented) in a scrollable list. Only
    leaf categories (no children) are selectable, since technical fields
    only apply to leaves.
    """

    def __init__(self, conn, on_selected, **kwargs):
        super().__init__(title="Select Category", size_hint=(0.9, 0.9), **kwargs)
        self.on_selected = on_selected

        scroll = ScrollView()
        self.list_layout = GridLayout(cols=1, size_hint_y=None, spacing=dp(2), padding=dp(6))
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        scroll.add_widget(self.list_layout)
        self.content = scroll

        tree = db.build_category_tree(conn)
        self._render_tree(tree, depth=0)

    def _render_tree(self, nodes, depth):
        for node in nodes:
            is_leaf = len(node["children"]) == 0
            prefix = "   " * depth
            label = ("\U0001F539 " if is_leaf else "\U0001F4C1 ") + prefix + node["name"]
            btn = Button(text=label, size_hint_y=None, height=dp(44), halign="left")
            if is_leaf:
                btn.bind(on_press=lambda inst, n=node: self._select(n))
            else:
                btn.disabled = False  # still visible, just not directly selectable
                btn.background_color = (0.3, 0.3, 0.3, 1)
            self.list_layout.add_widget(btn)
            if node["children"]:
                self._render_tree(node["children"], depth + 1)

    def _select(self, node):
        self.dismiss()
        self.on_selected(node)


# ---------------------------------------------------------------------------
# Entry screen ("Add Component")
# ---------------------------------------------------------------------------

class EntryScreen(Screen):
    def __init__(self, conn, **kwargs):
        super().__init__(**kwargs)
        self.conn = conn
        self.selected_category_id = None
        self.tech_field_inputs = {}  # key -> LabeledInput
        self.editing_component_id = None

        root = BoxLayout(orientation="vertical")
        self.add_widget(root)

        scroll = ScrollView()
        root.add_widget(scroll)

        self.form = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6), padding=dp(10))
        self.form.bind(minimum_height=self.form.setter("height"))
        scroll.add_widget(self.form)

        self.form.add_widget(Label(text="Add / Edit Component", size_hint_y=None, height=dp(36),
                                    font_size="20sp", bold=True))

        self.category_btn = Button(text="Select Category...", size_hint_y=None, height=dp(48))
        self.category_btn.bind(on_press=self._open_category_picker)
        self.form.add_widget(self.category_btn)

        self.name_row = LabeledInput("Name / Model *")
        self.form.add_widget(self.name_row)

        self.quantity_row = LabeledInput("Quantity")
        self.quantity_row.set(0)
        self.form.add_widget(self.quantity_row)

        self.location_row = LabeledInput("Storage Location")
        self.form.add_widget(self.location_row)

        self.price_row = LabeledInput("Price")
        self.form.add_widget(self.price_row)

        self.currency_row = LabeledInput("Currency")
        self.currency_row.set("USD")
        self.form.add_widget(self.currency_row)

        self.date_row = LabeledInput("Entry Date (YYYY-MM-DD)")
        self.form.add_widget(self.date_row)

        self.threshold_row = LabeledInput("Low Stock Threshold")
        self.threshold_row.set(5)
        self.form.add_widget(self.threshold_row)

        self.notes_row = LabeledInput("Notes", multiline=True)
        self.form.add_widget(self.notes_row)

        self.tech_fields_label = Label(text="Technical Fields", size_hint_y=None, height=dp(30),
                                        bold=True)
        self.form.add_widget(self.tech_fields_label)

        self.tech_fields_container = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        self.tech_fields_container.bind(minimum_height=self.tech_fields_container.setter("height"))
        self.form.add_widget(self.tech_fields_container)

        btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8), padding=(0, dp(10)))
        save_btn = Button(text="Save")
        save_btn.bind(on_press=lambda inst: self.save())
        clear_btn = Button(text="Clear")
        clear_btn.bind(on_press=lambda inst: self.reset_form())
        btn_row.add_widget(save_btn)
        btn_row.add_widget(clear_btn)
        self.form.add_widget(btn_row)

    def _open_category_picker(self, instance):
        CategoryPickerPopup(self.conn, on_selected=self._on_category_selected).open()

    def _on_category_selected(self, node):
        self.selected_category_id = node["id"]
        self.category_btn.text = f"Category: {node['name']}"
        self._rebuild_technical_fields(node.get("fields", []))

    def _rebuild_technical_fields(self, field_defs, values=None):
        values = values or {}
        self.tech_fields_container.clear_widgets()
        self.tech_field_inputs = {}
        if not field_defs:
            self.tech_fields_container.add_widget(
                Label(text="(No technical fields for this category)", size_hint_y=None, height=dp(30))
            )
            return
        for field in field_defs:
            row = LabeledInput(field["label"])
            if field["key"] in values:
                row.set(values[field["key"]])
            self.tech_fields_container.add_widget(row)
            self.tech_field_inputs[field["key"]] = row

    def _collect_technical_data(self):
        return {key: row.get() for key, row in self.tech_field_inputs.items()}

    def reset_form(self):
        self.editing_component_id = None
        self.selected_category_id = None
        self.category_btn.text = "Select Category..."
        self.name_row.clear()
        self.quantity_row.set(0)
        self.location_row.clear()
        self.price_row.clear()
        self.currency_row.set("USD")
        self.date_row.clear()
        self.threshold_row.set(5)
        self.notes_row.clear()
        self._rebuild_technical_fields([])

    def save(self):
        field_defs = (
            db.get_technical_fields(self.conn, self.selected_category_id)
            if self.selected_category_id else []
        )
        raw = {
            "name": self.name_row.get(),
            "category_id": self.selected_category_id,
            "quantity": self.quantity_row.get(),
            "location": self.location_row.get(),
            "price": self.price_row.get(),
            "currency": self.currency_row.get(),
            "entry_date": self.date_row.get(),
            "notes": self.notes_row.get(),
            "low_stock_threshold": self.threshold_row.get(),
            "technical_data": self._collect_technical_data(),
        }
        try:
            clean = v.validate_component_form(raw, field_defs)
        except v.ValidationError as e:
            make_popup_message("Invalid Input", str(e))
            return

        if self.editing_component_id is None:
            component_id = db.add_component(self.conn, clean)
            make_popup_message("Saved", f"Component saved (ID #{component_id}).")
        else:
            db.update_component(self.conn, self.editing_component_id, clean)
            make_popup_message("Updated", f"Component #{self.editing_component_id} updated.")

        self.reset_form()
        app = App.get_running_app()
        if app:
            app.on_component_saved()

    def load_component_for_edit(self, component_id):
        comp = db.get_component(self.conn, component_id)
        if comp is None:
            make_popup_message("Error", "Component not found.")
            return
        self.editing_component_id = component_id
        self.name_row.set(comp["name"])
        self.quantity_row.set(comp["quantity"])
        self.location_row.set(comp["location"] or "")
        self.price_row.set(comp["price"] if comp["price"] is not None else "")
        self.currency_row.set(comp["currency"] or "USD")
        self.date_row.set(comp["entry_date"] or "")
        self.threshold_row.set(comp["low_stock_threshold"])
        self.notes_row.set(comp["notes"] or "")

        if comp["category_id"]:
            cat = db.get_category(self.conn, comp["category_id"])
            self.selected_category_id = comp["category_id"]
            self.category_btn.text = f"Category: {cat['name']}" if cat else "Select Category..."
            field_defs = db.get_technical_fields(self.conn, comp["category_id"])
            tech_values = db.get_component_technical_data(comp)
            self._rebuild_technical_fields(field_defs, tech_values)
        else:
            self.selected_category_id = None
            self.category_btn.text = "Select Category..."
            self._rebuild_technical_fields([])


# ---------------------------------------------------------------------------
# Search screen
# ---------------------------------------------------------------------------

class ResultRow(BoxLayout):
    def __init__(self, component_row, on_tap, **kwargs):
        super().__init__(orientation="vertical", size_hint_y=None, height=dp(64),
                          padding=(dp(8), dp(4)), **kwargs)
        import component_code as cc
        is_low = component_row["quantity"] <= component_row["low_stock_threshold"]

        top_line = BoxLayout(size_hint_y=None, height=dp(26))
        top_line.add_widget(Label(text=component_row["name"], halign="left", bold=True))
        top_line.add_widget(Label(text=f"Qty: {component_row['quantity']}", size_hint_x=0.3))
        self.add_widget(top_line)

        bottom_line = BoxLayout(size_hint_y=None, height=dp(22))
        code = cc.format_component_code(component_row["id"])
        loc = component_row["location"] or "-"
        status = " \u26A0 LOW" if is_low else ""
        bottom_line.add_widget(Label(
            text=f"{code}  |  {loc}{status}", font_size="12sp", color=(0.7, 0.7, 0.7, 1),
        ))
        self.add_widget(bottom_line)

        self.on_tap = on_tap
        self.component_id = component_row["id"]

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.on_tap(self.component_id)
            return True
        return super().on_touch_down(touch)


class SearchScreen(Screen):
    def __init__(self, conn, on_edit_request, **kwargs):
        super().__init__(**kwargs)
        self.conn = conn
        self.on_edit_request = on_edit_request

        root = BoxLayout(orientation="vertical")
        self.add_widget(root)

        search_row = BoxLayout(size_hint_y=None, height=dp(48), padding=dp(6), spacing=dp(6))
        self.search_input = TextInput(
            hint_text="Search by name, location, or ID (EI-...)...", multiline=False,
        )
        self.search_input.bind(on_text_validate=lambda inst: self.run_search())
        search_btn = Button(text="Search", size_hint_x=0.3)
        search_btn.bind(on_press=lambda inst: self.run_search())
        search_row.add_widget(self.search_input)
        search_row.add_widget(search_btn)
        root.add_widget(search_row)

        self.result_count_label = Label(text="0 results", size_hint_y=None, height=dp(26))
        root.add_widget(self.result_count_label)

        scroll = ScrollView()
        root.add_widget(scroll)
        self.results_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(2))
        self.results_layout.bind(minimum_height=self.results_layout.setter("height"))
        scroll.add_widget(self.results_layout)

    def on_pre_enter(self, *args):
        self.run_search()

    def run_search(self):
        keyword = self.search_input.text.strip() or None
        try:
            results = db.search_components(self.conn, keyword=keyword)
        except Exception as e:
            make_popup_message("Search Error", str(e))
            return
        self._populate(results)

    def _populate(self, rows):
        self.results_layout.clear_widgets()
        for row in rows:
            self.results_layout.add_widget(ResultRow(row, on_tap=self._open_detail))
        self.result_count_label.text = f"{len(rows)} results"

    def _open_detail(self, component_id):
        DetailPopup(self.conn, component_id, on_edit=self._request_edit,
                    on_changed=self.run_search).open()

    def _request_edit(self, component_id):
        self.on_edit_request(component_id)


class DetailPopup(Popup):
    def __init__(self, conn, component_id, on_edit, on_changed, **kwargs):
        self.conn = conn
        self.component_id = component_id
        self.on_edit = on_edit
        self.on_changed = on_changed
        comp = db.get_component(conn, component_id)

        super().__init__(title=comp["name"] if comp else "Component", size_hint=(0.92, 0.85), **kwargs)

        if comp is None:
            self.content = Label(text="Component not found.")
            return

        import component_code as cc
        scroll = ScrollView()
        layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6), padding=dp(10))
        layout.bind(minimum_height=layout.setter("height"))
        scroll.add_widget(layout)
        self.content = scroll

        code = cc.format_component_code(comp["id"])
        cat_path = db.get_category_path(conn, comp["category_id"]) if comp["category_id"] else "Uncategorized"

        info_lines = [
            ("ID", code),
            ("Category", cat_path),
            ("Quantity", str(comp["quantity"])),
            ("Location", comp["location"] or "-"),
            ("Price", f"{comp['price']:,.0f} {comp['currency'] or ''}" if comp["price"] is not None else "-"),
            ("Entry Date", comp["entry_date"] or "-"),
            ("Notes", comp["notes"] or "-"),
        ]
        for label, value in info_lines:
            row = BoxLayout(size_hint_y=None, height=dp(30))
            row.add_widget(Label(text=f"{label}:", bold=True, size_hint_x=0.35))
            row.add_widget(Label(text=value))
            layout.add_widget(row)

        if comp["category_id"]:
            field_defs = db.get_technical_fields(conn, comp["category_id"])
            tech_data = db.get_component_technical_data(comp)
            if field_defs:
                layout.add_widget(Label(text="Technical Specs", bold=True, size_hint_y=None, height=dp(30)))
                for field in field_defs:
                    val = tech_data.get(field["key"])
                    if val:
                        row = BoxLayout(size_hint_y=None, height=dp(28))
                        row.add_widget(Label(text=f"{field['label']}:", size_hint_x=0.5))
                        row.add_widget(Label(text=val))
                        layout.add_widget(row)

        adjust_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6), padding=(0, dp(6)))
        minus_btn = Button(text="- Remove 1")
        minus_btn.bind(on_press=lambda inst: self._adjust(-1))
        plus_btn = Button(text="+ Add 1")
        plus_btn.bind(on_press=lambda inst: self._adjust(1))
        adjust_row.add_widget(minus_btn)
        adjust_row.add_widget(plus_btn)
        layout.add_widget(adjust_row)

        btn_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6), padding=(0, dp(6)))
        edit_btn = Button(text="Edit")
        edit_btn.bind(on_press=self._edit)
        delete_btn = Button(text="Delete")
        delete_btn.bind(on_press=self._delete)
        close_btn = Button(text="Close")
        close_btn.bind(on_press=self.dismiss)
        btn_row.add_widget(edit_btn)
        btn_row.add_widget(delete_btn)
        btn_row.add_widget(close_btn)
        layout.add_widget(btn_row)

    def _adjust(self, delta):
        try:
            db.adjust_quantity(self.conn, self.component_id, delta,
                                reason="Manual adjustment (mobile)")
        except ValueError as e:
            make_popup_message("Error", str(e))
            return
        self.dismiss()
        self.on_changed()

    def _edit(self, instance):
        self.dismiss()
        self.on_edit(self.component_id)

    def _delete(self, instance):
        def do_delete():
            db.delete_component(self.conn, self.component_id)
            self.dismiss()
            self.on_changed()
        make_confirm_popup("Confirm Delete", "Delete this component permanently?", do_delete)


# ---------------------------------------------------------------------------
# Main App
# ---------------------------------------------------------------------------

class InventoryApp(App):
    def build(self):
        self.title = "Electronics Inventory"
        data_dir = get_data_dir()
        db_path = db.get_db_path(data_dir)
        db.init_db(db_path)
        self.conn = db.get_connection(db_path)

        self.sm = ScreenManager(transition=NoTransition())

        self.search_screen = SearchScreen(self.conn, on_edit_request=self._go_to_edit, name="search")
        self.entry_screen = EntryScreen(self.conn, name="entry")

        root = BoxLayout(orientation="vertical")

        nav_bar = BoxLayout(size_hint_y=None, height=dp(50))
        search_nav_btn = Button(text="Search / Inventory")
        search_nav_btn.bind(on_press=lambda inst: self._show("search"))
        add_nav_btn = Button(text="Add Component")
        add_nav_btn.bind(on_press=lambda inst: self._show_new_entry())
        nav_bar.add_widget(search_nav_btn)
        nav_bar.add_widget(add_nav_btn)
        root.add_widget(nav_bar)

        self.sm.add_widget(self.search_screen)
        self.sm.add_widget(self.entry_screen)
        root.add_widget(self.sm)

        self.sm.current = "search"
        return root

    def _show(self, name):
        self.sm.current = name

    def _show_new_entry(self):
        self.entry_screen.reset_form()
        self.sm.current = "entry"

    def _go_to_edit(self, component_id):
        self.entry_screen.load_component_for_edit(component_id)
        self.sm.current = "entry"

    def on_component_saved(self):
        self.sm.current = "search"

    def on_stop(self):
        if hasattr(self, "conn"):
            self.conn.close()


if __name__ == "__main__":
    InventoryApp().run()
