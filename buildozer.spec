[app]

# Uygulama bilgileri
title = Maas Takip
package.name = maastakip
package.domain = org.kanka
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Gereksinimler (Hata payını düşürmek için sadece temel kütüphaneleri ekledik)
requirements = python3,kivy

# Ekran Ayarları
orientation = portrait
fullscreen = 0

# Android Ayarları
android.archs = arm64-v8a, armeabi-v7a
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET
android.api = 34
android.minapi = 24
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
