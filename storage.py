# -*- coding: utf-8 -*-
"""
Figures out where this app's private data folder should live.

On a real Android device, apps don't get to pick "next to the .apk" the
way the Windows version picks "next to the .exe" - Android gives every
app its own private, sandboxed storage folder instead. We use that.

When this same code is run on a regular desktop Python (for local
testing before building an APK), there's no "android" module available,
so we fall back to a plain folder next to this file - just like the
Windows version does.
"""

import os


def get_base_dir():
    try:
        from android.storage import app_storage_path  # type: ignore
        return app_storage_path()
    except ImportError:
        return os.path.dirname(os.path.abspath(__file__))


def get_data_dir():
    base_dir = get_base_dir()
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    for sub in ("images", "datasheets", "qrcodes", "barcodes", "reports"):
        os.makedirs(os.path.join(data_dir, sub), exist_ok=True)
    return data_dir
