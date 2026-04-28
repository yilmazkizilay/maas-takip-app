import os
import csv
import json
from datetime import datetime
from calendar import monthrange

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
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem


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
    "eksik_saat",
    "prim",
    "avans",
    "kesinti",
    "gunluk_ucret",
    "saatlik_ucret",
    "normal_ucret",
    "eksik_saat_kesinti",
    "tatil_ek_ucret",
    "mesai_ucret",
    "gun_toplami",
    "aciklama",
]

RENK_BG = (0.96, 0.97, 0.99, 1)
RENK_CARD = (1.00, 1.00, 1.00, 1)
RENK_INPUT = (0.94, 0.96, 0.99, 1)
RENK_TEXT = (0.10, 0.13, 0.20, 1)
RENK_MUTED = (0.40, 0.46, 0.56, 1)
RENK_BLUE = (0.16, 0.40, 0.86, 1)
RENK_GREEN = (0.10, 0.62, 0.34, 1)
RENK_RED = (0.88, 0.18, 0.22, 1)
RENK_ORANGE = (0.93, 0.50, 0.12, 1)

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

AY_ADLARI = [
    "",
    "Ocak",
    "Şubat",
    "Mart",
    "Nisan",
    "Mayıs",
    "Haziran",
    "Temmuz",
    "Ağustos",
    "Eylül",
    "Ekim",
    "Kasım",
    "Aralık",
]

GUN_TURU_SECENEKLERI = [
    "Otomatik",
    "Normal Gün",
    "Hafta Tatili",
    "Resmi Tatil",
    "Yarım Resmi Tatil",
]

CALISMA_SECENEKLERI = ["Çalıştım", "Çalışmadım"]

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
        metin = str(deger).replace(",", ".").strip()
        if metin == "":
            return 0.0
        return float(metin)
    except Exception:
        return 0.0


def sayi_yaz(deger):
    sayi = sayiya_cevir(deger)
    if sayi == int(sayi):
        return str(int(sayi))
    return f"{sayi:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def para_yaz(deger):
    return f"{sayiya_cevir(deger):,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")


def tarih_parse(tarih_metni):
    metin = str(tarih_metni).strip()
    formatlar = ["%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]
    for fmt in formatlar:
        try:
            return datetime.strptime(metin, fmt)
        except Exception:
            pass
    return None


def tarih_ay_anahtari(tarih_metni):
    tarih = tarih_parse(tarih_metni)
    if tarih:
        return tarih.strftime("%m.%Y")
    metin = str(tarih_metni).strip()
    if len(metin) >= 7:
        return metin[-7:]
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

    hafta_index = HAFTA_GUNLERI.get(hafta_tatili_gunu, 6)
    if tarih.weekday() == hafta_index:
        return "Hafta Tatili", hafta_tatili_gunu, 0.0

    return "Normal Gün", HAFTA_GUN_ADLARI[tarih.weekday()], 0.0


class Card(BoxLayout):
    bg_color = ListProperty(RENK_CARD)
    radius = NumericProperty(18)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._color = Color(rgba=self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
        self.bind(pos=self._update_rect, size=self._update_rect, bg_color=self._update_color, radius=self._update_rect)

    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._rect.radius = [self.radius]

    def _update_color(self, *args):
        self._color.rgba = self.bg_color


class RoundButton(Button):
    bg_color = ListProperty(RENK_BLUE)
    down_color = ListProperty((0.10, 0.26, 0.65, 1))
    radius = NumericProperty(16)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.font_size = dp(13)
        with self.canvas.before:
            self._color = Color(rgba=self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
        self.bind(pos=self._update_rect, size=self._update_rect, state=self._update_state, bg_color=self._update_state)

    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._rect.radius = [self.radius]

    def _update_state(self, *args):
        self._color.rgba = self.down_color if self.state == "down" else self.bg_color


class ModernInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline = False
        self.size_hint_y = None
        self.height = dp(40)
        self.background_normal = ""
        self.background_active = ""
        self.background_color = RENK_INPUT
        self.foreground_color = RENK_TEXT
        self.cursor_color = RENK_BLUE
        self.hint_text_color = RENK_MUTED
        self.font_size = dp(14)
        self.padding = [dp(10), dp(8), dp(10), dp(8)]


class ModernSpinner(Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(40)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = RENK_INPUT
        self.color = RENK_TEXT
        self.font_size = dp(13)


class MaasTakipApp(App):
    def build(self):
        self.title = "Maaş Takip"
        Window.clearcolor = RENK_BG
        Window.softinput_mode = "below_target"

        self.dosya_yolu = os.path.join(self.user_data_dir, "maas_kayitlari.csv")
        self.ayarlar_yolu = os.path.join(self.user_data_dir, "ayarlar.json")
        self.ayarlar = self.ayarlari_oku()
        self.gorunen_indeksler = []

        self.dosyayi_hazirla_ve_duzelt()

        root = TabbedPanel(do_default_tab=False)
        root.background_color = RENK_BG
        root.tab_width = dp(92)

        self.tab_ekle = TabbedPanelItem(text="Kayıt")
        self.tab_kayitlar = TabbedPanelItem(text="Liste")
        self.tab_ozet = TabbedPanelItem(text="Özet")
        self.tab_ayarlar = TabbedPanelItem(text="Ayarlar")

        root.add_widget(self.tab_ekle)
        root.add_widget(self.tab_kayitlar)
        root.add_widget(self.tab_ozet)
        root.add_widget(self.tab_ayarlar)

        self.tab_ekle.content = self.ekran_kayit_ekle()
        self.tab_kayitlar.content = self.ekran_kayitlar()
        self.tab_ozet.content = self.ekran_ozet()
        self.tab_ayarlar.content = self.ekran_ayarlar()

        root.switch_to(self.tab_ekle)

        self.ayar_bilgisi_guncelle()
        self.kayit_onizleme_guncelle()
        self.kayitlari_listele()
        self.ozet_goster()

        return root

    def panel(self):
        return BoxLayout(orientation="vertical", padding=[dp(10), dp(8), dp(10), dp(10)], spacing=dp(8))

    def card(self, height=None):
        kart = Card(orientation="vertical", bg_color=RENK_CARD, radius=18, padding=dp(10), spacing=dp(7))
        if height is not None:
            kart.size_hint_y = None
            kart.height = dp(height)
        return kart

    def baslik(self, metin, alt=""):
        kutu = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(58), spacing=dp(0))

        lbl = Label(text=metin, color=RENK_TEXT, font_size=dp(21), bold=True, halign="left", valign="middle")
        lbl.bind(size=self.label_size)
        kutu.add_widget(lbl)

        if alt:
            alt_lbl = Label(text=alt, color=RENK_MUTED, font_size=dp(12), halign="left", valign="middle")
            alt_lbl.bind(size=self.label_size)
            kutu.add_widget(alt_lbl)

        return kutu

    def label_size(self, instance, size):
        instance.text_size = (instance.width, None)

    def label_height(self, instance, texture_size):
        instance.height = texture_size[1] + dp(20)

    def label(self, text, size=14, bold=False, muted=False, height=None):
        lbl = Label(text=text, color=RENK_MUTED if muted else RENK_TEXT, font_size=dp(size), bold=bold, halign="left", valign="top")
        lbl.bind(size=self.label_size)
        if height is not None:
            lbl.size_hint_y = None
            lbl.height = dp(height)
        return lbl

    def input(self, text="", hint=""):
        return ModernInput(text=str(text), hint_text=hint)

    def spinner(self, text, values):
        return ModernSpinner(text=text, values=values)

    def koyu_renk(self, color):
        return (max(color[0] - 0.10, 0), max(color[1] - 0.12, 0), max(color[2] - 0.12, 0), 1)

    def button(self, text, color=RENK_BLUE, width=None):
        btn = RoundButton(text=text, size_hint_y=None, height=dp(42), bg_color=color, down_color=self.koyu_renk(color), radius=18)
        if width is not None:
            btn.size_hint_x = None
            btn.width = dp(width)
        return btn

    def kucuk_button(self, text, color=RENK_BLUE, width=76):
        return self.button(text, color=color, width=width)

    def row_label(self, text):
        lbl = Label(text=text, color=RENK_MUTED, font_size=dp(12), size_hint_y=None, height=dp(40), halign="left", valign="middle")
        lbl.bind(size=self.label_size)
        return lbl

    def add_row(self, grid, text, widget):
        grid.add_widget(self.row_label(text))
        grid.add_widget(widget)

    def mesaj_goster(self, baslik, mesaj):
        kutu = Card(orientation="vertical", padding=dp(14), spacing=dp(12), bg_color=RENK_CARD, radius=18)
        yazi = Label(text=mesaj, halign="center", valign="middle", color=RENK_TEXT, font_size=dp(14))
        yazi.bind(size=self.label_size)
        btn = self.button("Tamam", RENK_BLUE)
        kutu.add_widget(yazi)
        kutu.add_widget(btn)

        popup = Popup(
            title=baslik,
            content=kutu,
            size_hint=(0.86, 0.38),
            background_color=RENK_CARD,
            title_color=RENK_TEXT,
            separator_color=RENK_BLUE,
        )
        btn.bind(on_press=popup.dismiss)
        popup.open()

    def takvim_ac(self, hedef_input):
        secili = tarih_parse(hedef_input.text) or datetime.now()
        self.takvim_hedef_input = hedef_input
        self.takvim_yil = secili.year
        self.takvim_ay = secili.month

        self.takvim_kutu = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        self.takvim_popup = Popup(
            title="Tarih Seç",
            content=self.takvim_kutu,
            size_hint=(0.94, 0.72),
            background_color=RENK_CARD,
            title_color=RENK_TEXT,
            separator_color=RENK_BLUE,
        )
        self.takvim_ciz()
        self.takvim_popup.open()

    def takvim_ciz(self):
        self.takvim_kutu.clear_widgets()

        ust = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(42), spacing=dp(6))
        onceki = self.kucuk_button("<", RENK_BLUE, width=48)
        sonraki = self.kucuk_button(">", RENK_BLUE, width=48)
        baslik = Label(text=f"{AY_ADLARI[self.takvim_ay]} {self.takvim_yil}", color=RENK_TEXT, bold=True, font_size=dp(17))

        onceki.bind(on_press=lambda x: self.takvim_ay_degistir(-1))
        sonraki.bind(on_press=lambda x: self.takvim_ay_degistir(1))

        ust.add_widget(onceki)
        ust.add_widget(baslik)
        ust.add_widget(sonraki)
        self.takvim_kutu.add_widget(ust)

        grid = GridLayout(cols=7, spacing=dp(4))

        for gun in ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]:
            grid.add_widget(Label(text=gun, color=RENK_MUTED, bold=True, size_hint_y=None, height=dp(28), font_size=dp(12)))

        ilk_gun_index, ay_gun_sayisi = monthrange(self.takvim_yil, self.takvim_ay)

        for _ in range(ilk_gun_index):
            grid.add_widget(Label(text=""))

        for gun in range(1, ay_gun_sayisi + 1):
            btn = Button(text=str(gun), background_normal="", background_color=RENK_INPUT, color=RENK_TEXT, bold=True, font_size=dp(13))
            btn.bind(on_press=lambda x, g=gun: self.takvim_tarih_sec(g))
            grid.add_widget(btn)

        self.takvim_kutu.add_widget(grid)

    def takvim_ay_degistir(self, yon):
        self.takvim_ay += yon
        if self.takvim_ay < 1:
            self.takvim_ay = 12
            self.takvim_yil -= 1
        if self.takvim_ay > 12:
            self.takvim_ay = 1
            self.takvim_yil += 1
        self.takvim_ciz()

    def takvim_tarih_sec(self, gun):
        self.takvim_hedef_input.text = f"{gun:02d}.{self.takvim_ay:02d}.{self.takvim_yil}"
        self.takvim_popup.dismiss()
        self.kayit_onizleme_guncelle()

    def ekran_kayit_ekle(self):
        ana = self.panel()
        ana.add_widget(self.baslik("Kayıt Ekle", "Maaş ayarı varsa gün parası, eksik saat, mesai ve ekler hesaplanır."))

        kart = self.card()
        scroll = ScrollView()
        grid = GridLayout(cols=2, spacing=dp(6), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        tarih_kutu = BoxLayout(orientation="horizontal", spacing=dp(6), size_hint_y=None, height=dp(40))
        self.kayit_tarih = self.input(bugunun_tarihi(), "27.04.2026")
        takvim_btn = self.kucuk_button("Tarih", RENK_ORANGE, width=62)
        takvim_btn.bind(on_press=lambda x: self.takvim_ac(self.kayit_tarih))
        tarih_kutu.add_widget(self.kayit_tarih)
        tarih_kutu.add_widget(takvim_btn)

        self.kayit_gun_turu = self.spinner("Otomatik", GUN_TURU_SECENEKLERI)
        self.kayit_calisma = self.spinner("Çalıştım", CALISMA_SECENEKLERI)
        self.kayit_eksik_saat = self.input("0", "Örn: 2")
        self.kayit_mesai = self.input("0", "Örn: 2")
        self.kayit_prim = self.input("0", "Örn: 500")
        self.kayit_avans = self.input("0", "Örn: 1000")
        self.kayit_kesinti = self.input("0", "Örn: 250")
        self.kayit_aciklama = self.input("", "Örn: Eksik çalışma / bayram mesaisi")

        self.add_row(grid, "Tarih", tarih_kutu)
        self.add_row(grid, "Gün türü", self.kayit_gun_turu)
        self.add_row(grid, "Durum", self.kayit_calisma)
        self.add_row(grid, "Eksik saat", self.kayit_eksik_saat)
        self.add_row(grid, "Ek mesai saati", self.kayit_mesai)
        self.add_row(grid, "Prim", self.kayit_prim)
        self.add_row(grid, "Avans", self.kayit_avans)
        self.add_row(grid, "Kesinti", self.kayit_kesinti)
        self.add_row(grid, "Açıklama", self.kayit_aciklama)

        scroll.add_widget(grid)
        kart.add_widget(scroll)

        self.kayit_onizleme = self.label("", size=12, muted=True, height=126)
        kart.add_widget(self.kayit_onizleme)

        btns = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44), spacing=dp(8))
        hesap = self.button("Hesapla", RENK_BLUE)
        kaydet = self.button("Kaydet", RENK_GREEN)
        hesap.bind(on_press=lambda x: self.kayit_onizleme_guncelle())
        kaydet.bind(on_press=self.kaydet)
        btns.add_widget(hesap)
        btns.add_widget(kaydet)
        kart.add_widget(btns)

        ana.add_widget(kart)

        self.kayit_tarih.bind(text=lambda *args: self.kayit_onizleme_guncelle())
        self.kayit_mesai.bind(text=lambda *args: self.kayit_onizleme_guncelle())
        self.kayit_eksik_saat.bind(text=lambda *args: self.kayit_onizleme_guncelle())
        self.kayit_prim.bind(text=lambda *args: self.kayit_onizleme_guncelle())
        self.kayit_avans.bind(text=lambda *args: self.kayit_onizleme_guncelle())
        self.kayit_kesinti.bind(text=lambda *args: self.kayit_onizleme_guncelle())
        self.kayit_gun_turu.bind(text=lambda *args: self.kayit_onizleme_guncelle())
        self.kayit_calisma.bind(text=lambda *args: self.kayit_onizleme_guncelle())

        return ana

    def ekran_kayitlar(self):
        ana = self.panel()
        ana.add_widget(self.baslik("Kayıtlar", "Kayıtlar gün gün görünür. Ay filtresi ve silme işlemi burada."))

        filtre = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(42), spacing=dp(7))
        self.kayitlar_ay = self.input(bu_ay(), "Ay: 04.2026")
        ay_btn = self.kucuk_button("Ay", RENK_ORANGE, width=62)
        tum_btn = self.kucuk_button("Tümü", RENK_BLUE, width=70)
        ay_btn.bind(on_press=lambda x: self.kayitlari_listele())
        tum_btn.bind(on_press=self.kayitlar_tumunu_goster)
        filtre.add_widget(self.kayitlar_ay)
        filtre.add_widget(ay_btn)
        filtre.add_widget(tum_btn)
        ana.add_widget(filtre)

        sil = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(42), spacing=dp(7))
        self.silinecek_no = self.input("", "Silinecek no")
        self.silinecek_no.input_filter = "int"
        sil_btn = self.button("Kaydı Sil", RENK_RED, width=112)
        sil_btn.bind(on_press=self.kaydi_sil)
        sil.add_widget(self.silinecek_no)
        sil.add_widget(sil_btn)
        ana.add_widget(sil)

        kart = self.card()
        self.kayitlar_ozet = self.label("", size=12, muted=True, height=104)
        kart.add_widget(self.kayitlar_ozet)

        scroll = ScrollView()
        self.kayit_label = self.label("", size=12)
        self.kayit_label.size_hint_y = None
        self.kayit_label.bind(texture_size=self.label_height)
        scroll.add_widget(self.kayit_label)
        kart.add_widget(scroll)

        ana.add_widget(kart)
        return ana

    def ekran_ozet(self):
        ana = self.panel()
        ana.add_widget(self.baslik("Aylık Özet", "Gün parası, eksik saat kesintisi, tatil, mesai ve toplamlar."))

        filtre = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(42), spacing=dp(7))
        self.ozet_ay = self.input(bu_ay(), "Ay: 04.2026")
        goster = self.button("Özeti Göster", RENK_ORANGE, width=130)
        goster.bind(on_press=lambda x: self.ozet_goster())
        filtre.add_widget(self.ozet_ay)
        filtre.add_widget(goster)
        ana.add_widget(filtre)

        kart = self.card()
        self.ozet_label = self.label("", size=14)
        kart.add_widget(self.ozet_label)
        ana.add_widget(kart)
        return ana

    def ekran_ayarlar(self):
        ana = self.panel()
        ana.add_widget(self.baslik("Ayarlar", "Maaş bilgisi girilmeden kayıt alınmaz."))

        kart = self.card(height=295)
        grid = GridLayout(cols=2, spacing=dp(6), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        self.ayar_maas = self.input(self.ayarlar.get("aylik_maas", "0"), "Örn: 35000")
        self.ayar_saat = self.input(self.ayarlar.get("gunluk_calisma_saati", "7.5"), "Örn: 7.5")
        self.ayar_katsayi = self.input(self.ayarlar.get("mesai_katsayi", "1.5"), "Örn: 1.5")
        self.ayar_tatil = self.spinner(self.ayarlar.get("hafta_tatili_gunu", "Pazar"), list(HAFTA_GUNLERI.keys()))

        self.add_row(grid, "Aylık maaş", self.ayar_maas)
        self.add_row(grid, "Günlük saat", self.ayar_saat)
        self.add_row(grid, "Mesai katsayısı", self.ayar_katsayi)
        self.add_row(grid, "Hafta tatili", self.ayar_tatil)

        kart.add_widget(grid)

        self.ayar_bilgi = self.label("", size=12, muted=True, height=76)
        kart.add_widget(self.ayar_bilgi)

        btns = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44), spacing=dp(8))
        kaydet = self.button("Ayarları Kaydet", RENK_GREEN)
        hesap = self.button("Hesabı Göster", RENK_BLUE)
        kaydet.bind(on_press=self.ayarlari_kaydet)
        hesap.bind(on_press=lambda x: self.ayar_bilgisi_guncelle())
        btns.add_widget(kaydet)
        btns.add_widget(hesap)
        kart.add_widget(btns)

        ana.add_widget(kart)

        self.ayar_maas.bind(text=lambda *args: self.ayar_bilgisi_guncelle())
        self.ayar_saat.bind(text=lambda *args: self.ayar_bilgisi_guncelle())

        return ana

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
        if str(ayarlar.get("aylik_maas", "")).strip() == "":
            ayarlar["aylik_maas"] = "0"
        if str(ayarlar.get("mesai_katsayi", "")).strip() == "":
            ayarlar["mesai_katsayi"] = "1.5"
        if str(ayarlar.get("gunluk_calisma_saati", "")).strip() == "":
            ayarlar["gunluk_calisma_saati"] = "7.5"
        return ayarlar

    def ayarlari_yaz(self):
        with open(self.ayarlar_yolu, "w", encoding="utf-8") as f:
            json.dump(self.ayarlar, f, ensure_ascii=False, indent=2)

    def ayar_bilgisi_guncelle(self):
        if not hasattr(self, "ayar_maas"):
            return

        maas = sayiya_cevir(self.ayar_maas.text)
        gunluk_saat = sayiya_cevir(self.ayar_saat.text)
        gunluk = maas / 30 if maas > 0 else 0.0
        saatlik = gunluk / gunluk_saat if gunluk > 0 and gunluk_saat > 0 else 0.0
        aylik_saat = gunluk_saat * 30 if gunluk_saat > 0 else 0.0

        self.ayar_bilgi.text = (
            f"Aylık maaş: {para_yaz(maas)}\n"
            f"Günlük ücret: {para_yaz(gunluk)}\n"
            f"Saatlik ücret: {para_yaz(saatlik)} | Aylık saat: {sayi_yaz(aylik_saat)}"
        )

    def ayarlari_kaydet(self, instance=None):
        self.ayarlar["aylik_maas"] = self.ayar_maas.text.strip() or "0"
        self.ayarlar["gunluk_calisma_saati"] = self.ayar_saat.text.strip() or "7.5"
        self.ayarlar["mesai_katsayi"] = self.ayar_katsayi.text.strip() or "1.5"

        if self.ayar_tatil.text in HAFTA_GUNLERI:
            self.ayarlar["hafta_tatili_gunu"] = self.ayar_tatil.text
        else:
            self.ayarlar["hafta_tatili_gunu"] = "Pazar"

        self.ayarlari_yaz()
        self.ayar_bilgisi_guncelle()
        self.kayit_onizleme_guncelle()
        self.kayitlari_listele()
        self.ozet_goster()
        self.mesaj_goster("Kaydedildi", "Ayarlar kaydedildi. Artık kayıt alabilirsin.")

    def gunluk_ucret(self, maas=None):
        if maas is None:
            maas = self.ayarlar.get("aylik_maas", "0")
        maas = sayiya_cevir(maas)
        return maas / 30 if maas > 0 else 0.0

    def saatlik_ucret(self, maas=None, gunluk_saat=None):
        if maas is None:
            maas = self.ayarlar.get("aylik_maas", "0")
        if gunluk_saat is None:
            gunluk_saat = self.ayarlar.get("gunluk_calisma_saati", "7.5")
        gunluk = self.gunluk_ucret(maas)
        saat = sayiya_cevir(gunluk_saat)
        return gunluk / saat if gunluk > 0 and saat > 0 else 0.0

    def dosyayi_hazirla_ve_duzelt(self):
        if not os.path.exists(self.dosya_yolu):
            self.kayitlari_yaz([])
            return

        try:
            with open(self.dosya_yolu, "r", newline="", encoding="utf-8") as f:
                eski = list(csv.DictReader(f))
        except Exception:
            eski = []

        duzeltilmis = []
        for kayit in eski:
            if kayit:
                duzeltilmis.append(self.kaydi_duzelt(kayit))
        self.kayitlari_yaz(duzeltilmis)

    def kaydi_duzelt(self, kayit):
        eski_gunluk = sayiya_cevir(kayit.get("gunluk_ucret", "0"))
        eski_aylik = sayiya_cevir(kayit.get("aylik_maas_snapshot", kayit.get("aylik_maas", "0")))

        if eski_aylik <= 0 and eski_gunluk > 0:
            eski_aylik = eski_gunluk * 30
        if eski_aylik <= 0:
            eski_aylik = sayiya_cevir(self.ayarlar.get("aylik_maas", "0"))

        tarih = kayit.get("tarih") or kayit.get("Tarih") or bugunun_tarihi()
        hafta_tatili = kayit.get(
            "hafta_tatili_gunu_snapshot",
            kayit.get("hafta_tatili_gunu", self.ayarlar.get("hafta_tatili_gunu", "Pazar")),
        )
        if hafta_tatili not in HAFTA_GUNLERI:
            hafta_tatili = "Pazar"

        gun_turu_secim = kayit.get("gun_turu_secim", "Otomatik")
        if gun_turu_secim not in GUN_TURU_SECENEKLERI:
            gun_turu_secim = "Otomatik"

        gun_turu, tatil_adi, oran = gun_turu_hesapla(tarih, hafta_tatili, gun_turu_secim)

        yeni = {
            "tarih": tarih,
            "aylik_maas_snapshot": kayit.get("aylik_maas_snapshot", f"{eski_aylik:.2f}"),
            "gunluk_calisma_saati_snapshot": kayit.get("gunluk_calisma_saati_snapshot", self.ayarlar.get("gunluk_calisma_saati", "7.5")),
            "hafta_tatili_gunu_snapshot": hafta_tatili,
            "mesai_katsayi_snapshot": kayit.get("mesai_katsayi_snapshot", kayit.get("mesai_katsayi", self.ayarlar.get("mesai_katsayi", "1.5"))),
            "gun_turu_secim": gun_turu_secim,
            "gun_turu": gun_turu,
            "tatil_adi": tatil_adi,
            "calisma_durumu": kayit.get("calisma_durumu", "Çalıştım"),
            "mesai_saat": kayit.get("mesai_saat", "0"),
            "eksik_saat": kayit.get("eksik_saat", "0"),
            "prim": kayit.get("prim", "0"),
            "avans": kayit.get("avans", "0"),
            "kesinti": kayit.get("kesinti", "0"),
            "aciklama": kayit.get("aciklama", ""),
        }

        gunluk, saatlik, normal_ucret, eksik_kesinti, tatil_ek, mesai_ucret, gun_toplami = self.hesapla_kayittan(yeni)

        yeni["gunluk_ucret"] = f"{gunluk:.2f}"
        yeni["saatlik_ucret"] = f"{saatlik:.2f}"
        yeni["normal_ucret"] = f"{normal_ucret:.2f}"
        yeni["eksik_saat_kesinti"] = f"{eksik_kesinti:.2f}"
        yeni["tatil_ek_ucret"] = f"{tatil_ek:.2f}"
        yeni["mesai_ucret"] = f"{mesai_ucret:.2f}"
        yeni["gun_toplami"] = f"{gun_toplami:.2f}"
        return yeni

    def kayitlari_oku(self):
        if not os.path.exists(self.dosya_yolu):
            return []
        try:
            with open(self.dosya_yolu, "r", newline="", encoding="utf-8") as f:
                okuyucu = csv.DictReader(f)
                return [self.kaydi_duzelt(kayit) for kayit in okuyucu if kayit]
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
        maas = self.ayarlar.get("aylik_maas", "0")
        saat = self.ayarlar.get("gunluk_calisma_saati", "7.5")
        hafta = self.ayarlar.get("hafta_tatili_gunu", "Pazar")
        katsayi = self.ayarlar.get("mesai_katsayi", "1.5")

        gun_turu, tatil_adi, oran = gun_turu_hesapla(self.kayit_tarih.text, hafta, self.kayit_gun_turu.text)

        kayit = {
            "tarih": self.kayit_tarih.text.strip() or bugunun_tarihi(),
            "aylik_maas_snapshot": maas,
            "gunluk_calisma_saati_snapshot": saat,
            "hafta_tatili_gunu_snapshot": hafta,
            "mesai_katsayi_snapshot": katsayi,
            "gun_turu_secim": self.kayit_gun_turu.text,
            "gun_turu": gun_turu,
            "tatil_adi": tatil_adi,
            "calisma_durumu": self.kayit_calisma.text,
            "mesai_saat": self.kayit_mesai.text,
            "eksik_saat": self.kayit_eksik_saat.text,
            "prim": self.kayit_prim.text,
            "avans": self.kayit_avans.text,
            "kesinti": self.kayit_kesinti.text,
            "aciklama": self.kayit_aciklama.text,
        }

        gunluk, saatlik, normal_ucret, eksik_kesinti, tatil_ek, mesai_ucret, gun_toplami = self.hesapla_kayittan(kayit)

        kayit["gunluk_ucret"] = f"{gunluk:.2f}"
        kayit["saatlik_ucret"] = f"{saatlik:.2f}"
        kayit["normal_ucret"] = f"{normal_ucret:.2f}"
        kayit["eksik_saat_kesinti"] = f"{eksik_kesinti:.2f}"
        kayit["tatil_ek_ucret"] = f"{tatil_ek:.2f}"
        kayit["mesai_ucret"] = f"{mesai_ucret:.2f}"
        kayit["gun_toplami"] = f"{gun_toplami:.2f}"

        return kayit, gunluk, saatlik, normal_ucret, eksik_kesinti, tatil_ek, mesai_ucret, gun_toplami

    def hesapla_kayittan(self, kayit):
        maas = sayiya_cevir(kayit.get("aylik_maas_snapshot", self.ayarlar.get("aylik_maas", "0")))
        gunluk_saat = sayiya_cevir(kayit.get("gunluk_calisma_saati_snapshot", self.ayarlar.get("gunluk_calisma_saati", "7.5")))
        katsayi = sayiya_cevir(kayit.get("mesai_katsayi_snapshot", self.ayarlar.get("mesai_katsayi", "1.5")))

        gunluk = maas / 30 if maas > 0 else 0.0
        saatlik = gunluk / gunluk_saat if gunluk > 0 and gunluk_saat > 0 else 0.0

        mesai_saat = sayiya_cevir(kayit.get("mesai_saat", "0"))
        eksik_saat = sayiya_cevir(kayit.get("eksik_saat", "0"))
        prim = sayiya_cevir(kayit.get("prim", "0"))
        avans = sayiya_cevir(kayit.get("avans", "0"))
        kesinti = sayiya_cevir(kayit.get("kesinti", "0"))

        gun_turu = kayit.get("gun_turu", "Normal Gün")
        calisma = kayit.get("calisma_durumu", "Çalıştım")

        normal_ucret = 0.0
        tatil_ek = 0.0

        if calisma == "Çalıştım":
            normal_ucret = gunluk
            if gun_turu == "Resmi Tatil":
                tatil_ek = gunluk
            elif gun_turu == "Yarım Resmi Tatil":
                tatil_ek = gunluk * 0.5
            elif gun_turu == "Hafta Tatili":
                tatil_ek = gunluk * 1.5
        else:
            if gun_turu == "Resmi Tatil":
                normal_ucret = gunluk
            elif gun_turu == "Yarım Resmi Tatil":
                normal_ucret = gunluk * 0.5
            elif gun_turu == "Hafta Tatili":
                normal_ucret = gunluk
            else:
                normal_ucret = 0.0

        eksik_kesinti = eksik_saat * saatlik
        if eksik_kesinti > normal_ucret:
            eksik_kesinti = normal_ucret

        mesai_ucret = mesai_saat * saatlik * katsayi
        gun_toplami = normal_ucret - eksik_kesinti + tatil_ek + mesai_ucret + prim - avans - kesinti

        return gunluk, saatlik, normal_ucret, eksik_kesinti, tatil_ek, mesai_ucret, gun_toplami

    def kayit_onizleme_guncelle(self):
        if not hasattr(self, "kayit_tarih"):
            return

        kayit, gunluk, saatlik, normal_ucret, eksik_kesinti, tatil_ek, mesai_ucret, gun_toplami = self.hesapla_formdan()

        maas = sayiya_cevir(self.ayarlar.get("aylik_maas", "0"))
        if maas <= 0:
            self.kayit_onizleme.text = "Önce Ayarlar sekmesinden aylık maaşını gir. Maaş olmadan kayıt alınmaz."
            return

        self.kayit_onizleme.text = (
            f"Gün türü: {kayit.get('gun_turu', '')} | {kayit.get('tatil_adi', '')}\n"
            f"Günlük: {para_yaz(gunluk)} | Saatlik: {para_yaz(saatlik)}\n"
            f"Gün parası: {para_yaz(normal_ucret)} | Eksik saat kesintisi: -{para_yaz(eksik_kesinti)}\n"
            f"Tatil ek: {para_yaz(tatil_ek)} | Mesai: {para_yaz(mesai_ucret)}\n"
            f"Bu günün toplamı: {para_yaz(gun_toplami)}"
        )

    def kaydet(self, instance=None):
        if sayiya_cevir(self.ayarlar.get("aylik_maas", "0")) <= 0:
            self.mesaj_goster("Maaş eksik", "Önce Ayarlar sekmesinden aylık maaşını yazıp kaydetmelisin.")
            return

        kayit, gunluk, saatlik, normal_ucret, eksik_kesinti, tatil_ek, mesai_ucret, gun_toplami = self.hesapla_formdan()

        kayitlar = self.kayitlari_oku()
        kayitlar.append(kayit)
        self.kayitlari_yaz(kayitlar)

        self.kayit_mesai.text = "0"
        self.kayit_eksik_saat.text = "0"
        self.kayit_prim.text = "0"
        self.kayit_avans.text = "0"
        self.kayit_kesinti.text = "0"
        self.kayit_aciklama.text = ""
        self.kayit_tarih.text = bugunun_tarihi()
        self.kayit_gun_turu.text = "Otomatik"
        self.kayit_calisma.text = "Çalıştım"

        self.kayit_onizleme_guncelle()
        self.kayitlari_listele()
        self.ozet_goster()

        self.mesaj_goster(
            "Kaydedildi",
            f"Gün parası: {para_yaz(normal_ucret)}\n"
            f"Eksik saat kesintisi: -{para_yaz(eksik_kesinti)}\n"
            f"Tatil ek: {para_yaz(tatil_ek)}\n"
            f"Mesai: {para_yaz(mesai_ucret)}\n"
            f"Bu günün toplamı: {para_yaz(gun_toplami)}",
        )

    def filtreye_uyuyor_mu(self, kayit, filtre):
        filtre = str(filtre).strip()
        if filtre == "":
            return True
        ay = tarih_ay_anahtari(kayit.get("tarih", ""))
        if filtre == ay:
            return True
        if filtre in str(kayit.get("tarih", "")):
            return True
        return False

    def kayitlari_filtrele(self, filtre):
        tum = self.kayitlari_oku()
        sonuc = []
        for i, kayit in enumerate(tum):
            if self.filtreye_uyuyor_mu(kayit, filtre):
                sonuc.append((i, kayit))
        return sonuc

    def toplamlar(self, kayit_ciftleri):
        sonuc = {
            "gunluk_toplam": 0.0,
            "normal": 0.0,
            "eksik": 0.0,
            "tatil_ek": 0.0,
            "mesai": 0.0,
            "prim": 0.0,
            "avans": 0.0,
            "kesinti": 0.0,
            "mesai_saat": 0.0,
            "eksik_saat": 0.0,
        }

        for indeks, kayit in kayit_ciftleri:
            gunluk, saatlik, normal_ucret, eksik_kesinti, tatil_ek, mesai_ucret, gun_toplami = self.hesapla_kayittan(kayit)
            sonuc["gunluk_toplam"] += gun_toplami
            sonuc["normal"] += normal_ucret
            sonuc["eksik"] += eksik_kesinti
            sonuc["tatil_ek"] += tatil_ek
            sonuc["mesai"] += mesai_ucret
            sonuc["prim"] += sayiya_cevir(kayit.get("prim", "0"))
            sonuc["avans"] += sayiya_cevir(kayit.get("avans", "0"))
            sonuc["kesinti"] += sayiya_cevir(kayit.get("kesinti", "0"))
            sonuc["mesai_saat"] += sayiya_cevir(kayit.get("mesai_saat", "0"))
            sonuc["eksik_saat"] += sayiya_cevir(kayit.get("eksik_saat", "0"))

        return sonuc

    def kayitlari_listele(self):
        if not hasattr(self, "kayitlar_ay"):
            return

        filtre = self.kayitlar_ay.text.strip()
        ciftler = self.kayitlari_filtrele(filtre)
        ciftler_ters = list(reversed(ciftler))
        self.gorunen_indeksler = [i for i, kayit in ciftler_ters]
        top = self.toplamlar(ciftler)

        baslik = f"Ay: {filtre}" if filtre else "Tüm kayıtlar"

        self.kayitlar_ozet.text = (
            f"{baslik} | Kayıt: {len(ciftler)}\n"
            f"Gün parası: {para_yaz(top['normal'])} | Eksik saat: {sayi_yaz(top['eksik_saat'])} saat = -{para_yaz(top['eksik'])}\n"
            f"Tatil ek: {para_yaz(top['tatil_ek'])} | Mesai: {para_yaz(top['mesai'])} | Saat: {sayi_yaz(top['mesai_saat'])}\n"
            f"Prim: {para_yaz(top['prim'])} | Avans: {para_yaz(top['avans'])} | Kesinti: {para_yaz(top['kesinti'])}\n"
            f"Kaydedilen toplam: {para_yaz(top['gunluk_toplam'])}"
        )

        satirlar = []
        for sira, (orijinal_indeks, kayit) in enumerate(ciftler_ters, start=1):
            gunluk, saatlik, normal_ucret, eksik_kesinti, tatil_ek, mesai_ucret, gun_toplami = self.hesapla_kayittan(kayit)
            aciklama = str(kayit.get("aciklama", "")).strip()
            not_satiri = f"\nNot: {aciklama}" if aciklama else ""

            satirlar.append(
                f"{sira}) {kayit.get('tarih', '')} | {kayit.get('gun_turu', '')}\n"
                f"Detay: {kayit.get('tatil_adi', '')}\n"
                f"Durum: {kayit.get('calisma_durumu', '')} | Günlük: {para_yaz(gunluk)} | Saatlik: {para_yaz(saatlik)}\n"
                f"Gün parası: {para_yaz(normal_ucret)} | Eksik: {sayi_yaz(kayit.get('eksik_saat', '0'))} saat = -{para_yaz(eksik_kesinti)}\n"
                f"Tatil ek: {para_yaz(tatil_ek)} | Mesai: {sayi_yaz(kayit.get('mesai_saat', '0'))} saat = {para_yaz(mesai_ucret)}\n"
                f"Prim: {para_yaz(kayit.get('prim', '0'))} | Avans: {para_yaz(kayit.get('avans', '0'))} | Kesinti: {para_yaz(kayit.get('kesinti', '0'))}\n"
                f"Gün toplamı: {para_yaz(gun_toplami)}{not_satiri}\n"
                f"------------------------------\n"
            )

        self.kayit_label.text = "\n".join(satirlar) if satirlar else "Bu filtrede kayıt yok."

    def kayitlar_tumunu_goster(self, instance=None):
        self.kayitlar_ay.text = ""
        self.kayitlari_listele()

    def ozet_goster(self):
        if not hasattr(self, "ozet_ay"):
            return

        filtre = self.ozet_ay.text.strip()
        ciftler = self.kayitlari_filtrele(filtre)
        top = self.toplamlar(ciftler)
        baslik = f"{filtre} Maaş Özeti" if filtre else "Genel Maaş Özeti"

        self.ozet_label.text = (
            f"{baslik}\n\n"
            f"Aylık maaş ayarı: {para_yaz(self.ayarlar.get('aylik_maas', '0'))}\n"
            f"Günlük ücret: {para_yaz(self.gunluk_ucret())}\n"
            f"Saatlik ücret: {para_yaz(self.saatlik_ucret())}\n\n"
            f"Kayıt sayısı: {len(ciftler)}\n"
            f"Toplam eksik saat: {sayi_yaz(top['eksik_saat'])} saat\n"
            f"Toplam mesai saati: {sayi_yaz(top['mesai_saat'])} saat\n\n"
            f"Kaydedilen gün parası: {para_yaz(top['normal'])}\n"
            f"Eksik saat kesintisi: -{para_yaz(top['eksik'])}\n"
            f"Tatil / hafta tatili ek ücreti: {para_yaz(top['tatil_ek'])}\n"
            f"Fazla mesai ücreti: {para_yaz(top['mesai'])}\n"
            f"Prim: {para_yaz(top['prim'])}\n"
            f"Avans: -{para_yaz(top['avans'])}\n"
            f"Kesinti: -{para_yaz(top['kesinti'])}\n\n"
            f"KAYDEDİLEN TOPLAM: {para_yaz(top['gunluk_toplam'])}"
        )

    def kaydi_sil(self, instance=None):
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

        tum = self.kayitlari_oku()
        silinecek = self.gorunen_indeksler[no - 1]

        if silinecek < 0 or silinecek >= len(tum):
            self.mesaj_goster("Hata", "Kayıt bulunamadı.")
            return

        silinen = tum.pop(silinecek)
        self.kayitlari_yaz(tum)
        self.silinecek_no.text = ""
        self.kayitlari_listele()
        self.ozet_goster()

        self.mesaj_goster("Silindi", f"Tarih: {silinen.get('tarih', '')}\nGün toplamı: {para_yaz(silinen.get('gun_toplami', '0'))}")


if __name__ == "__main__":
    MaasTakipApp().run()
