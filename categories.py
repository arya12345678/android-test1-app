# -*- coding: utf-8 -*-
"""
Default category tree for electronic components.

Each node can have children or not. "Leaf" nodes (no children) can have a
list of dedicated "technical fields" that are automatically shown in the
form when registering a component from that category.

Each technical field's type is one of:
    "text"   -> free text input
    "number" -> numeric input
    "select" -> choose from a fixed set of options (requires "options" key)

This structure is only used to "seed" the database the first time the app
runs. After that, all categories and their technical fields live in the
database, and the user can edit, add, or delete them from the "Manage
Categories" section of the app - this file is just the starting point.
"""

# Shared technical field that can be added to any category (kept here only
# for reference; it is attached to the relevant categories below).
PACKAGE_FIELD = {
    "key": "package",
    "label": "Package Type",
    "type": "select",
    "options": ["THT (through-hole)", "SMD", "Unspecified"],
}

DEFAULT_CATEGORY_TREE = [
    {
        "name": "Resistor",
        "children": [
            {
                "name": "Carbon / Film",
                "fields": [
                    {"key": "resistance", "label": "Resistance", "type": "text"},
                    {"key": "tolerance", "label": "Tolerance (%)", "type": "text"},
                    {"key": "power", "label": "Power (W)", "type": "text"},
                    PACKAGE_FIELD,
                ],
            },
            {
                "name": "Potentiometer / Trimmer",
                "fields": [
                    {"key": "resistance", "label": "Resistance", "type": "text"},
                    {"key": "rotation", "label": "Type (Rotary/Linear)", "type": "text"},
                ],
            },
        ],
    },
    {
        "name": "Capacitor",
        "children": [
            {
                "name": "Ceramic",
                "fields": [
                    {"key": "capacitance", "label": "Capacitance", "type": "text"},
                    {"key": "voltage", "label": "Rated Voltage", "type": "text"},
                    PACKAGE_FIELD,
                ],
            },
            {
                "name": "Electrolytic",
                "fields": [
                    {"key": "capacitance", "label": "Capacitance", "type": "text"},
                    {"key": "voltage", "label": "Rated Voltage", "type": "text"},
                ],
            },
            {
                "name": "Tantalum / Film",
                "fields": [
                    {"key": "capacitance", "label": "Capacitance", "type": "text"},
                    {"key": "voltage", "label": "Rated Voltage", "type": "text"},
                ],
            },
        ],
    },
    {
        "name": "Inductor",
        "fields": [
            {"key": "inductance", "label": "Inductance", "type": "text"},
            {"key": "current", "label": "Rated Current", "type": "text"},
        ],
    },
    {
        "name": "Diode",
        "children": [
            {
                "name": "General Purpose / Rectifier",
                "fields": [
                    {"key": "voltage", "label": "Reverse Voltage", "type": "text"},
                    {"key": "current", "label": "Rated Current", "type": "text"},
                ],
            },
            {
                "name": "Zener",
                "fields": [
                    {"key": "zener_voltage", "label": "Zener Voltage", "type": "text"},
                    {"key": "power", "label": "Power", "type": "text"},
                ],
            },
            {
                "name": "LED",
                "fields": [
                    {"key": "color", "label": "Color", "type": "text"},
                    {"key": "size", "label": "Size", "type": "text"},
                ],
            },
        ],
    },
    {
        "name": "Transistor",
        "children": [
            {
                "name": "BJT",
                "fields": [
                    {"key": "type", "label": "Type (NPN/PNP)", "type": "select",
                     "options": ["NPN", "PNP"]},
                    {"key": "vce", "label": "Vce max", "type": "text"},
                    {"key": "ic", "label": "Ic max", "type": "text"},
                    PACKAGE_FIELD,
                ],
            },
            {
                "name": "MOSFET",
                "fields": [
                    {"key": "channel", "label": "Channel Type", "type": "select",
                     "options": ["N-Channel", "P-Channel"]},
                    {"key": "vds", "label": "Vds max", "type": "text"},
                    {"key": "id", "label": "Id max", "type": "text"},
                    PACKAGE_FIELD,
                ],
            },
        ],
    },
    {
        "name": "IC",
        "children": [
            {
                "name": "Microcontroller",
                "fields": [
                    {"key": "model", "label": "Exact Model", "type": "text"},
                    {"key": "voltage", "label": "Operating Voltage", "type": "text"},
                    PACKAGE_FIELD,
                ],
            },
            {
                "name": "Voltage Regulator",
                "fields": [
                    {"key": "output_voltage", "label": "Output Voltage", "type": "text"},
                    {"key": "current", "label": "Output Current", "type": "text"},
                    PACKAGE_FIELD,
                ],
            },
            {
                "name": "Op-Amp",
                "fields": [
                    {"key": "model", "label": "Exact Model", "type": "text"},
                    PACKAGE_FIELD,
                ],
            },
            {
                "name": "Logic / Digital",
                "fields": [
                    {"key": "model", "label": "Exact Model", "type": "text"},
                    {"key": "family", "label": "Family (74xx / 40xx / ...)", "type": "text"},
                ],
            },
            {
                "name": "Other ICs",
                "fields": [
                    {"key": "model", "label": "Exact Model", "type": "text"},
                    PACKAGE_FIELD,
                ],
            },
        ],
    },
    {
        "name": "Module",
        "fields": [
            {"key": "function", "label": "Module Function", "type": "text"},
            {"key": "voltage", "label": "Operating Voltage", "type": "text"},
            {"key": "interface", "label": "Interface (I2C/SPI/UART/...)", "type": "text"},
        ],
    },
    {
        "name": "Connector / Socket",
        "fields": [
            {"key": "pin_count", "label": "Pin Count", "type": "text"},
            {"key": "pitch", "label": "Pitch", "type": "text"},
        ],
    },
    {
        "name": "Switch",
        "fields": [
            {"key": "type", "label": "Switch Type", "type": "text"},
            {"key": "current_rating", "label": "Current Rating", "type": "text"},
        ],
    },
    {
        "name": "Development Board",
        "fields": [
            {"key": "model", "label": "Exact Model", "type": "text"},
        ],
    },
    {
        "name": "Tools & Misc",
        "fields": [],
    },
]
