[app]
title = Maas Takip
package.name = maastakip
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Sadece bunlar kalsın!
requirements = python3,kivy

orientation = portrait
android.api = 33
android.minapi = 21
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
icon.filename = icon.png
presplash.filename = loading.png

[buildozer]
log_level = 2
