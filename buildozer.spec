[app]

# Maaş Takip v0.7
# Ana dosya: main.py

title = Maaş Takip
package.name = maastakip
package.domain = org.yilmaz

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,ttf

version = 0.7

requirements = python3,kivy

orientation = portrait
fullscreen = 0

# Dış depolama izni istemiyoruz.
# Kayıtlar main.py içinde App.user_data_dir / app_storage_path ile uygulamanın özel klasörüne yazılır.
# Bu, Android Error 13 / Permission denied hatasını önlemek için özellikle böyle ayarlandı.
android.permissions =
android.private_storage = True

# Güncel Android hedefleri. Buildozer ortamın eskiyse api/ndk değerlerini kendi kurulumuna göre düşürebilirsin.
android.api = 35
android.minapi = 23
android.ndk = 25b
android.sdk = 35
android.accept_sdk_license = True

# APK üretimi için varsayılan mimariler.
android.archs = arm64-v8a, armeabi-v7a

# Logcat filtreleri. Hata ayıklamada iş görür.
android.logcat_filters = *:S python:D

# AndroidX genelde modern buildlerde güvenli tercih.
android.enable_androidx = True

# Python for Android ayarları
p4a.bootstrap = sdl2
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
