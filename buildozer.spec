[app]

title = InventoryApp
package.name = electronicsinventory
package.domain = org.shahram

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

requirements = python3,kivy

orientation = portrait
fullscreen = 0

# Same proven settings confirmed working on the Motorola phone (Android 14)
android.minapi = 21
android.api = 33
android.archs = arm64-v8a
android.permissions =
android.accept_sdk_license = True

[buildozer]

log_level = 2
warn_on_root = 1
