[app]
title = Maas Takip
package.name = maastakip
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# SADECE BUNLAR! Virgül hatası yapma.
requirements = python3,kivy

orientation = portrait
android.api = 33
android.minapi = 21
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
icon.filename = icon.png
presplash.filename = loading.png

# BUILD SÜRESİNİ KISALTMAK İÇİN SADECE TEK MİMARİ
android.archs = arm64-v8a

[buildozer]
log_level = 2
