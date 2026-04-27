import os
import csv
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup


ALANLAR = [
    "tarih",
    "gun_sayisi",
    "gunluk_ucret",
    "mesai_saat",
    "mesai_katsayi",
    "prim",
    "avans",
    "kesinti",
    "normal_ucret",
    "mesai_ucret",
    "toplam",
    "aciklama",
]


def bugunun_tarihi():
    return datetime.now().strftime("%d.%m.%Y")


def bu_ay():
    return datetime.now().strftime("%m.%Y")


def sayiya_cevir(deger):
    try:
        if deger is None:
            return 0.0

        deger = str(deger).replace(",", ".").strip()

        if deger == "":
            return 0.0

        return float(deger)
    except Exception:
        return 0.0


def para_yaz(deger):
    return f"{sayiya_cevir(deger):,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")


def tarih_ay_anahtari(tarih_metni):
    tarih_metni = str(tarih_metni).strip()

    formatlar = [
        "%d.%m.%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
    ]

    for fmt in formatlar:
        try:
            tarih = datetime.strptime(tarih_metni, fmt)
            return tarih.strftime("%m.%Y")
        except Exception:
            pass

    if len(tarih_metni) >= 7:
        return tarih_metni[-7:]

    return ""


class MaasTakipApp(App):
    def build(self):
        self.title = "Maaş Takip"

        self.dosya_yolu = os.path.join(self.user_data_dir, "maas_kayitlari.csv")
        self.dosyayi_hazirla_ve_duzelt()

        varsayilan_gunluk_ucret, varsayilan_mesai_katsayi = self.son_ayarlari_getir()

        ana = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=7
        )

        baslik = Label(
            text="Maaş ve Mesai Takip",
            size_hint_y=None,
            height=42,
            font_size=23,
            bold=True
        )
        ana.add_widget(baslik)

        form_scroll = ScrollView(size_hint=(1, 0.47))

        form = GridLayout(
            cols=2,
            spacing=7,
            padding=4,
            size_hint_y=None
        )
        form.bind(minimum_height=form.setter("height"))

        self.tarih = self.input_ekle(form, "Tarih", bugunun_tarihi())
        self.gun_sayisi = self.input_ekle(form, "Gün sayısı", "1")
        self.gunluk_ucret = self.input_ekle(form, "Günlük ücret", varsayilan_gunluk_ucret)
        self.mesai_saat = self.input_ekle(form, "Mesai saati", "0")
        self.mesai_katsayi = self.input_ekle(form, "Mesai katsayısı", varsayilan_mesai_katsayi)
        self.prim = self.input_ekle(form, "Prim", "0")
        self.avans = self.input_ekle(form, "Avans", "0")
        self.kesinti = self.input_ekle(form, "Kesinti", "0")
        self.aciklama = self.input_ekle(form, "Açıklama", "")

        form_scroll.add_widget(form)
        ana.add_widget(form_scroll)

        butonlar_1 = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=55,
            spacing=7
        )

        kaydet_btn = Button(text="Kaydet")
        kaydet_btn.bind(on_press=self.kaydet)

        toplam_btn = Button(text="Toplamı Göster")
        toplam_btn.bind(on_press=self.kayitlari_goster)

        butonlar_1.add_widget(kaydet_btn)
        butonlar_1.add_widget(toplam_btn)
        ana.add_widget(butonlar_1)

        filtre_satiri = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=48,
            spacing=7
        )

        self.ay_filtre = TextInput(
            text=bu_ay(),
            hint_text="Ay filtresi: 04.2026",
            multiline=False
        )

        filtre_btn = Button(text="Ayı Göster")
        filtre_btn.bind(on_press=self.kayitlari_goster)

        temizle_btn = Button(text="Tümünü Göster")
        temizle_btn.bind(on_press=self.filtre_temizle)

        filtre_satiri.add_widget(self.ay_filtre)
        filtre_satiri.add_widget(filtre_btn)
        filtre_satiri.add_widget(temizle_btn)
        ana.add_widget(filtre_satiri)

        sil_satiri = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=48,
            spacing=7
        )

        self.silinecek_no = TextInput(
            text="",
            hint_text="Silinecek kayıt no",
            multiline=False,
            input_filter="int"
        )

        sil_btn = Button(text="Kaydı Sil")
        sil_btn.bind(on_press=self.kaydi_sil)

        sil_satiri.add_widget(self.silinecek_no)
        sil_satiri.add_widget(sil_btn)
        ana.add_widget(sil_satiri)

        self.sonuc = Label(
            text="Hazır.",
            size_hint_y=None,
            height=100,
            font_size=15,
            halign="left",
            valign="middle"
        )
        self.sonuc.bind(width=self.label_genislik_ayarla)
        ana.add_widget(self.sonuc)

        kayit_baslik = Label(
            text="Kayıtlar",
            size_hint_y=None,
            height=32,
            font_size=19,
            bold=True
        )
        ana.add_widget(kayit_baslik)

        self.kayit_scroll = ScrollView(size_hint=(1, 0.53))

        self.kayit_label = Label(
            text="",
            size_hint_y=None,
            halign="left",
            valign="top",
            font_size=14
        )
        self.kayit_label.bind(width=self.label_genislik_ayarla)
        self.kayit_label.bind(texture_size=self.kayit_yukseklik_ayarla)

        self.kayit_scroll.add_widget(self.kayit_label)
        ana.add_widget(self.kayit_scroll)

        self.gorunen_indeksler = []
        self.kayitlari_goster()

        return ana

    def label_genislik_ayarla(self, instance, width):
        instance.text_size = (width, None)

    def kayit_yukseklik_ayarla(self, instance, texture_size):
        instance.height = texture_size[1] + 20

    def input_ekle(self, form, baslik, varsayilan):
        lbl = Label(
            text=baslik,
            size_hint_y=None,
            height=43,
            halign="left",
            valign="middle"
        )
        lbl.bind(width=self.label_genislik_ayarla)

        inp = TextInput(
            text=str(varsayilan),
            multiline=False,
            size_hint_y=None,
            height=43
        )

        form.add_widget(lbl)
        form.add_widget(inp)

        return inp

    def mesaj_goster(self, baslik, mesaj):
        kutu = BoxLayout(orientation="vertical", padding=10, spacing=10)
        kutu.add_widget(Label(text=mesaj, halign="center", valign="middle"))

        kapat_btn = Button(text="Tamam", size_hint_y=None, height=45)
        kutu.add_widget(kapat_btn)

        popup = Popup(
            title=baslik,
            content=kutu,
            size_hint=(0.85, 0.38)
        )
        kapat_btn.bind(on_press=popup.dismiss)
        popup.open()

    def dosyayi_hazirla_ve_duzelt(self):
        if not os.path.exists(self.dosya_yolu):
            self.kayitlari_yaz([])
            return

        try:
            with open(self.dosya_yolu, "r", newline="", encoding="utf-8") as f:
                okuyucu = csv.DictReader(f)
                eski_kayitlar = list(okuyucu)
        except Exception:
            eski_kayitlar = []

        duzeltilmis_kayitlar = []

        for kayit in eski_kayitlar:
            duzeltilmis_kayitlar.append(self.kaydi_duzelt(kayit))

        self.kayitlari_yaz(duzeltilmis_kayitlar)

    def kaydi_duzelt(self, kayit):
        ekstra = kayit.get(None, [])
        if not isinstance(ekstra, list):
            ekstra = []

        yeni = {}

        yeni["tarih"] = (
            kayit.get("tarih")
            or kayit.get("Tarih")
            or bugunun_tarihi()
        )

        for sira, alan in enumerate(ALANLAR[1:], start=1):
            varsayilan = "0"

            if alan == "mesai_katsayi":
                varsayilan = "1.5"
            elif alan == "aciklama":
                varsayilan = ""

            deger = kayit.get(alan)

            if deger is None and len(ekstra) >= sira:
                deger = ekstra[sira - 1]

            if deger is None:
                deger = varsayilan

            yeni[alan] = deger

        normal_ucret, mesai_ucret, toplam = self.hesapla_kayittan(yeni)

        yeni["normal_ucret"] = f"{normal_ucret:.2f}"
        yeni["mesai_ucret"] = f"{mesai_ucret:.2f}"
        yeni["toplam"] = f"{toplam:.2f}"

        return yeni

    def son_ayarlari_getir(self):
        kayitlar = self.kayitlari_oku()

        if not kayitlar:
            return "0", "1.5"

        son = kayitlar[-1]

        gunluk = son.get("gunluk_ucret", "0")
        katsayi = son.get("mesai_katsayi", "1.5")

        if str(gunluk).strip() == "":
            gunluk = "0"

        if str(katsayi).strip() == "":
            katsayi = "1.5"

        return gunluk, katsayi

    def kayitlari_oku(self):
        if not os.path.exists(self.dosya_yolu):
            return []

        try:
            with open(self.dosya_yolu, "r", newline="", encoding="utf-8") as f:
                okuyucu = csv.DictReader(f)
                kayitlar = []
                for kayit in okuyucu:
                    if kayit:
                        kayitlar.append(self.kaydi_duzelt(kayit))
                return kayitlar
        except Exception:
            return []

    def kayitlari_yaz(self, kayitlar):
        with open(self.dosya_yolu, "w", newline="", encoding="utf-8") as f:
            yazici = csv.DictWriter(f, fieldnames=ALANLAR)
            yazici.writeheader()

            for kayit in kayitlar:
                temiz = {}

                for alan in ALANLAR:
                    temiz[alan] = kayit.get(alan, "")

                yazici.writerow(temiz)

    def hesapla_formdan(self):
        kayit = {
            "tarih": self.tarih.text,
            "gun_sayisi": self.gun_sayisi.text,
            "gunluk_ucret": self.gunluk_ucret.text,
            "mesai_saat": self.mesai_saat.text,
            "mesai_katsayi": self.mesai_katsayi.text,
            "prim": self.prim.text,
            "avans": self.avans.text,
            "kesinti": self.kesinti.text,
            "aciklama": self.aciklama.text,
        }

        normal_ucret, mesai_ucret, toplam = self.hesapla_kayittan(kayit)

        kayit["normal_ucret"] = f"{normal_ucret:.2f}"
        kayit["mesai_ucret"] = f"{mesai_ucret:.2f}"
        kayit["toplam"] = f"{toplam:.2f}"

        return kayit, normal_ucret, mesai_ucret, toplam

    def hesapla_kayittan(self, kayit):
        gun_sayisi = sayiya_cevir(kayit.get("gun_sayisi", "0"))
        gunluk_ucret = sayiya_cevir(kayit.get("gunluk_ucret", "0"))
        mesai_saat = sayiya_cevir(kayit.get("mesai_saat", "0"))
        mesai_katsayi = sayiya_cevir(kayit.get("mesai_katsayi", "1.5"))
        prim = sayiya_cevir(kayit.get("prim", "0"))
        avans = sayiya_cevir(kayit.get("avans", "0"))
        kesinti = sayiya_cevir(kayit.get("kesinti", "0"))

        normal_ucret = gun_sayisi * gunluk_ucret

        if gunluk_ucret > 0:
            saatlik_ucret = gunluk_ucret / 7.5
        else:
            saatlik_ucret = 0

        mesai_ucret = mesai_saat * saatlik_ucret * mesai_katsayi
        toplam = normal_ucret + mesai_ucret + prim - avans - kesinti

        return normal_ucret, mesai_ucret, toplam

    def kaydet(self, instance):
        kayit, normal_ucret, mesai_ucret, toplam = self.hesapla_formdan()

        if str(kayit["tarih"]).strip() == "":
            kayit["tarih"] = bugunun_tarihi()

        kayitlar = self.kayitlari_oku()
        kayitlar.append(kayit)
        self.kayitlari_yaz(kayitlar)

        self.mesai_saat.text = "0"
        self.prim.text = "0"
        self.avans.text = "0"
        self.kesinti.text = "0"
        self.aciklama.text = ""
        self.tarih.text = bugunun_tarihi()

        self.kayitlari_goster()

        self.mesaj_goster(
            "Kaydedildi",
            f"Normal: {para_yaz(normal_ucret)}\nMesai: {para_yaz(mesai_ucret)}\nNet: {para_yaz(toplam)}"
        )

    def filtre_temizle(self, instance):
        self.ay_filtre.text = ""
        self.kayitlari_goster()

    def filtreye_uyuyor_mu(self, kayit):
        filtre = self.ay_filtre.text.strip()

        if filtre == "":
            return True

        kayit_ayi = tarih_ay_anahtari(kayit.get("tarih", ""))

        if filtre == kayit_ayi:
            return True

        if filtre in str(kayit.get("tarih", "")):
            return True

        return False

    def kayitlari_goster(self, instance=None):
        tum_kayitlar = self.kayitlari_oku()

        gorunenler = []

        for orijinal_indeks, kayit in enumerate(tum_kayitlar):
            if self.filtreye_uyuyor_mu(kayit):
                gorunenler.append((orijinal_indeks, kayit))

        gorunenler = list(reversed(gorunenler))
        self.gorunen_indeksler = [indeks for indeks, kayit in gorunenler]

        toplam_gun = 0.0
        toplam_mesai_saat = 0.0
        toplam_normal = 0.0
        toplam_mesai_ucret = 0.0
        toplam_prim = 0.0
        toplam_avans = 0.0
        toplam_kesinti = 0.0
        net_toplam = 0.0

        satirlar = []

        for sira, (orijinal_indeks, kayit) in enumerate(gorunenler, start=1):
            normal_ucret, mesai_ucret, toplam = self.hesapla_kayittan(kayit)

            gun = sayiya_cevir(kayit.get("gun_sayisi", "0"))
            mesai_saat = sayiya_cevir(kayit.get("mesai_saat", "0"))
            prim = sayiya_cevir(kayit.get("prim", "0"))
            avans = sayiya_cevir(kayit.get("avans", "0"))
            kesinti = sayiya_cevir(kayit.get("kesinti", "0"))
            aciklama = str(kayit.get("aciklama", "")).strip()

            toplam_gun += gun
            toplam_mesai_saat += mesai_saat
            toplam_normal += normal_ucret
            toplam_mesai_ucret += mesai_ucret
            toplam_prim += prim
            toplam_avans += avans
            toplam_kesinti += kesinti
            net_toplam += toplam

            aciklama_satiri = ""
            if aciklama:
                aciklama_satiri = f"\n   Not: {aciklama}"

            satirlar.append(
                f"{sira}) {kayit.get('tarih', '')}\n"
                f"   Gün: {gun:g} | Mesai: {mesai_saat:g} saat | Net: {para_yaz(toplam)}\n"
                f"   Normal: {para_yaz(normal_ucret)} | Mesai: {para_yaz(mesai_ucret)}\n"
                f"   Prim: {para_yaz(prim)} | Avans: {para_yaz(avans)} | Kesinti: {para_yaz(kesinti)}"
                f"{aciklama_satiri}\n"
            )

        filtre = self.ay_filtre.text.strip()

        if filtre:
            baslik = f"Ay filtresi: {filtre}"
        else:
            baslik = "Tüm kayıtlar"

        self.sonuc.text = (
            f"{baslik} | Kayıt: {len(gorunenler)}\n"
            f"Gün: {toplam_gun:g} | Mesai: {toplam_mesai_saat:g} saat\n"
            f"Normal: {para_yaz(toplam_normal)} | Mesai: {para_yaz(toplam_mesai_ucret)}\n"
            f"Prim: {para_yaz(toplam_prim)} | Avans: {para_yaz(toplam_avans)} | Kesinti: {para_yaz(toplam_kesinti)}\n"
            f"NET TOPLAM: {para_yaz(net_toplam)}"
        )

        if satirlar:
            self.kayit_label.text = "\n".join(satirlar)
        else:
            self.kayit_label.text = "Bu filtrede kayıt yok."

    def kaydi_sil(self, instance):
        no_metni = self.silinecek_no.text.strip()

        if no_metni == "":
            self.mesaj_goster("Eksik bilgi", "Silmek istediğin kayıt numarasını yaz.")
            return

        try:
            no = int(no_metni)
        except Exception:
            self.mesaj_goster("Hatalı numara", "Kayıt numarası sayı olmalı.")
            return

        if no < 1 or no > len(self.gorunen_indeksler):
            self.mesaj_goster("Bulunamadı", "Bu numarada görünen bir kayıt yok.")
            return

        tum_kayitlar = self.kayitlari_oku()
        silinecek_orijinal_indeks = self.gorunen_indeksler[no - 1]

        if silinecek_orijinal_indeks < 0 or silinecek_orijinal_indeks >= len(tum_kayitlar):
            self.mesaj_goster("Hata", "Kayıt bulunamadı.")
            return

        silinen = tum_kayitlar.pop(silinecek_orijinal_indeks)
        self.kayitlari_yaz(tum_kayitlar)

        self.silinecek_no.text = ""
        self.kayitlari_goster()

        self.mesaj_goster(
            "Silindi",
            f"Tarih: {silinen.get('tarih', '')}\nNet: {para_yaz(silinen.get('toplam', '0'))}"
        )


if __name__ == "__main__":
    MaasTakipApp().run()
