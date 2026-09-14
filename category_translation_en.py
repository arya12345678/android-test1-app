# -*- coding: utf-8 -*-
"""
Auto-generated translation table (Persian defaults -> English defaults),
used once by database._migrate_translate_seed_categories_to_english() to
translate a user'''s already-seeded default categories after upgrading to
the English version of the app. Only categories/fields whose current text
exactly matches the original Persian default are touched - anything the
user renamed or added themselves is left untouched.
"""

NAME_MAP =  {
    "مقاومت": "Resistor",
    "کربنی / فیلمی": "Carbon / Film",
    "پتانسیومتر / تریمر": "Potentiometer / Trimmer",
    "خازن": "Capacitor",
    "سرامیکی": "Ceramic",
    "الکترولیتی": "Electrolytic",
    "تانتالیوم / فیلمی": "Tantalum / Film",
    "سلف": "Inductor",
    "دیود": "Diode",
    "معمولی / یکسوساز": "General Purpose / Rectifier",
    "زنر": "Zener",
    "LED": "LED",
    "ترانزیستور": "Transistor",
    "BJT": "BJT",
    "MOSFET": "MOSFET",
    "آی‌سی (IC)": "IC",
    "میکروکنترلر": "Microcontroller",
    "رگولاتور ولتاژ": "Voltage Regulator",
    "آپ‌امپ": "Op-Amp",
    "منطقی / دیجیتال": "Logic / Digital",
    "سایر آی‌سی‌ها": "Other ICs",
    "ماژول": "Module",
    "کانکتور / سوکت": "Connector / Socket",
    "سوئیچ / کلید": "Switch",
    "مادربرد / بردهای توسعه": "Development Board",
    "ابزار و متفرقه": "Tools & Misc"
}

FIELD_MAP =  {
    "Resistor": [],
    "Carbon / Film": [
        {
            "key": "resistance",
            "old_label": "مقدار مقاومت",
            "new_label": "Resistance"
        },
        {
            "key": "tolerance",
            "old_label": "تولرانس (%)",
            "new_label": "Tolerance (%)"
        },
        {
            "key": "power",
            "old_label": "توان (وات)",
            "new_label": "Power (W)"
        },
        {
            "key": "package",
            "old_label": "نوع پکیج",
            "new_label": "Package Type",
            "old_options": [
                "THT (سوراخ‌دار)",
                "SMD",
                "نامشخص"
            ],
            "new_options": [
                "THT (through-hole)",
                "SMD",
                "Unspecified"
            ]
        }
    ],
    "Potentiometer / Trimmer": [
        {
            "key": "resistance",
            "old_label": "مقدار مقاومت",
            "new_label": "Resistance"
        },
        {
            "key": "rotation",
            "old_label": "نوع (چرخشی/خطی)",
            "new_label": "Type (Rotary/Linear)"
        }
    ],
    "Capacitor": [],
    "Ceramic": [
        {
            "key": "capacitance",
            "old_label": "ظرفیت",
            "new_label": "Capacitance"
        },
        {
            "key": "voltage",
            "old_label": "ولتاژ کاری",
            "new_label": "Rated Voltage"
        },
        {
            "key": "package",
            "old_label": "نوع پکیج",
            "new_label": "Package Type",
            "old_options": [
                "THT (سوراخ‌دار)",
                "SMD",
                "نامشخص"
            ],
            "new_options": [
                "THT (through-hole)",
                "SMD",
                "Unspecified"
            ]
        }
    ],
    "Electrolytic": [
        {
            "key": "capacitance",
            "old_label": "ظرفیت",
            "new_label": "Capacitance"
        },
        {
            "key": "voltage",
            "old_label": "ولتاژ کاری",
            "new_label": "Rated Voltage"
        }
    ],
    "Tantalum / Film": [
        {
            "key": "capacitance",
            "old_label": "ظرفیت",
            "new_label": "Capacitance"
        },
        {
            "key": "voltage",
            "old_label": "ولتاژ کاری",
            "new_label": "Rated Voltage"
        }
    ],
    "Inductor": [
        {
            "key": "inductance",
            "old_label": "مقدار سلفی",
            "new_label": "Inductance"
        },
        {
            "key": "current",
            "old_label": "جریان مجاز",
            "new_label": "Rated Current"
        }
    ],
    "Diode": [],
    "General Purpose / Rectifier": [
        {
            "key": "voltage",
            "old_label": "ولتاژ معکوس",
            "new_label": "Reverse Voltage"
        },
        {
            "key": "current",
            "old_label": "جریان مجاز",
            "new_label": "Rated Current"
        }
    ],
    "Zener": [
        {
            "key": "zener_voltage",
            "old_label": "ولتاژ زنر",
            "new_label": "Zener Voltage"
        },
        {
            "key": "power",
            "old_label": "توان",
            "new_label": "Power"
        }
    ],
    "LED": [
        {
            "key": "color",
            "old_label": "رنگ",
            "new_label": "Color"
        },
        {
            "key": "size",
            "old_label": "سایز",
            "new_label": "Size"
        }
    ],
    "Transistor": [],
    "BJT": [
        {
            "key": "type",
            "old_label": "نوع (NPN/PNP)",
            "new_label": "Type (NPN/PNP)",
            "old_options": [
                "NPN",
                "PNP"
            ],
            "new_options": [
                "NPN",
                "PNP"
            ]
        },
        {
            "key": "vce",
            "old_label": "Vce max",
            "new_label": "Vce max"
        },
        {
            "key": "ic",
            "old_label": "Ic max",
            "new_label": "Ic max"
        },
        {
            "key": "package",
            "old_label": "نوع پکیج",
            "new_label": "Package Type",
            "old_options": [
                "THT (سوراخ‌دار)",
                "SMD",
                "نامشخص"
            ],
            "new_options": [
                "THT (through-hole)",
                "SMD",
                "Unspecified"
            ]
        }
    ],
    "MOSFET": [
        {
            "key": "channel",
            "old_label": "نوع کانال",
            "new_label": "Channel Type",
            "old_options": [
                "N-Channel",
                "P-Channel"
            ],
            "new_options": [
                "N-Channel",
                "P-Channel"
            ]
        },
        {
            "key": "vds",
            "old_label": "Vds max",
            "new_label": "Vds max"
        },
        {
            "key": "id",
            "old_label": "Id max",
            "new_label": "Id max"
        },
        {
            "key": "package",
            "old_label": "نوع پکیج",
            "new_label": "Package Type",
            "old_options": [
                "THT (سوراخ‌دار)",
                "SMD",
                "نامشخص"
            ],
            "new_options": [
                "THT (through-hole)",
                "SMD",
                "Unspecified"
            ]
        }
    ],
    "IC": [],
    "Microcontroller": [
        {
            "key": "model",
            "old_label": "مدل دقیق",
            "new_label": "Exact Model"
        },
        {
            "key": "voltage",
            "old_label": "ولتاژ کاری",
            "new_label": "Operating Voltage"
        },
        {
            "key": "package",
            "old_label": "نوع پکیج",
            "new_label": "Package Type",
            "old_options": [
                "THT (سوراخ‌دار)",
                "SMD",
                "نامشخص"
            ],
            "new_options": [
                "THT (through-hole)",
                "SMD",
                "Unspecified"
            ]
        }
    ],
    "Voltage Regulator": [
        {
            "key": "output_voltage",
            "old_label": "ولتاژ خروجی",
            "new_label": "Output Voltage"
        },
        {
            "key": "current",
            "old_label": "جریان خروجی",
            "new_label": "Output Current"
        },
        {
            "key": "package",
            "old_label": "نوع پکیج",
            "new_label": "Package Type",
            "old_options": [
                "THT (سوراخ‌دار)",
                "SMD",
                "نامشخص"
            ],
            "new_options": [
                "THT (through-hole)",
                "SMD",
                "Unspecified"
            ]
        }
    ],
    "Op-Amp": [
        {
            "key": "model",
            "old_label": "مدل دقیق",
            "new_label": "Exact Model"
        },
        {
            "key": "package",
            "old_label": "نوع پکیج",
            "new_label": "Package Type",
            "old_options": [
                "THT (سوراخ‌دار)",
                "SMD",
                "نامشخص"
            ],
            "new_options": [
                "THT (through-hole)",
                "SMD",
                "Unspecified"
            ]
        }
    ],
    "Logic / Digital": [
        {
            "key": "model",
            "old_label": "مدل دقیق",
            "new_label": "Exact Model"
        },
        {
            "key": "family",
            "old_label": "خانواده (74xx / 40xx / ...)",
            "new_label": "Family (74xx / 40xx / ...)"
        }
    ],
    "Other ICs": [
        {
            "key": "model",
            "old_label": "مدل دقیق",
            "new_label": "Exact Model"
        },
        {
            "key": "package",
            "old_label": "نوع پکیج",
            "new_label": "Package Type",
            "old_options": [
                "THT (سوراخ‌دار)",
                "SMD",
                "نامشخص"
            ],
            "new_options": [
                "THT (through-hole)",
                "SMD",
                "Unspecified"
            ]
        }
    ],
    "Module": [
        {
            "key": "function",
            "old_label": "کاربرد ماژول",
            "new_label": "Module Function"
        },
        {
            "key": "voltage",
            "old_label": "ولتاژ کاری",
            "new_label": "Operating Voltage"
        },
        {
            "key": "interface",
            "old_label": "نوع ارتباط (I2C/SPI/UART/...)",
            "new_label": "Interface (I2C/SPI/UART/...)"
        }
    ],
    "Connector / Socket": [
        {
            "key": "pin_count",
            "old_label": "تعداد پین",
            "new_label": "Pin Count"
        },
        {
            "key": "pitch",
            "old_label": "فاصله پین‌ها (Pitch)",
            "new_label": "Pitch"
        }
    ],
    "Switch": [
        {
            "key": "type",
            "old_label": "نوع کلید",
            "new_label": "Switch Type"
        },
        {
            "key": "current_rating",
            "old_label": "جریان مجاز",
            "new_label": "Current Rating"
        }
    ],
    "Development Board": [
        {
            "key": "model",
            "old_label": "مدل دقیق",
            "new_label": "Exact Model"
        }
    ],
    "Tools & Misc": []
}
