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


class MaasTakipApp(App):
    def build(self):
        self.title = "Maaş Takip"

        self.dosya_yolu = os.path.join(self.user_data_dir, "maas_kayitlari.csv")
        self.dosya_hazirla()

        ana = BoxLayout(
            orientation="vertical",
            padding=12,
            spacing=8
        )

        baslik = Label(
            text="Maaş ve Mesai Takip",
            size_hint_y=None,
            height=45,
            font_size=24,
            bold=True
        )
        ana.add_widget(baslik)

        form_scroll = ScrollView(size_hint=(1, 0.55))
        form = GridLayout(
            cols=2,
            spacing=8,
            padding=5,
            size_hint_y=None
        )
        form.bind(minimum_height=form.setter("height"))

        self.tarih = self.input_ekle(form, "Tarih", datetime.now().strftime("%d.%m.%Y"))
        self.gun_sayisi = self.input_ekle(form, "Gün sayısı", "1")
        self.gunluk_ucret = self.input_ekle(form, "Günlük ücret TL", "0")
        self.mesai_saat = self.input_ekle(form, "Mesai saati", "0")
        self.mesai_katsayi = self.input_ekle(form, "Mesai katsayısı", "1.5")
        self.prim = self.input_ekle(form, "Prim TL", "0")
        self.avans = self.input_ekle(form, "Avans TL", "0")
        self.kesinti = self.input_ekle(form, "Kesinti TL", "0")
        self.aciklama = self.input_ekle(form, "Açıklama", "")

        form_scroll.add_widget(form)
        ana.add_widget(form_scroll)

        butonlar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=60,
            spacing=8
        )

        kaydet_btn = Button(text="Kaydet")
        kaydet_btn.bind(on_press=self.kaydet)

        yenile_btn = Button(text="Toplamı Göster")
        yenile_btn.bind(on_press=self.kayitlari_goster)

        butonlar.add_widget(kaydet_btn)
        butonlar.add_widget(yenile_btn)

        ana.add_widget(butonlar)

        self.sonuc = Label(
            text="Henüz hesaplama yapılmadı.",
            size_hint_y=None,
            height=70,
            font_size=17
        )
        ana.add_widget(self.sonuc)

        kayit_baslik = Label(
            text="Kayıtlar",
            size_hint_y=None,
            height=35,
            font_size=20,
            bold=True
        )
        ana.add_widget(kayit_baslik)

        self.kayit_scroll = ScrollView(size_hint=(1, 0.45))
        self.kayit_label = Label(
            text="",
            size_hint_y=None,
            halign="left",
            valign="top",
            font_size=15
        )
        self.kayit_label.bind(texture_size=self.kayit_label.setter("size"))
        self.kayit_scroll.add_widget(self.kayit_label)
        ana.add_widget(self.kayit_scroll)

        self.kayitlari_goster()

        return ana

    def input_ekle(self, form, baslik, varsayilan):
        lbl = Label(
            text=baslik,
            size_hint_y=None,
            height=45,
            halign="left"
        )

        inp = TextInput(
            text=varsayilan,
            multiline=False,
            size_hint_y=None,
            height=45
        )

        form.add_widget(lbl)
        form.add_widget(inp)

        return inp

    def dosya_hazirla(self):
        if not os.path.exists(self.dosya_yolu):
            with open(self.dosya_yolu, "w", newline="", encoding="utf-8") as f:
                yazici = csv.writer(f)
                yazici.writerow([
                    "tarih",
                    "gun_sayisi",
                    "gunluk_ucret",
                    "mesai_saat",
                    "mesai_katsayi",
                    "prim",
                    "avans",
                    "kesinti",
                    "toplam",
                    "aciklama"
                ])

    def hesapla(self):
        gun_sayisi = sayiya_cevir(self.gun_sayisi.text)
        gunluk_ucret = sayiya_cevir(self.gunluk_ucret.text)
        mesai_saat = sayiya_cevir(self.mesai_saat.text)
        mesai_katsayi = sayiya_cevir(self.mesai_katsayi.text)
        prim = sayiya_cevir(self.prim.text)
        avans = sayiya_cevir(self.avans.text)
        kesinti = sayiya_cevir(self.kesinti.text)

        normal_ucret = gun_sayisi * gunluk_ucret

        saatlik_ucret = gunluk_ucret / 7.5 if gunluk_ucret > 0 else 0
        mesai_ucret = mesai_saat * saatlik_ucret * mesai_katsayi

        toplam = normal_ucret + mesai_ucret + prim - avans - kesinti

        return toplam, normal_ucret, mesai_ucret

    def kaydet(self, instance):
        toplam, normal_ucret, mesai_ucret = self.hesapla()

        with open(self.dosya_yolu, "a", newline="", encoding="utf-8") as f:
            yazici = csv.writer(f)
            yazici.writerow([
                self.tarih.text,
                self.gun_sayisi.text,
                self.gunluk_ucret.text,
                self.mesai_saat.text,
                self.mesai_katsayi.text,
                self.prim.text,
                self.avans.text,
                self.kesinti.text,
                f"{toplam:.2f}",
                self.aciklama.text
            ])

        self.sonuc.text = (
            f"Kayıt eklendi.\n"
            f"Normal: {normal_ucret:.2f} TL | Mesai: {mesai_ucret:.2f} TL | Toplam: {toplam:.2f} TL"
        )

        self.kayitlari_goster()

    def kayitlari_goster(self, instance=None):
        toplam_maas = 0.0
        toplam_gun = 0.0
        toplam_mesai = 0.0
        satirlar = []

        if not os.path.exists(self.dosya_yolu):
            self.kayit_label.text = "Kayıt bulunamadı."
            return

        with open(self.dosya_yolu, "r", newline="", encoding="utf-8") as f:
            okuyucu = csv.DictReader(f)

            for kayit in okuyucu:
                tarih = kayit.get("tarih", "")
                gun = sayiya_cevir(kayit.get("gun_sayisi", "0"))
                mesai = sayiya_cevir(kayit.get("mesai_saat", "0"))
                toplam = sayiya_cevir(kayit.get("toplam", "0"))
                aciklama = kayit.get("aciklama", "")

                toplam_maas += toplam
                toplam_gun += gun
                toplam_mesai += mesai

                satirlar.append(
                    f"{tarih} | Gün: {gun:g} | Mesai: {mesai:g} saat | {toplam:.2f} TL | {aciklama}"
                )

        self.sonuc.text = (
            f"Toplam gün: {toplam_gun:g}\n"
            f"Toplam mesai: {toplam_mesai:g} saat | Genel toplam: {toplam_maas:.2f} TL"
        )

        if satirlar:
            self.kayit_label.text = "\n".join(reversed(satirlar))
        else:
            self.kayit_label.text = "Henüz kayıt yok."


if __name__ == "__main__":
    MaasTakipApp().run()
