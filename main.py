import os
import csv
import json
from datetime import datetime

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup


ALANLAR = [
    "tarih",
    "aylik_maas_snapshot",
    "gunluk_calisma_saati_snapshot",
    "hafta_tatili_gunu_snapshot",
    "mesai_katsayi_snapshot",
    "gun_turu_secim",
    "gun_turu",
    "tatil_adi",
    "calisma_durumu",
    "mesai_saat",
    "prim",
    "avans",
    "kesinti",
    "tatil_ek_ucret",
    "mesai_ucret",
    "toplam_ek",
    "aciklama",
]

RENK_ARKA_PLAN = [0.05, 0.07, 0.11, 1]
RENK_KART = [0.10, 0.14, 0.22, 1]
RENK_KART_2 = [0.13, 0.18, 0.28, 1]
RENK_YAZI = [0.95, 0.97, 1.00, 1]
RENK_SOLUK_YAZI = [0.70, 0.76, 0.86, 1]
RENK_MAVI = [0.18, 0.48, 0.95, 1]
RENK_MAVI_KOYU = [0.10, 0.35, 0.78, 1]
RENK_YESIL = [0.10, 0.65, 0.38, 1]
RENK_YESIL_KOYU = [0.07, 0.48, 0.28, 1]
RENK_KIRMIZI = [0.88, 0.20, 0.25, 1]
RENK_KIRMIZI_KOYU = [0.62, 0.12, 0.16, 1]
RENK_TURUNCU = [0.95, 0.55, 0.16, 1]
RENK_MOR = [0.45, 0.28, 0.95, 1]
RENK_MOR_KOYU = [0.30, 0.18, 0.72, 1]

HAFTA_GUNLERI = {
    "Pazartesi": 0,
    "Salı": 1,
    "Çarşamba": 2,
    "Perşembe": 3,
    "Cuma": 4,
    "Cumartesi": 5,
    "Pazar": 6,
}

HAFTA_GUN_ADLARI = [
    "Pazartesi",
    "Salı",
    "Çarşamba",
    "Perşembe",
    "Cuma",
    "Cumartesi",
    "Pazar",
]

GUN_TURU_SECENEKLERI = [
    "Otomatik",
    "Normal Gün",
    "Hafta Tatili",
    "Resmi Tatil",
    "Yarım Resmi Tatil",
]

CALISMA_SECENEKLERI = [
    "Çalıştım",
    "Çalışmadım",
]

RESMI_TATILLER_2026 = {
    "2026-03-19": ("Ramazan Bayramı Arifesi", 0.5),
    "2026-03-20": ("Ramazan Bayramı 1. Gün", 1.0),
    "2026-03-21": ("Ramazan Bayramı 2. Gün", 1.0),
    "2026-03-22": ("Ramazan Bayramı 3. Gün", 1.0),
    "2026-05-26": ("Kurban Bayramı Arifesi", 0.5),
    "2026-05-27": ("Kurban Bayramı 1. Gün", 1.0),
    "2026-05-28": ("Kurban Bayramı 2. Gün", 1.0),
    "2026-05-29": ("Kurban Bayramı 3. Gün", 1.0),
    "2026-05-30": ("Kurban Bayramı 4. Gün", 1.0),
}


def bugunun_tarihi():
    return datetime.now().strftime("%d.%m.%Y")


def bu_ay():
    return datetime.now().strftime("%m.%Y")


def varsayilan_ayarlar():
    return {
        "aylik_maas": "0",
        "hafta_tatili_gunu": "Pazar",
        "mesai_katsayi": "1.5",
        "gunluk_calisma_saati": "7.5",
    }


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


def sayi_yaz(deger):
    deger = sayiya_cevir(deger)

    if deger == int(deger):
        return str(int(deger))

    return str(deger).replace(".", ",")


def para_yaz(deger):
    return f"{sayiya_cevir(deger):,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")


def tarih_parse(tarih_metni):
    tarih_metni = str(tarih_metni).strip()

    formatlar = [
        "%d.%m.%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
    ]

    for fmt in formatlar:
        try:
            return datetime.strptime(tarih_metni, fmt)
        except Exception:
            pass

    return None


def tarih_ay_anahtari(tarih_metni):
    tarih = tarih_parse(tarih_metni)

    if tarih:
        return tarih.strftime("%m.%Y")

    tarih_metni = str(tarih_metni).strip()

    if len(tarih_metni) >= 7:
        return tarih_metni[-7:]

    return ""


def resmi_tatil_bilgisi(tarih):
    if tarih is None:
        return None, 0.0

    iso = tarih.strftime("%Y-%m-%d")

    if iso in RESMI_TATILLER_2026:
        return RESMI_TATILLER_2026[iso]

    sabitler = {
        (1, 1): ("Yılbaşı", 1.0),
        (4, 23): ("23 Nisan Ulusal Egemenlik ve Çocuk Bayramı", 1.0),
        (5, 1): ("1 Mayıs Emek ve Dayanışma Günü", 1.0),
        (5, 19): ("19 Mayıs Atatürk'ü Anma, Gençlik ve Spor Bayramı", 1.0),
        (7, 15): ("15 Temmuz Demokrasi ve Millî Birlik Günü", 1.0),
        (8, 30): ("30 Ağustos Zafer Bayramı", 1.0),
        (10, 28): ("Cumhuriyet Bayramı Arifesi", 0.5),
        (10, 29): ("29 Ekim Cumhuriyet Bayramı", 1.0),
    }

    return sabitler.get((tarih.month, tarih.day), (None, 0.0))


def gun_turu_hesapla(tarih_metni, hafta_tatili_gunu, gun_turu_secim):
    tarih = tarih_parse(tarih_metni)

    if tarih is None:
        return "Normal Gün", "Tarih okunamadı", 0.0

    if gun_turu_secim == "Normal Gün":
        return "Normal Gün", HAFTA_GUN_ADLARI[tarih.weekday()], 0.0

    if gun_turu_secim == "Hafta Tatili":
        return "Hafta Tatili", "Manuel hafta tatili", 0.0

    if gun_turu_secim == "Resmi Tatil":
        return "Resmi Tatil", "Manuel resmi tatil", 1.0

    if gun_turu_secim == "Yarım Resmi Tatil":
        return "Yarım Resmi Tatil", "Manuel yarım resmi tatil", 0.5

    tatil_adi, tatil_orani = resmi_tatil_bilgisi(tarih)

    if tatil_adi:
        if tatil_orani == 0.5:
            return "Yarım Resmi Tatil", tatil_adi, tatil_orani

        return "Resmi Tatil", tatil_adi, tatil_orani

    hafta_tatili_index = HAFTA_GUNLERI.get(hafta_tatili_gunu, 6)

    if tarih.weekday() == hafta_tatili_index:
        return "Hafta Tatili", hafta_tatili_gunu, 0.0

    return "Normal Gün", HAFTA_GUN_ADLARI[tarih.weekday()], 0.0


class YuvarlakKutu(BoxLayout):
    bg_color = ListProperty([1, 1, 1, 1])
    radius = NumericProperty(18)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            self.renk = Color(rgba=self.bg_color)
            self.arka_plan = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.radius]
            )

        self.bind(pos=self.guncelle)
        self.bind(size=self.guncelle)
        self.bind(bg_color=self.renk_guncelle)
        self.bind(radius=self.guncelle)

    def guncelle(self, *args):
        self.arka_plan.pos = self.pos
        self.arka_plan.size = self.size
        self.arka_plan.radius = [self.radius]

    def renk_guncelle(self, *args):
        self.renk.rgba = self.bg_color


class ModernButon(Button):
    bg_color = ListProperty(RENK_MAVI)
    bg_down_color = ListProperty(RENK_MAVI_KOYU)
    radius = NumericProperty(14)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = [0, 0, 0, 0]
        self.color = RENK_YAZI
        self.bold = True
        self.font_size = dp(13)

        with self.canvas.before:
            self.renk = Color(rgba=self.bg_color)
            self.arka_plan = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.radius]
            )

        self.bind(pos=self.guncelle)
        self.bind(size=self.guncelle)
        self.bind(state=self.durum_guncelle)
        self.bind(bg_color=self.durum_guncelle)
        self.bind(bg_down_color=self.durum_guncelle)

    def guncelle(self, *args):
        self.arka_plan.pos = self.pos
        self.arka_plan.size = self.size
        self.arka_plan.radius = [self.radius]

    def durum_guncelle(self, *args):
        if self.state == "down":
            self.renk.rgba = self.bg_down_color
        else:
            self.renk.rgba = self.bg_color


class ModernSpinner(Spinner):
    bg_color = ListProperty(RENK_KART_2)
    bg_down_color = ListProperty([0.18, 0.24, 0.36, 1])
    radius = NumericProperty(14)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = [0, 0, 0, 0]
        self.color = RENK_YAZI
        self.bold = True
        self.font_size = dp(13)

        with self.canvas.before:
            self.renk = Color(rgba=self.bg_color)
            self.arka_plan = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.radius]
            )

        self.bind(pos=self.guncelle)
        self.bind(size=self.guncelle)
        self.bind(state=self.durum_guncelle)

    def guncelle(self, *args):
        self.arka_plan.pos = self.pos
        self.arka_plan.size = self.size
        self.arka_plan.radius = [self.radius]

    def durum_guncelle(self, *args):
        if self.state == "down":
            self.renk.rgba = self.bg_down_color
        else:
            self.renk.rgba = self.bg_color


class ModernInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_active = ""
        self.background_color = [0.94, 0.96, 1.00, 1]
        self.foreground_color = [0.05, 0.07, 0.11, 1]
        self.cursor_color = RENK_MAVI
        self.hint_text_color = [0.45, 0.48, 0.55, 1]
        self.font_size = dp(15)
        self.padding = [dp(10), dp(10), dp(10), dp(10)]
        self.multiline = False


class MaasTakipApp(App):
    def build(self):
        self.title = "Maaş Takip v0.5"
        Window.clearcolor = RENK_ARKA_PLAN
        Window.softinput_mode = "below_target"

        self.dosya_yolu = os.path.join(self.user_data_dir, "maas_kayitlari.csv")
        self.ayarlar_yolu = os.path.join(self.user_data_dir, "ayarlar.json")
        self.ayarlar = self.ayarlari_oku()
        self.dosyayi_hazirla_ve_duzelt()
        self.gorunen_indeksler = []

        ana = YuvarlakKutu(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8),
            bg_color=RENK_ARKA_PLAN,
            radius=0
        )

        ust_kart = YuvarlakKutu(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(2),
            size_hint_y=None,
            height=dp(82),
            bg_color=RENK_KART,
            radius=22
        )

        baslik = Label(
            text="Maaş Takip v0.5",
            color=RENK_YAZI,
            font_size=dp(24),
            bold=True,
            halign="left",
            valign="middle"
        )
        baslik.bind(width=self.label_genislik_ayarla)

        alt = Label(
            text="Ayarlar kaydedilir, kayıtlar maaşa göre otomatik hesaplanır",
            color=RENK_SOLUK_YAZI,
            font_size=dp(12),
            halign="left",
            valign="middle"
        )
        alt.bind(width=self.label_genislik_ayarla)

        ust_kart.add_widget(baslik)
        ust_kart.add_widget(alt)
        ana.add_widget(ust_kart)

        nav = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(6)
        )

        b_ayar = ModernButon(
            text="Ayarlar",
            bg_color=RENK_MOR,
            bg_down_color=RENK_MOR_KOYU
        )
        b_ekle = ModernButon(
            text="Kayıt Ekle",
            bg_color=RENK_YESIL,
            bg_down_color=RENK_YESIL_KOYU
        )
        b_kayit = ModernButon(
            text="Kayıtlar",
            bg_color=RENK_MAVI,
            bg_down_color=RENK_MAVI_KOYU
        )
        b_ozet = ModernButon(
            text="Özet",
            bg_color=RENK_TURUNCU,
            bg_down_color=[0.75, 0.38, 0.08, 1]
        )

        b_ayar.bind(on_press=lambda x: self.show_ayarlar())
        b_ekle.bind(on_press=lambda x: self.show_kayit_ekle())
        b_kayit.bind(on_press=lambda x: self.show_kayitlar())
        b_ozet.bind(on_press=lambda x: self.show_ozet())

        nav.add_widget(b_ayar)
        nav.add_widget(b_ekle)
        nav.add_widget(b_kayit)
        nav.add_widget(b_ozet)
        ana.add_widget(nav)

        self.content = YuvarlakKutu(
            orientation="vertical",
            padding=dp(0),
            spacing=dp(0),
            bg_color=RENK_ARKA_PLAN,
            radius=0
        )
        ana.add_widget(self.content)

        self.show_ayarlar()

        return ana

    def label_genislik_ayarla(self, instance, width):
        instance.text_size = (width, None)

    def label_yukseklik_ayarla(self, instance, texture_size):
        instance.height = texture_size[1] + dp(20)

    def temizle(self):
        self.content.clear_widgets()

    def kart(self, **kwargs):
        return YuvarlakKutu(
            bg_color=RENK_KART,
            radius=22,
            padding=dp(12),
            spacing=dp(8),
            **kwargs
        )

    def input_satiri(self, form, baslik, varsayilan, hint=""):
        lbl = Label(
            text=baslik,
            size_hint_y=None,
            height=dp(42),
            color=RENK_SOLUK_YAZI,
            font_size=dp(13),
            halign="left",
            valign="middle"
        )
        lbl.bind(width=self.label_genislik_ayarla)

        inp = ModernInput(
            text=str(varsayilan),
            hint_text=hint,
            size_hint_y=None,
            height=dp(42)
        )

        form.add_widget(lbl)
        form.add_widget(inp)

        return inp

    def spinner_satiri(self, form, baslik, varsayilan, secenekler):
        lbl = Label(
            text=baslik,
            size_hint_y=None,
            height=dp(42),
            color=RENK_SOLUK_YAZI,
            font_size=dp(13),
            halign="left",
            valign="middle"
        )
        lbl.bind(width=self.label_genislik_ayarla)

        spn = ModernSpinner(
            text=varsayilan,
            values=secenekler,
            size_hint_y=None,
            height=dp(42)
        )

        form.add_widget(lbl)
        form.add_widget(spn)

        return spn

    def ekran_baslik(self, metin, alt_metin=""):
        kutu = YuvarlakKutu(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(2),
            size_hint_y=None,
            height=dp(70),
            bg_color=RENK_KART_2,
            radius=20
        )

        baslik = Label(
            text=metin,
            color=RENK_YAZI,
            font_size=dp(20),
            bold=True,
            halign="left",
            valign="middle"
        )
        baslik.bind(width=self.label_genislik_ayarla)
        kutu.add_widget(baslik)

        if alt_metin:
            alt = Label(
                text=alt_metin,
                color=RENK_SOLUK_YAZI,
                font_size=dp(12),
                halign="left",
                valign="middle"
            )
            alt.bind(width=self.label_genislik_ayarla)
            kutu.add_widget(alt)

        return kutu

    def mesaj_goster(self, baslik, mesaj):
        kutu = YuvarlakKutu(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(12),
            bg_color=RENK_KART,
            radius=20
        )

        yazi = Label(
            text=mesaj,
            color=RENK_YAZI,
            font_size=dp(15),
            halign="center",
            valign="middle"
        )
        yazi.bind(width=self.label_genislik_ayarla)

        kapat_btn = ModernButon(
            text="Tamam",
            size_hint_y=None,
            height=dp(46),
            bg_color=RENK_MAVI,
            bg_down_color=RENK_MAVI_KOYU
        )

        kutu.add_widget(yazi)
        kutu.add_widget(kapat_btn)

        popup = Popup(
            title=baslik,
            content=kutu,
            size_hint=(0.88, 0.42),
            background_color=[0.05, 0.07, 0.11, 1],
            separator_color=RENK_MAVI,
            title_color=RENK_YAZI
        )
        kapat_btn.bind(on_press=popup.dismiss)
        popup.open()

    def ayarlari_oku(self):
        ayarlar = varsayilan_ayarlar()

        if os.path.exists(self.ayarlar_yolu):
            try:
                with open(self.ayarlar_yolu, "r", encoding="utf-8") as f:
                    okunan = json.load(f)

                if isinstance(okunan, dict):
                    ayarlar.update(okunan)
            except Exception:
                pass

        if ayarlar.get("hafta_tatili_gunu") not in HAFTA_GUNLERI:
            ayarlar["hafta_tatili_gunu"] = "Pazar"

        if str(ayarlar.get("mesai_katsayi", "")).strip() == "":
            ayarlar["mesai_katsayi"] = "1.5"

        if str(ayarlar.get("gunluk_calisma_saati", "")).strip() == "":
            ayarlar["gunluk_calisma_saati"] = "7.5"

        if str(ayarlar.get("aylik_maas", "")).strip() == "":
            ayarlar["aylik_maas"] = "0"

        return ayarlar

    def ayarlari_yaz(self):
        with open(self.ayarlar_yolu, "w", encoding="utf-8") as f:
            json.dump(self.ayarlar, f, ensure_ascii=False, indent=2)

    def gunluk_ucret(self, maas=None):
        if maas is None:
            maas = self.ayarlar.get("aylik_maas", "0")

        maas = sayiya_cevir(maas)

        if maas > 0:
            return maas / 30

        return 0.0

    def saatlik_ucret(self, maas=None, gunluk_saat=None):
        if maas is None:
            maas = self.ayarlar.get("aylik_maas", "0")

        if gunluk_saat is None:
            gunluk_saat = self.ayarlar.get("gunluk_calisma_saati", "7.5")

        gunluk = self.gunluk_ucret(maas)
        saat = sayiya_cevir(gunluk_saat)

        if gunluk > 0 and saat > 0:
            return gunluk / saat

        return 0.0

    def show_ayarlar(self):
        self.temizle()

        ana = BoxLayout(
            orientation="vertical",
            spacing=dp(8)
        )

        ana.add_widget(
            self.ekran_baslik(
                "Ayarlar",
                "Maaşı bir kere yaz, uygulama bütün hesabı ona göre yapsın."
            )
        )

        kart = self.kart(orientation="vertical")

        form = GridLayout(
            cols=2,
            spacing=dp(7),
            padding=dp(2),
            size_hint_y=None
        )
        form.bind(minimum_height=form.setter("height"))

        self.ayar_maas = self.input_satiri(
            form,
            "Aylık maaş",
            self.ayarlar.get("aylik_maas", "0"),
            "Örn: 35000"
        )

        self.ayar_gunluk_saat = self.input_satiri(
            form,
            "Günlük çalışma saati",
            self.ayarlar.get("gunluk_calisma_saati", "7.5"),
            "Örn: 7.5"
        )

        self.ayar_mesai_katsayi = self.input_satiri(
            form,
            "Mesai katsayısı",
            self.ayarlar.get("mesai_katsayi", "1.5"),
            "Örn: 1.5"
        )

        self.ayar_hafta_tatili = self.spinner_satiri(
            form,
            "Hafta tatilin",
            self.ayarlar.get("hafta_tatili_gunu", "Pazar"),
            list(HAFTA_GUNLERI.keys())
        )

        kart.add_widget(form)

        self.ayar_bilgi = Label(
            text="",
            color=RENK_SOLUK_YAZI,
            font_size=dp(14),
            size_hint_y=None,
            height=dp(78),
            halign="left",
            valign="top"
        )
        self.ayar_bilgi.bind(width=self.label_genislik_ayarla)
        kart.add_widget(self.ayar_bilgi)

        btn_satir = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(52),
            spacing=dp(8)
        )

        kaydet = ModernButon(
            text="Ayarları Kaydet",
            bg_color=RENK_YESIL,
            bg_down_color=RENK_YESIL_KOYU
        )
        kaydet.bind(on_press=self.ayarlari_kaydet)

        hesapla = ModernButon(
            text="Hesabı Göster",
            bg_color=RENK_MAVI,
            bg_down_color=RENK_MAVI_KOYU
        )
        hesapla.bind(on_press=lambda x: self.ayar_bilgisi_guncelle())

        btn_satir.add_widget(kaydet)
        btn_satir.add_widget(hesapla)
        kart.add_widget(btn_satir)

        ana.add_widget(kart)
        self.content.addf.label_genislik_ayarla)

        alt_baslik = Label(
            text="Aylık maaşa göre mesai, tatil, prim, avans ve kesinti hesabı",
            color=RENK_SOLUK_YAZI,
            font_size=dp(13),
            halign="left",
            valign="middle"
        )
        alt_baslik.bind(width=self.label_genislik_ayarla)

        ust_kart.add_widget(baslik)
        ust_kart.add_widget(alt_baslik)
        ana.add_widget(ust_kart)

        maas_kart = YuvarlakKutu(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(7),
            bg_color=RENK_KART_2,
            radius=20,
            size_hint_y=None,
            height=dp(122)
        )

        maas_baslik = Label(
            text="Aylık Maaş",
            color=RENK_YAZI,
            font_size=dp(18),
            bold=True,
            size_hint_y=None,
            height=dp(28),
            halign="left",
            valign="middle"
        )
        maas_baslik.bind(width=self.label_genislik_ayarla)

        self.aylik_maas = ModernInput(
            text=varsayilan_maas,
            hint_text="Örn: 35000",
            size_hint_y=None,
            height=dp(45)
        )

        self.maas_bilgi = Label(
            text="Günlük: 0,00 TL | Saatlik: 0,00 TL",
            color=RENK_SOLUK_YAZI,
            font_size=dp(13),
            size_hint_y=None,
            height=dp(24),
            halign="left",
            valign="middle"
        )
        self.maas_bilgi.bind(width=self.label_genislik_ayarla)

        self.aylik_maas.bind(text=self.maas_bilgisi_guncelle)

        maas_kart.add_widget(maas_baslik)
        maas_kart.add_widget(self.aylik_maas)
        maas_kart.add_widget(self.maas_bilgi)
        ana.add_widget(maas_kart)

        form_kart = YuvarlakKutu(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8),
            bg_color=RENK_KART,
            radius=22,
            size_hint_y=0.44
        )

        form_baslik = Label(
            text="Yeni Kayıt",
            color=RENK_YAZI,
            font_size=dp(18),
            bold=True,
            size_hint_y=None,
            height=dp(28),
            halign="left",
            valign="middle"
        )
        form_baslik.bind(width=self.label_genislik_ayarla)
        form_kart.add_widget(form_baslik)

        form_scroll = ScrollView()

        form = GridLayout(
            cols=2,
            spacing=dp(7),
            padding=dp(2),
            size_hint_y=None
        )
        form.bind(minimum_height=form.setter("height"))

        self.tarih = self.input_ekle(form, "Tarih", bugunun_tarihi())

        self.hafta_tatili_gunu = self.spinner_ekle(
            form,
            "Hafta tatilin",
            varsayilan_hafta_tatili,
            list(HAFTA_GUNLERI.keys())
        )

        self.gun_turu_secim = self.spinner_ekle(
            form,
            "Gün türü",
            "Otomatik",
            GUN_TURU_SECENEKLERI
        )

        self.calisma_durumu = self.spinner_ekle(
            form,
            "Durum",
            "Çalıştım",
            CALISMA_SECENEKLERI
        )

        self.mesai_saat = self.input_ekle(form, "Ek mesai saati", "0")
        self.mesai_katsayi = self.input_ekle(form, "Mesai katsayısı", varsayilan_katsayi)
        self.prim = self.input_ekle(form, "Prim", "0")
        self.avans = self.input_ekle(form, "Avans", "0")
        self.kesinti = self.input_ekle(form, "Kesinti", "0")
        self.aciklama = self.input_ekle(form, "Açıklama", "")

        form_scroll.add_widget(form)
        form_kart.add_widget(form_scroll)
        ana.add_widget(form_kart)

        butonlar_1 = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(52),
            spacing=dp(8)
        )

        kaydet_btn = ModernButon(
            text="Kaydet",
            bg_color=RENK_YESIL,
            bg_down_color=RENK_YESIL_KOYU
        )
        kaydet_btn.bind(on_press=self.kaydet)

        hesap_btn = ModernButon(
            text="Hesapla",
            bg_color=RENK_MAVI,
            bg_down_color=RENK_MAVI_KOYU
        )
        hesap_btn.bind(on_press=self.anlik_hesap_goster)

        butonlar_1.add_widget(kaydet_btn)
        butonlar_1.add_widget(hesap_btn)
        ana.add_widget(butonlar_1)

        filtre_satiri = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(7)
        )

        self.ay_filtre = ModernInput(
            text=bu_ay(),
            hint_text="Ay: 04.2026"
        )

        filtre_btn = ModernButon(
            text="Ayı Göster",
            bg_color=RENK_TURUNCU,
            bg_down_color=[0.75, 0.38, 0.08, 1]
        )
        filtre_btn.bind(on_press=self.kayitlari_goster)

        temizle_btn = ModernButon(
            text="Tümü",
            bg_color=RENK_KART_2,
            bg_down_color=[0.18, 0.24, 0.36, 1]
        )
        temizle_btn.bind(on_press=self.filtre_temizle)

        filtre_satiri.add_widget(self.ay_filtre)
        filtre_satiri.add_widget(filtre_btn)
        filtre_satiri.add_widget(temizle_btn)
        ana.add_widget(filtre_satiri)

        sil_satiri = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(7)
        )

        self.silinecek_no = ModernInput(
            text="",
            hint_text="Silinecek no",
            input_filter="int"
        )

        sil_btn = ModernButon(
            text="Kaydı Sil",
            bg_color=RENK_KIRMIZI,
            bg_down_color=RENK_KIRMIZI_KOYU
        )
        sil_btn.bind(on_press=self.kaydi_sil)

        sil_satiri.add_widget(self.silinecek_no)
        sil_satiri.add_widget(sil_btn)
        ana.add_widget(sil_satiri)

        ozet_kart = YuvarlakKutu(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(4),
            bg_color=RENK_KART_2,
            radius=20,
            size_hint_y=None,
            height=dp(128)
        )

        ozet_baslik = Label(
            text="Özet",
            color=RENK_YAZI,
            font_size=dp(17),
            bold=True,
            size_hint_y=None,
            height=dp(24),
            halign="left",
            valign="middle"
        )
        ozet_baslik.bind(width=self.label_genislik_ayarla)

        self.sonuc = Label(
            text="Hazır.",
            color=RENK_SOLUK_YAZI,
            font_size=dp(13),
            halign="left",
            valign="top"
        )
        self.sonuc.bind(width=self.label_genislik_ayarla)

        ozet_kart.add_widget(ozet_baslik)
        ozet_kart.add_widget(self.sonuc)
        ana.add_widget(ozet_kart)

        kayit_kart = YuvarlakKutu(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(6),
            bg_color=RENK_KART,
            radius=22,
            size_hint_y=0.56
        )

        kayit_baslik = Label(
            text="Kayıtlar",
            color=RENK_YAZI,
            size_hint_y=None,
            height=dp(30),
            font_size=dp(18),
            bold=True,
            halign="left",
            valign="middle"
        )
        kayit_baslik.bind(width=self.label_genislik_ayarla)
        kayit_kart.add_widget(kayit_baslik)

        self.kayit_scroll = ScrollView()

        self.kayit_label = Label(
            text="",
            size_hint_y=None,
            color=RENK_YAZI,
            halign="left",
            valign="top",
            font_size=dp(13)
        )
        self.kayit_label.bind(width=self.label_genislik_ayarla)
        self.kayit_label.bind(texture_size=self.kayit_yukseklik_ayarla)

        self.kayit_scroll.add_widget(self.kayit_label)
        kayit_kart.add_widget(self.kayit_scroll)
        ana.add_widget(kayit_kart)

        self.gorunen_indeksler = []
        self.maas_bilgisi_guncelle()
        self.kayitlari_goster()

        return ana

    def label_genislik_ayarla(self, instance, width):
        instance.text_size = (width, None)

    def kayit_yukseklik_ayarla(self, instance, texture_size):
        instance.height = texture_size[1] + dp(20)

    def input_ekle(self, form, baslik, varsayilan):
        lbl = Label(
            text=baslik,
            size_hint_y=None,
            height=dp(42),
            color=RENK_SOLUK_YAZI,
            font_size=dp(13),
            halign="left",
            valign="middle"
        )
        lbl.bind(width=self.label_genislik_ayarla)

        inp = ModernInput(
            text=str(varsayilan),
            size_hint_y=None,
            height=dp(42)
        )

        form.add_widget(lbl)
        form.add_widget(inp)

        return inp

    def spinner_ekle(self, form, baslik, varsayilan, secenekler):
        lbl = Label(
            text=baslik,
            size_hint_y=None,
            height=dp(42),
            color=RENK_SOLUK_YAZI,
            font_size=dp(13),
            halign="left",
            valign="middle"
        )
        lbl.bind(width=self.label_genislik_ayarla)

        spn = ModernSpinner(
            text=varsayilan,
            values=secenekler,
            size_hint_y=None,
            height=dp(42)
        )

        form.add_widget(lbl)
        form.add_widget(spn)

        return spn

    def maas_bilgisi_guncelle(self, *args):
        maas = sayiya_cevir(self.aylik_maas.text)
        gunluk = maas / 30 if maas > 0 else 0
        saatlik = maas / 225 if maas > 0 else 0

        self.maas_bilgi.text = (
            f"Günlük: {para_yaz(gunluk)} | Saatlik: {para_yaz(saatlik)}"
        )

    def mesaj_goster(self, baslik, mesaj):
        kutu = YuvarlakKutu(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(12),
            bg_color=RENK_KART,
            radius=20
        )

        yazi = Label(
            text=mesaj,
            color=RENK_YAZI,
            font_size=dp(15),
            halign="center",
            valign="middle"
        )
        yazi.bind(width=self.label_genislik_ayarla)

        kapat_btn = ModernButon(
            text="Tamam",
            size_hint_y=None,
            height=dp(46),
            bg_color=RENK_MAVI,
            bg_down_color=RENK_MAVI_KOYU
        )

        kutu.add_widget(yazi)
        kutu.add_widget(kapat_btn)

        popup = Popup(
            title=baslik,
            content=kutu,
            size_hint=(0.88, 0.42),
            background_color=[0.05, 0.07, 0.11, 1],
            separator_color=RENK_MAVI,
            title_color=RENK_YAZI
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
        yeni = {}

        tarih = kayit.get("tarih") or kayit.get("Tarih") or bugunun_tarihi()

        eski_gunluk = sayiya_cevir(kayit.get("gunluk_ucret", "0"))
        eski_aylik = sayiya_cevir(kayit.get("aylik_maas", "0"))

        if eski_aylik <= 0 and eski_gunluk > 0:
            eski_aylik = eski_gunluk * 30

        yeni["tarih"] = tarih
        yeni["aylik_maas"] = kayit.get("aylik_maas", f"{eski_aylik:.2f}")
        yeni["hafta_tatili_gunu"] = kayit.get("hafta_tatili_gunu", "Pazar")
        yeni["gun_turu_secim"] = kayit.get("gun_turu_secim", "Otomatik")
        yeni["calisma_durumu"] = kayit.get("calisma_durumu", "Çalıştım")
        yeni["mesai_saat"] = kayit.get("mesai_saat", "0")
        yeni["mesai_katsayi"] = kayit.get("mesai_katsayi", "1.5")
        yeni["prim"] = kayit.get("prim", "0")
        yeni["avans"] = kayit.get("avans", "0")
        yeni["kesinti"] = kayit.get("kesinti", "0")
        yeni["aciklama"] = kayit.get("aciklama", "")

        gun_turu, tatil_adi, tatil_orani = gun_turu_hesapla(
            yeni["tarih"],
            yeni["hafta_tatili_gunu"],
            yeni["gun_turu_secim"]
        )

        yeni["gun_turu"] = kayit.get("gun_turu", gun_turu)
        yeni["tatil_adi"] = kayit.get("tatil_adi", tatil_adi)

        tatil_ek, mesai_ucret, toplam_ek = self.hesapla_kayittan(yeni)

        yeni["tatil_ek_ucret"] = f"{tatil_ek:.2f}"
        yeni["mesai_ucret"] = f"{mesai_ucret:.2f}"
        yeni["toplam_ek"] = f"{toplam_ek:.2f}"

        return yeni

    def son_ayarlari_getir(self):
        kayitlar = self.kayitlari_oku()

        if not kayitlar:
            return "0", "1.5", "Pazar"

        son = kayitlar[-1]

        maas = son.get("aylik_maas", "0")
        katsayi = son.get("mesai_katsayi", "1.5")
        hafta_tatili = son.get("hafta_tatili_gunu", "Pazar")

        if str(maas).strip() == "":
            maas = "0"

        if str(katsayi).strip() == "":
            katsayi = "1.5"

        if hafta_tatili not in HAFTA_GUNLERI:
            hafta_tatili = "Pazar"

        return maas, katsayi, hafta_tatili

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
        gun_turu, tatil_adi, tatil_orani = gun_turu_hesapla(
            self.tarih.text,
            self.hafta_tatili_gunu.text,
            self.gun_turu_secim.text
        )

        kayit = {
            "tarih": self.tarih.text,
            "aylik_maas": self.aylik_maas.text,
            "hafta_tatili_gunu": self.hafta_tatili_gunu.text,
            "gun_turu_secim": self.gun_turu_secim.text,
            "gun_turu": gun_turu,
            "tatil_adi": tatil_adi,
            "calisma_durumu": self.calisma_durumu.text,
            "mesai_saat": self.mesai_saat.text,
            "mesai_katsayi": self.mesai_katsayi.text,
            "prim": self.prim.text,
            "avans": self.avans.text,
            "kesinti": self.kesinti.text,
            "aciklama": self.aciklama.text,
        }

        tatil_ek, mesai_ucret, toplam_ek = self.hesapla_kayittan(kayit)

        kayit["tatil_ek_ucret"] = f"{tatil_ek:.2f}"
        kayit["mesai_ucret"] = f"{mesai_ucret:.2f}"
        kayit["toplam_ek"] = f"{toplam_ek:.2f}"

        return kayit, tatil_ek, mesai_ucret, toplam_ek

    def hesapla_kayittan(self, kayit):
        maas = sayiya_cevir(kayit.get("aylik_maas", "0"))
        gunluk = maas / 30 if maas > 0 else 0
        saatlik = maas / 225 if maas > 0 else 0

        mesai_saat = sayiya_cevir(kayit.get("mesai_saat", "0"))
        mesai_katsayi = sayiya_cevir(kayit.get("mesai_katsayi", "1.5"))
        prim = sayiya_cevir(kayit.get("prim", "0"))
        avans = sayiya_cevir(kayit.get("avans", "0"))
        kesinti = sayiya_cevir(kayit.get("kesinti", "0"))

        gun_turu = kayit.get("gun_turu", "Normal Gün")
        calisma = kayit.get("calisma_durumu", "Çalıştım")

        tatil_ek = 0.0

        if calisma == "Çalıştım":
            if gun_turu == "Resmi Tatil":
                tatil_ek = gunluk
            elif gun_turu == "Yarım Resmi Tatil":
                tatil_ek = gunluk * 0.5
            elif gun_turu == "Hafta Tatili":
                tatil_ek = gunluk * 1.5

        mesai_ucret = mesai_saat * saatlik * mesai_katsayi
        toplam_ek = tatil_ek + mesai_ucret + prim - avans - kesinti

        return tatil_ek, mesai_ucret, toplam_ek

    def anlik_hesap_goster(self, instance=None):
        kayit, tatil_ek, mesai_ucret, toplam_ek = self.hesapla_formdan()

        maas = sayiya_cevir(kayit.get("aylik_maas", "0"))
        gunluk = maas / 30 if maas > 0 else 0
        saatlik = maas / 225 if maas > 0 else 0

        self.mesaj_goster(
            "Anlık Hesap",
            f"Gün türü: {kayit['gun_turu']}\n"
            f"Detay: {kayit['tatil_adi']}\n"
            f"Günlük: {para_yaz(gunluk)}\n"
            f"Saatlik: {para_yaz(saatlik)}\n"
            f"Tatil ek ücreti: {para_yaz(tatil_ek)}\n"
            f"Mesai ücreti: {para_yaz(mesai_ucret)}\n"
            f"Bu kaydın etkisi: {para_yaz(toplam_ek)}"
        )

    def kaydet(self, instance):
        kayit, tatil_ek, mesai_ucret, toplam_ek = self.hesapla_formdan()

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
        self.gun_turu_secim.text = "Otomatik"
        self.calisma_durumu.text = "Çalıştım"

        self.kayitlari_goster()

        self.mesaj_goster(
            "Kaydedildi",
            f"Gün türü: {kayit['gun_turu']}\n"
            f"Detay: {kayit['tatil_adi']}\n"
            f"Tatil ek: {para_yaz(tatil_ek)}\n"
            f"Mesai: {para_yaz(mesai_ucret)}\n"
            f"Bu kaydın etkisi: {para_yaz(toplam_ek)}"
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

        maas = sayiya_cevir(self.aylik_maas.text)
        gunluk = maas / 30 if maas > 0 else 0
        saatlik = maas / 225 if maas > 0 else 0

        toplam_tatil_ek = 0.0
        toplam_mesai_ucret = 0.0
        toplam_prim = 0.0
        toplam_avans = 0.0
        toplam_kesinti = 0.0
        toplam_ek = 0.0
        toplam_mesai_saat = 0.0

        satirlar = []

        for sira, (orijinal_indeks, kayit) in enumerate(gorunenler, start=1):
            tatil_ek, mesai_ucret, kayit_toplam_ek = self.hesapla_kayittan(kayit)

            mesai_saat = sayiya_cevir(kayit.get("mesai_saat", "0"))
            prim = sayiya_cevir(kayit.get("prim", "0"))
            avans = sayiya_cevir(kayit.get("avans", "0"))
            kesinti = sayiya_cevir(kayit.get("kesinti", "0"))
            aciklama = str(kayit.get("aciklama", "")).strip()

            toplam_tatil_ek += tatil_ek
            toplam_mesai_ucret += mesai_ucret
            toplam_prim += prim
            toplam_avans += avans
            toplam_kesinti += kesinti
            toplam_ek += kayit_toplam_ek
            toplam_mesai_saat += mesai_saat

            aciklama_satiri = ""
            if aciklama:
                aciklama_satiri = f"\nNot: {aciklama}"

            satirlar.append(
                f"{sira}) {kayit.get('tarih', '')} | {kayit.get('gun_turu', '')}\n"
                f"Detay: {kayit.get('tatil_adi', '')}\n"
                f"Durum: {kayit.get('calisma_durumu', '')} | Mesai: {mesai_saat:g} saat\n"
                f"Tatil ek: {para_yaz(tatil_ek)} | Mesai: {para_yaz(mesai_ucret)}\n"
                f"Prim: {para_yaz(prim)} | Avans: {para_yaz(avans)} | Kesinti: {para_yaz(kesinti)}\n"
                f"Kayıt etkisi: {para_yaz(kayit_toplam_ek)}"
                f"{aciklama_satiri}\n"
                f"------------------------------\n"
            )

        filtre = self.ay_filtre.text.strip()

        if filtre:
            baslik = f"Ay: {filtre}"
        else:
            baslik = "Tüm kayıtlar"

        tahmini_toplam = maas + toplam_ek

        self.sonuc.text = (
            f"{baslik} | Kayıt: {len(gorunenler)}\n"
            f"Aylık maaş: {para_yaz(maas)} | Günlük: {para_yaz(gunluk)} | Saatlik: {para_yaz(saatlik)}\n"
            f"Tatil ek: {para_yaz(toplam_tatil_ek)} | Mesai: {para_yaz(toplam_mesai_ucret)} | Saat: {toplam_mesai_saat:g}\n"
            f"Prim: {para_yaz(toplam_prim)} | Avans: {para_yaz(toplam_avans)} | Kesinti: {para_yaz(toplam_kesinti)}\n"
            f"TAHMİNİ TOPLAM: {para_yaz(tahmini_toplam)}"
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
            f"Tarih: {silinen.get('tarih', '')}\n"
            f"Gün türü: {silinen.get('gun_turu', '')}\n"
            f"Etki: {para_yaz(silinen.get('toplam_ek', '0'))}"
        )


if __name__ == "__main__":
    MaasTakipApp().run()
