[app]

# (str) Uygulama başlığı
title = Maas Takip

# (str) Paket adı (boşluk ve özel karakter içermez)
package.name = maastakip

# (str) Paket alanı (ters domain yapısı)
package.domain = org.test

# (str) Kaynak kodun olduğu dizin
source.dir = .

# (list) Dahil edilecek dosya uzantıları
source.include_exts = py,png,jpg,kv,atlas

# (str) Uygulama versiyonu
version = 0.1

# (list) Uygulama gereksinimleri (Ağır kütüphaneler çıkarıldı!)
requirements = python3,kivy

# (str) Uygulama ikonu (GitHub'a yüklediğin isimle aynı olmalı)
icon.filename = icon.png

# (str) Açılış ekranı resmi
presplash.filename = loading.png

# (str) Uygulama yönü (Dikey)
orientation = portrait

# (bool) Tam ekran modu
fullscreen = 0

# --- Android Ayarları ---

# (list) İzinler (CSV kaydı için şart)
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Hedef Android API seviyesi (2026 için 34 idealdir)
android.api = 34

# (int) Minimum Android API (Eski telefonlar için destek)
android.minapi = 21

# (bool) Uygulamanın uyku moduna geçmesini engelle
android.skip_update = False

# (str) Android Logcat log seviyesi (Hata ayıklamak için)
log_level = 2

# (int) Android SDK sürümü
android.sdk = 34

[buildozer]

# (int) Log seviyesi (2 = her şeyi göster)
log_level = 2

# (int) Buildozer'ın çıktıları için bekleme süresi
warn_on_root = 1
