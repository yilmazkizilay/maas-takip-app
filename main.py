import os
import json
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle

# --- PROFESYONEL TASARIM BİLEŞENLERİ ---
class ModernButton(Button):
    def __init__(self, bg_color=(0.1, 0.6, 0.3, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.bold = True
        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[12])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

# --- 1. KAYIT EKRANI ---
class KayitEkrani(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        layout.add_widget(Label(text="MESAİ KAYDI", font_size=26, bold=True, color=(0.2, 0.8, 0.4, 1), size_hint_y=None, height=60))

        # Tarih Seçici Bölümü
        layout.add_widget(Label(text="Çalışma Tarihi Seçin:", size_hint_y=None, height=30))
        self.btn_tarih = ModernButton(text=datetime.now().strftime('%d.%m.%Y'), size_hint_y=None, height=55, bg_color=(0.2, 0.2, 0.2, 1))
        self.btn_tarih.bind(on_press=self.tarih_secici_ac)
        layout.add_widget(self.btn_tarih)

        # Saat Girişi
        layout.add_widget(Label(text="Çalışma Saati:", size_hint_y=None, height=30))
        self.saat_input = TextInput(text="8", multiline=False, input_filter='float', size_hint_y=None, height=50, font_size=20, halign='center')
        layout.add_widget(self.saat_input)

        # Not Alanı
        layout.add_widget(Label(text="Açıklama / Not:", size_hint_y=None, height=30))
        self.not_input = TextInput(hint_text="İsteğe bağlı...", size_hint_y=None, height=50)
        layout.add_widget(self.not_input)

        layout.add_widget(Label(size_hint_y=1)) # Esnek boşluk

        # Kaydet Butonu
        btn_kaydet = ModernButton(text="KAYDI TAMAMLA", size_hint_y=None, height=65, font_size=18)
        btn_kaydet.bind(on_press=self.kaydet)
        layout.add_widget(btn_kaydet)

        self.add_widget(layout)

    def tarih_secici_ac(self, *args):
        icerik = BoxLayout(orientation='vertical', padding=10, spacing=10)
        secici = BoxLayout(spacing=5, size_hint_y=None, height=50)
        
        self.gun = Spinner(text=datetime.now().strftime('%d'), values=[str(i).zfill(2) for i in range(1, 32)])
        self.ay = Spinner(text=datetime.now().strftime('%m'), values=[str(i).zfill(2) for i in range(1, 13)])
        self.yil = Spinner(text=datetime.now().strftime('%Y'), values=[str(i) for i in range(2025, 2030)])
        
        secici.add_widget(self.gun); secici.add_widget(self.ay); secici.add_widget(self.yil)
        icerik.add_widget(secici)
        
        btn = ModernButton(text="SEÇ", size_hint_y=None, height=50)
        icerik.add_widget(btn)
        
        popup = Popup(title="Tarih Seçimi", content=icerik, size_hint=(0.8, 0.4))
        btn.bind(on_press=lambda x: self.tarih_onayla(popup))
        popup.open()

    def tarih_onayla(self, popup):
        self.btn_tarih.text = f"{self.gun.text}.{self.ay.text}.{self.yil.text}"
        popup.dismiss()

    def kaydet(self, *args):
        veri = {"tarih": self.btn_tarih.text, "saat": self.saat_input.text, "not": self.not_input.text}
        self.app.veri_ekle(veri)
        self.not_input.text = ""
        self.app.ekran_degistir("Gecmis")

# --- 2. GEÇMİŞ EKRANI ---
class GecmisEkrani(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        self.layout.add_widget(Label(text="KAYIT GEÇMİŞİ", font_size=20, bold=True, size_hint_y=None, height=50))
        
        self.scroll = ScrollView()
        self.liste = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8)
        self.liste.bind(minimum_height=self.liste.setter('height'))
        self.scroll.add_widget(self.liste)
        
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

    def on_enter(self):
        self.liste.clear_widgets()
        veriler = self.app.verileri_oku()
        for v in reversed(veriler):
            item = BoxLayout(orientation='vertical', size_hint_y=None, height=80, padding=10)
            with item.canvas.before:
                Color(0.15, 0.15, 0.15, 1)
                RoundedRectangle(size=item.size, pos=item.pos, radius=[10])
            item.add_widget(Label(text=f"[b]{v['tarih']}[/b]  |  {v['saat']} Saat", markup=True, color=(0.2, 0.8, 0.4, 1)))
            item.add_widget(Label(text=v['not'] if v['not'] else "Not yok", font_size=13, color=(0.6, 0.6, 0.6, 1)))
            self.liste.add_widget(item)

# --- 3. ÖZET EKRANI ---
class OzetEkrani(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        self.layout.add_widget(Label(text="AYLIK İSTATİSTİK", font_size=22, bold=True, color=(0.2, 0.8, 0.4, 1)))
        
        self.gun_lbl = Label(text="Toplam Gün: 0", font_size=18)
        self.saat_lbl = Label(text="Toplam Saat: 0", font_size=18)
        
        self.layout.add_widget(self.gun_lbl)
        self.layout.add_widget(self.saat_lbl)
        self.layout.add_widget(Label(size_hint_y=1))
        self.add_widget(self.layout)

    def on_enter(self):
        veriler = self.app.verileri_oku()
        toplam_saat = sum(float(v['saat']) for v in veriler if v['saat'])
        self.gun_lbl.text = f"Çalışılan Toplam Gün: [b]{len(veriler)}[/b]"
        self.saat_lbl.text = f"Toplam Mesai Saati: [b]{toplam_saat}[/b]"
        self.gun_lbl.markup = self.saat_lbl.markup = True

# --- ANA UYGULAMA SINIFI ---
class MaasPro(App):
    def build(self):
        Window.clearcolor = (0.08, 0.08, 0.08, 1)
        self.db = os.path.join(self.user_data_dir, 'database.json')
        
        ana_layout = BoxLayout(orientation='vertical')
        
        self.sm = ScreenManager()
        self.sm.add_widget(KayitEkrani(self, name="Kayit"))
        self.sm.add_widget(GecmisEkrani(self, name="Gecmis"))
        self.sm.add_widget(OzetEkrani(self, name="Ozet"))
        
        ana_layout.add_widget(self.sm)

        # Sekme Menüsü (Navigasyon)
        nav = BoxLayout(size_hint_y=None, height=65, padding=5, spacing=5)
        btn_k = ModernButton(text="YENİ", bg_color=(0.15, 0.15, 0.15, 1))
        btn_g = ModernButton(text="GEÇMİŞ", bg_color=(0.15, 0.15, 0.15, 1))
        btn_o = ModernButton(text="ÖZET", bg_color=(0.15, 0.15, 0.15, 1))
        
        btn_k.bind(on_press=lambda x: self.ekran_degistir("Kayit"))
        btn_g.bind(on_press=lambda x: self.ekran_degistir("Gecmis"))
        btn_o.bind(on_press=lambda x: self.ekran_degistir("Ozet"))
        
        nav.add_widget(btn_k); nav.add_widget(btn_g); nav.add_widget(btn_o)
        ana_layout.add_widget(nav)
        
        ana_layout.add_widget(Label(text="v1.0.0 Pro", size_hint_y=None, height=20, font_size=10, color=(0.4, 0.4, 0.4, 1)))
        return ana_layout

    def ekran_degistir(self, isim):
        self.sm.current = isim

    def verileri_oku(self):
        if not os.path.exists(self.db): return []
        with open(self.db, 'r', encoding='utf-8') as f: return json.load(f)

    def veri_ekle(self, veri):
        veriler = self.verileri_oku()
        veriler.append(veri)
        with open(self.db, 'w', encoding='utf-8') as f:
            json.dump(veriler, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    MaasPro().run()
from kivy.graphics import Color, RoundedRectangle

APP_VERSION = "0.7"
APP_TITLE = "Maaş Takip"
DATA_FILE_NAME = "records.json"
DATE_FMT = "%Y-%m-%d"


COLORS = {
    "bg": (0.965, 0.976, 0.992, 1),
    "card": (1, 1, 1, 1),
    "primary": (0.09, 0.32, 0.82, 1),
    "primary_dark": (0.06, 0.22, 0.55, 1),
    "soft_blue": (0.88, 0.925, 1, 1),
    "danger": (0.87, 0.18, 0.18, 1),
    "success": (0.10, 0.55, 0.28, 1),
    "warning": (0.95, 0.55, 0.10, 1),
    "text": (0.08, 0.10, 0.16, 1),
    "muted": (0.42, 0.46, 0.55, 1),
    "line": (0.88, 0.90, 0.94, 1),
}


MONTHS_TR = [
    "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
]

WEEKDAYS_TR = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]


# -----------------------------------------------------------------------------
# Yardımcı fonksiyonlar
# -----------------------------------------------------------------------------


def today_iso() -> str:
    return date.today().strftime(DATE_FMT)


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, DATE_FMT).date()
    except Exception:
        return date.today()


def format_date_tr(value: str) -> str:
    d = parse_date(value)
    return f"{d.day:02d} {MONTHS_TR[d.month - 1]} {d.year}"


def month_title(year: int, month: int) -> str:
    return f"{MONTHS_TR[month - 1]} {year}"


def parse_float(value: str) -> float:
    value = (value or "").strip().replace(" ", "").replace(",", ".")
    if not value:
        return 0.0
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Sayı alanı hatalı: {value}")


def fmt_num(value: float) -> str:
    value = float(value or 0)
    if value.is_integer():
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def make_record(
    record_date: str,
    title: str,
    record_type: str,
    work_hours: float,
    missing_hours: float,
    amount: float,
    note: str,
    record_id: Optional[str] = None,
    created_at: Optional[str] = None,
) -> Dict:
    return {
        "id": record_id or uuid.uuid4().hex,
        "date": record_date,
        "title": title.strip() or "Kayıt",
        "type": record_type.strip() or "Diğer",
        "work_hours": float(work_hours or 0),
        "missing_hours": float(missing_hours or 0),
        "amount": float(amount or 0),
        "note": note.strip(),
        "created_at": created_at or now_iso(),
        "updated_at": now_iso(),
    }


def normalize_record(raw: Dict) -> Dict:
    """Eski sürüm kayıtlarını da kırmadan v0.7 formatına çeker."""
    return {
        "id": raw.get("id") or uuid.uuid4().hex,
        "date": raw.get("date") or raw.get("tarih") or today_iso(),
        "title": raw.get("title") or raw.get("baslik") or raw.get("text") or raw.get("aciklama") or "Kayıt",
        "type": raw.get("type") or raw.get("tur") or "Diğer",
        "work_hours": float(raw.get("work_hours") or raw.get("calisma_saati") or 0),
        "missing_hours": float(raw.get("missing_hours") or raw.get("eksik_saat") or 0),
        "amount": float(raw.get("amount") or raw.get("tutar") or 0),
        "note": raw.get("note") or raw.get("not") or "",
        "created_at": raw.get("created_at") or now_iso(),
        "updated_at": raw.get("updated_at") or now_iso(),
    }


def test_writable(folder: str) -> bool:
    try:
        os.makedirs(folder, exist_ok=True)
        probe = os.path.join(folder, ".write_test")
        with open(probe, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(probe)
        return True
    except Exception:
        return False


def safe_data_dir(app: App) -> str:
    """
    Error 13 / permission denied çözümü:
    Android'da dış depolamaya değil, uygulamanın kendi yazılabilir alanına kaydeder.
    """
    candidates: List[str] = []

    if platform == "android":
        try:
            from android.storage import app_storage_path  # type: ignore
            candidates.append(os.path.join(app_storage_path(), "data"))
        except Exception:
            pass

    try:
        candidates.append(os.path.join(app.user_data_dir, "data"))
    except Exception:
        pass

    candidates.extend([
        os.path.join(os.path.expanduser("~"), ".maas_takip", "data"),
        os.path.join(os.getcwd(), "data"),
    ])

    for folder in candidates:
        if folder and test_writable(folder):
            return folder

    # Son çare. Çok nadir gerekir ama uygulama boş ekranda kalmasın.
    fallback = os.path.join(os.getcwd(), "data")
    os.makedirs(fallback, exist_ok=True)
    return fallback


# -----------------------------------------------------------------------------
# Görsel yardımcılar
# -----------------------------------------------------------------------------


class RoundedPanel(BoxLayout):
    def __init__(self, bg_color=COLORS["card"], radius=18, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.radius = radius
        with self.canvas.before:
            Color(*self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(self.radius)])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *_args):
        self._rect.pos = self.pos
        self._rect.size = self.size


def label(
    text: str,
    size: int = 15,
    color=COLORS["text"],
    bold: bool = False,
    markup: bool = False,
    halign: str = "left",
    valign: str = "middle",
    height: Optional[float] = None,
) -> Label:
    lbl = Label(
        text=text,
        font_size=sp(size),
        color=color,
        bold=bold,
        markup=markup,
        halign=halign,
        valign=valign,
        size_hint_y=None if height else None,
        height=height or dp(24),
    )
    lbl.bind(width=lambda inst, value: setattr(inst, "text_size", (value, None)))
    lbl.bind(texture_size=lambda inst, value: setattr(inst, "height", max(value[1] + dp(4), height or dp(24))))
    return lbl


def sp(value: int) -> float:
    # Kodun her yerde okunur kalması için basit wrapper.
    from kivy.metrics import sp as kivy_sp
    return kivy_sp(value)


def button(
    text: str,
    bg=COLORS["primary"],
    fg=(1, 1, 1, 1),
    height: float = 44,
    font_size: int = 15,
) -> Button:
    return Button(
        text=text,
        size_hint_y=None,
        height=dp(height),
        background_normal="",
        background_down="",
        background_color=bg,
        color=fg,
        font_size=sp(font_size),
    )


def tiny_button(text: str, bg=COLORS["soft_blue"], fg=COLORS["primary_dark"]) -> Button:
    return button(text, bg=bg, fg=fg, height=38, font_size=14)


def show_message(title: str, message: str):
    box = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
    msg = label(message, size=15, color=COLORS["text"])
    msg.halign = "left"
    box.add_widget(msg)
    ok = button("Tamam", height=42)
    box.add_widget(ok)
    popup = Popup(title=title, content=box, size_hint=(0.90, None), height=dp(260), auto_dismiss=True)
    ok.bind(on_release=popup.dismiss)
    popup.open()


# -----------------------------------------------------------------------------
# Veri katmanı
# -----------------------------------------------------------------------------


class RecordStore:
    def __init__(self, app: App):
        self.app = app
        self.data_dir = safe_data_dir(app)
        self.path = os.path.join(self.data_dir, DATA_FILE_NAME)
        self.records: List[Dict] = []

    def load(self):
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.path):
            self.records = []
            self.save()
            return

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                raw_records = data.get("records", [])
            elif isinstance(data, list):
                raw_records = data
            else:
                raw_records = []
            self.records = [normalize_record(item) for item in raw_records if isinstance(item, dict)]
            self.save()
        except Exception as exc:
            backup = self.path + f".bozuk_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                shutil.copy2(self.path, backup)
            except Exception:
                backup = "yedek alınamadı"
            self.records = []
            self.save()
            show_message(
                "Kayıt Dosyası Onarıldı",
                f"Eski dosya okunamadı. Yeni temiz dosya açıldı.\n\nYedek: {backup}\n\nHata: {exc}",
            )

    def save(self):
        os.makedirs(self.data_dir, exist_ok=True)
        payload = {
            "app": APP_TITLE,
            "version": APP_VERSION,
            "saved_at": now_iso(),
            "records": self.records,
        }
        tmp_path = self.path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, self.path)
        except PermissionError as exc:
            raise RuntimeError(
                "Kayıt dosyasına yazılamadı. Error 13/izin hatası gibi görünüyor. "
                f"Uygulama klasörü: {self.data_dir}\n\nDetay: {exc}"
            ) from exc
        except Exception as exc:
            raise RuntimeError(f"Kayıt kaydedilemedi. Detay: {exc}") from exc

    def add(self, record: Dict):
        self.records.append(record)
        self.save()

    def update(self, record_id: str, new_record: Dict):
        for idx, old in enumerate(self.records):
            if old.get("id") == record_id:
                new_record["id"] = record_id
                new_record["created_at"] = old.get("created_at") or new_record.get("created_at") or now_iso()
                new_record["updated_at"] = now_iso()
                self.records[idx] = new_record
                self.save()
                return
        raise RuntimeError("Düzenlenecek kayıt bulunamadı.")

    def delete(self, record_id: str):
        before = len(self.records)
        self.records = [r for r in self.records if r.get("id") != record_id]
        if len(self.records) == before:
            raise RuntimeError("Silinecek kayıt bulunamadı.")
        self.save()

    def records_for_month(self, year: int, month: int) -> List[Dict]:
        output = []
        for rec in self.records:
            d = parse_date(rec.get("date", today_iso()))
            if d.year == year and d.month == month:
                output.append(rec)
        return sorted(output, key=lambda r: (r.get("date", ""), r.get("created_at", "")), reverse=True)


# -----------------------------------------------------------------------------
# Takvim popup
# -----------------------------------------------------------------------------


class CalendarPopup(Popup):
    def __init__(self, initial_date: date, on_select: Callable[[date], None], title="Tarih Seç", **kwargs):
        super().__init__(**kwargs)
        self.selected = initial_date or date.today()
        self.view_year = self.selected.year
        self.view_month = self.selected.month
        self.on_select_callback = on_select
        self.title = title
        self.size_hint = (0.95, 0.86)
        self.auto_dismiss = True
        self.content = self._build()
        self._refresh_days()

    def _build(self) -> BoxLayout:
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))

        top = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        prev_btn = tiny_button("‹", bg=COLORS["primary"], fg=(1, 1, 1, 1))
        next_btn = tiny_button("›", bg=COLORS["primary"], fg=(1, 1, 1, 1))
        self.month_lbl = label("", size=18, bold=True, halign="center", height=dp(44))
        self.month_lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        top.add_widget(prev_btn)
        top.add_widget(self.month_lbl)
        top.add_widget(next_btn)
        prev_btn.bind(on_release=lambda *_: self._change_month(-1))
        next_btn.bind(on_release=lambda *_: self._change_month(1))
        root.add_widget(top)

        weekdays = GridLayout(cols=7, size_hint_y=None, height=dp(30), spacing=dp(3))
        for day_name in WEEKDAYS_TR:
            weekdays.add_widget(label(day_name, size=13, color=COLORS["muted"], bold=True, halign="center", height=dp(28)))
        root.add_widget(weekdays)

        self.days_grid = GridLayout(cols=7, spacing=dp(4), size_hint_y=1)
        root.add_widget(self.days_grid)

        bottom = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        today_btn = tiny_button("Bugün", bg=COLORS["success"], fg=(1, 1, 1, 1))
        cancel_btn = tiny_button("Vazgeç", bg=(0.82, 0.84, 0.88, 1), fg=COLORS["text"])
        bottom.add_widget(today_btn)
        bottom.add_widget(cancel_btn)
        root.add_widget(bottom)

        today_btn.bind(on_release=lambda *_: self._select(date.today()))
        cancel_btn.bind(on_release=lambda *_: self.dismiss())
        return root

    def _change_month(self, delta: int):
        month = self.view_month + delta
        year = self.view_year
        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1
        self.view_year = year
        self.view_month = month
        self._refresh_days()

    def _refresh_days(self):
        self.month_lbl.text = month_title(self.view_year, self.view_month)
        self.days_grid.clear_widgets()

        cal = calendar.Calendar(firstweekday=0)  # Pazartesi
        days = list(cal.itermonthdates(self.view_year, self.view_month))
        for d in days:
            is_current_month = d.month == self.view_month
            is_selected = d == self.selected
            is_today = d == date.today()

            if is_selected:
                bg = COLORS["primary"]
                fg = (1, 1, 1, 1)
            elif is_today:
                bg = COLORS["soft_blue"]
                fg = COLORS["primary_dark"]
            elif is_current_month:
                bg = (0.96, 0.97, 0.99, 1)
                fg = COLORS["text"]
            else:
                bg = (0.91, 0.92, 0.94, 1)
                fg = (0.62, 0.66, 0.72, 1)

            day_btn = Button(
                text=str(d.day),
                background_normal="",
                background_down="",
                background_color=bg,
                color=fg,
                font_size=sp(14),
            )
            day_btn.bind(on_release=lambda _btn, picked=d: self._select(picked))
            self.days_grid.add_widget(day_btn)

    def _select(self, picked: date):
        self.on_select_callback(picked)
        self.dismiss()


# -----------------------------------------------------------------------------
# Kayıt formu
# -----------------------------------------------------------------------------


class RecordFormPopup(Popup):
    def __init__(
        self,
        on_save: Callable[[Dict], None],
        record: Optional[Dict] = None,
        title: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.record = normalize_record(record) if record else None
        self.on_save_callback = on_save
        self.selected_date = parse_date(self.record["date"]) if self.record else date.today()
        self.title = title or ("Kaydı Düzenle" if record else "Yeni Kayıt")
        self.size_hint = (0.95, 0.92)
        self.auto_dismiss = False
        self.content = self._build()

    def _build(self) -> BoxLayout:
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))

        scroll = ScrollView()
        form = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        form.bind(minimum_height=form.setter("height"))

        form.add_widget(label("Tarih", size=13, color=COLORS["muted"], bold=True))
        self.date_btn = button(format_date_tr(self.selected_date.strftime(DATE_FMT)), bg=COLORS["soft_blue"], fg=COLORS["primary_dark"])
        self.date_btn.bind(on_release=lambda *_: self.open_calendar())
        form.add_widget(self.date_btn)

        form.add_widget(label("Kayıt başlığı / açıklama", size=13, color=COLORS["muted"], bold=True))
        self.title_input = TextInput(
            text=(self.record or {}).get("title", ""),
            hint_text="Örn: Normal çalışma, eksik saat, avans, mesai...",
            multiline=False,
            size_hint_y=None,
            height=dp(46),
            foreground_color=COLORS["text"],
            cursor_color=COLORS["primary"],
            background_color=(1, 1, 1, 1),
            font_size=sp(15),
        )
        form.add_widget(self.title_input)

        form.add_widget(label("Kayıt türü", size=13, color=COLORS["muted"], bold=True))
        self.type_spinner = Spinner(
            text=(self.record or {}).get("type", "Çalışma"),
            values=("Çalışma", "Eksik Saat", "Mesai", "İzin", "Avans", "Ödeme", "Diğer"),
            size_hint_y=None,
            height=dp(46),
            background_normal="",
            background_color=COLORS["soft_blue"],
            color=COLORS["primary_dark"],
            font_size=sp(15),
        )
        form.add_widget(self.type_spinner)

        row = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(84))
        row.add_widget(self._number_field_box("Çalışma saati", "work_hours", "0"))
        row.add_widget(self._number_field_box("Eksik saat", "missing_hours", "0"))
        form.add_widget(row)

        form.add_widget(label("Tutar / ödeme / avans (opsiyonel)", size=13, color=COLORS["muted"], bold=True))
        self.amount_input = TextInput(
            text=fmt_num((self.record or {}).get("amount", 0)),
            hint_text="0",
            multiline=False,
            input_filter=None,
            input_type="number",
            size_hint_y=None,
            height=dp(46),
            foreground_color=COLORS["text"],
            cursor_color=COLORS["primary"],
            background_color=(1, 1, 1, 1),
            font_size=sp(15),
        )
        form.add_widget(self.amount_input)

        form.add_widget(label("Not", size=13, color=COLORS["muted"], bold=True))
        self.note_input = TextInput(
            text=(self.record or {}).get("note", ""),
            hint_text="İstersen ayrıntı yaz. Boş da kalabilir.",
            multiline=True,
            size_hint_y=None,
            height=dp(100),
            foreground_color=COLORS["text"],
            cursor_color=COLORS["primary"],
            background_color=(1, 1, 1, 1),
            font_size=sp(15),
        )
        form.add_widget(self.note_input)

        scroll.add_widget(form)
        root.add_widget(scroll)

        actions = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        cancel = button("Vazgeç", bg=(0.78, 0.80, 0.84, 1), fg=COLORS["text"])
        save = button("Kaydet", bg=COLORS["success"])
        actions.add_widget(cancel)
        actions.add_widget(save)
        root.add_widget(actions)

        cancel.bind(on_release=lambda *_: self.dismiss())
        save.bind(on_release=lambda *_: self.save())
        return root

    def _number_field_box(self, title: str, attr: str, hint: str) -> BoxLayout:
        box = BoxLayout(orientation="vertical", spacing=dp(4))
        box.add_widget(label(title, size=13, color=COLORS["muted"], bold=True))
        inp = TextInput(
            text=fmt_num((self.record or {}).get(attr, 0)),
            hint_text=hint,
            multiline=False,
            input_filter=None,
            input_type="number",
            size_hint_y=None,
            height=dp(46),
            foreground_color=COLORS["text"],
            cursor_color=COLORS["primary"],
            background_color=(1, 1, 1, 1),
            font_size=sp(15),
        )
        setattr(self, f"{attr}_input", inp)
        box.add_widget(inp)
        return box

    def open_calendar(self):
        CalendarPopup(self.selected_date, self._set_date, title="Kayıt Tarihi Seç").open()

    def _set_date(self, picked: date):
        self.selected_date = picked
        self.date_btn.text = format_date_tr(picked.strftime(DATE_FMT))

    def save(self):
        try:
            rec = make_record(
                record_date=self.selected_date.strftime(DATE_FMT),
                title=self.title_input.text,
                record_type=self.type_spinner.text,
                work_hours=parse_float(self.work_hours_input.text),
                missing_hours=parse_float(self.missing_hours_input.text),
                amount=parse_float(self.amount_input.text),
                note=self.note_input.text,
                record_id=(self.record or {}).get("id"),
                created_at=(self.record or {}).get("created_at"),
            )
            self.on_save_callback(rec)
            self.dismiss()
        except Exception as exc:
            show_message("Kaydedilemedi", str(exc))


# -----------------------------------------------------------------------------
# Uzun basılabilir kart
# -----------------------------------------------------------------------------


class LongPressCard(RoundedPanel):
    record = ObjectProperty(None)

    def __init__(self, record: Dict, on_long_press: Callable[[Dict], None], **kwargs):
        super().__init__(bg_color=COLORS["card"], radius=20, **kwargs)
        self.record = record
        self.on_long_press_callback = on_long_press
        self._long_press_event = None
        self._touch_start = None
        self._long_pressed = False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch_start = touch.pos
            self._long_pressed = False
            touch.grab(self)
            self._long_press_event = Clock.schedule_once(lambda *_: self._fire_long_press(), 0.55)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self and self._touch_start:
            dx = abs(touch.pos[0] - self._touch_start[0])
            dy = abs(touch.pos[1] - self._touch_start[1])
            if dx > dp(14) or dy > dp(14):
                self._cancel_long_press()
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self._cancel_long_press()
            # Kısa dokunuşta da kolaylık olsun diye aynı menüyü açıyoruz.
            if not self._long_pressed and self.collide_point(*touch.pos):
                self.on_long_press_callback(self.record)
            return True
        return super().on_touch_up(touch)

    def _fire_long_press(self):
        self._long_pressed = True
        self.on_long_press_callback(self.record)

    def _cancel_long_press(self):
        if self._long_press_event is not None:
            self._long_press_event.cancel()
            self._long_press_event = None


# -----------------------------------------------------------------------------
# Ana ekran
# -----------------------------------------------------------------------------


class MainScreen(BoxLayout):
    def __init__(self, store: RecordStore, **kwargs):
        super().__init__(orientation="vertical", padding=dp(12), spacing=dp(10), **kwargs)
        self.store = store
        now = date.today()
        self.current_year = now.year
        self.current_month = now.month
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        header = RoundedPanel(orientation="vertical", padding=dp(14), spacing=dp(4), size_hint_y=None, bg_color=COLORS["primary"], radius=24)
        header.bind(minimum_height=header.setter("height"))

        title_row = BoxLayout(size_hint_y=None, height=dp(34), spacing=dp(8))
        title = label(f"{APP_TITLE}", size=24, color=(1, 1, 1, 1), bold=True, height=dp(34))
        version = label(f"v{APP_VERSION}", size=14, color=(0.88, 0.92, 1, 1), bold=True, halign="right", height=dp(34))
        version.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        title_row.add_widget(title)
        title_row.add_widget(version)
        header.add_widget(title_row)

        subtitle = label(
            "Kayıtlar güvenli uygulama klasörüne kaydedilir. Kartlara bas: düzenle / sil.",
            size=13,
            color=(0.88, 0.92, 1, 1),
        )
        header.add_widget(subtitle)
        self.add_widget(header)

        actions = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        add_btn = button("+ Yeni Kayıt", bg=COLORS["success"])
        path_btn = button("Kayıt Yeri", bg=COLORS["soft_blue"], fg=COLORS["primary_dark"])
        actions.add_widget(add_btn)
        actions.add_widget(path_btn)
        self.add_widget(actions)
        add_btn.bind(on_release=lambda *_: self.open_add_record())
        path_btn.bind(on_release=lambda *_: self.show_data_path())

        month_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        prev_btn = tiny_button("‹", bg=COLORS["primary"], fg=(1, 1, 1, 1))
        next_btn = tiny_button("›", bg=COLORS["primary"], fg=(1, 1, 1, 1))
        self.month_btn = button("", bg=COLORS["soft_blue"], fg=COLORS["primary_dark"])
        month_row.add_widget(prev_btn)
        month_row.add_widget(self.month_btn)
        month_row.add_widget(next_btn)
        self.add_widget(month_row)
        prev_btn.bind(on_release=lambda *_: self.change_month(-1))
        next_btn.bind(on_release=lambda *_: self.change_month(1))
        self.month_btn.bind(on_release=lambda *_: self.open_month_calendar())

        self.summary_panel = RoundedPanel(orientation="vertical", padding=dp(12), spacing=dp(2), size_hint_y=None, bg_color=COLORS["card"], radius=18)
        self.summary_panel.bind(minimum_height=self.summary_panel.setter("height"))
        self.summary_title = label("Aylık Özet", size=16, color=COLORS["text"], bold=True)
        self.summary_detail = label("", size=14, color=COLORS["muted"])
        self.summary_panel.add_widget(self.summary_title)
        self.summary_panel.add_widget(self.summary_detail)
        self.add_widget(self.summary_panel)

        self.scroll = ScrollView(size_hint=(1, 1), bar_width=dp(4))
        self.list_box = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=(0, dp(2), 0, dp(12)))
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        self.scroll.add_widget(self.list_box)
        self.add_widget(self.scroll)

    def refresh(self):
        self.month_btn.text = month_title(self.current_year, self.current_month) + "  📅"
        records = self.store.records_for_month(self.current_year, self.current_month)
        self._refresh_summary(records)
        self._refresh_cards(records)

    def _refresh_summary(self, records: List[Dict]):
        total_work = sum(float(r.get("work_hours", 0) or 0) for r in records)
        total_missing = sum(float(r.get("missing_hours", 0) or 0) for r in records)
        total_amount = sum(float(r.get("amount", 0) or 0) for r in records)
        days = len({r.get("date") for r in records})
        self.summary_detail.text = (
            f"{len(records)} kayıt • {days} gün • Çalışma: {fmt_num(total_work)} saat • "
            f"Eksik: {fmt_num(total_missing)} saat • Tutar: {fmt_num(total_amount)} TL"
        )

    def _refresh_cards(self, records: List[Dict]):
        self.list_box.clear_widgets()

        if not records:
            empty = RoundedPanel(orientation="vertical", padding=dp(16), spacing=dp(8), size_hint_y=None, bg_color=COLORS["card"], radius=20)
            empty.bind(minimum_height=empty.setter("height"))
            empty.add_widget(label("Bu ay kayıt yok.", size=18, color=COLORS["text"], bold=True, halign="center"))
            empty.add_widget(label("+ Yeni Kayıt ile başla. Tarihi takvimden seçebilirsin.", size=14, color=COLORS["muted"], halign="center"))
            self.list_box.add_widget(empty)
            return

        for rec in records:
            card = self._record_card(rec)
            self.list_box.add_widget(card)

    def _record_card(self, rec: Dict) -> LongPressCard:
        card = LongPressCard(
            record=rec,
            on_long_press=self.open_record_actions,
            orientation="vertical",
            padding=dp(12),
            spacing=dp(5),
            size_hint_y=None,
        )
        card.bind(minimum_height=card.setter("height"))

        top = BoxLayout(size_hint_y=None, height=dp(30), spacing=dp(6))
        top.add_widget(label(format_date_tr(rec.get("date", today_iso())), size=15, color=COLORS["primary_dark"], bold=True, height=dp(30)))
        tag = label(rec.get("type", "Diğer"), size=13, color=COLORS["muted"], bold=True, halign="right", height=dp(30))
        tag.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        top.add_widget(tag)
        card.add_widget(top)

        card.add_widget(label(rec.get("title", "Kayıt"), size=17, color=COLORS["text"], bold=True))

        info_bits = []
        work = float(rec.get("work_hours", 0) or 0)
        missing = float(rec.get("missing_hours", 0) or 0)
        amount = float(rec.get("amount", 0) or 0)
        if work:
            info_bits.append(f"Çalışma: {fmt_num(work)} saat")
        if missing:
            info_bits.append(f"Eksik: {fmt_num(missing)} saat")
        if amount:
            info_bits.append(f"Tutar: {fmt_num(amount)} TL")
        if not info_bits:
            info_bits.append("Sadece not/text kaydı")
        card.add_widget(label(" • ".join(info_bits), size=14, color=COLORS["muted"]))

        note = (rec.get("note") or "").strip()
        if note:
            card.add_widget(label(note, size=14, color=COLORS["text"]))

        hint = label("Basılı tut: düzenle / sil", size=12, color=(0.62, 0.66, 0.74, 1), halign="right")
        hint.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        card.add_widget(hint)
        return card

    def change_month(self, delta: int):
        month = self.current_month + delta
        year = self.current_year
        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1
        self.current_month = month
        self.current_year = year
        self.refresh()

    def open_month_calendar(self):
        initial = date(self.current_year, self.current_month, 1)
        CalendarPopup(initial, self._set_month_from_calendar, title="Aylık Görünüm İçin Tarih Seç").open()

    def _set_month_from_calendar(self, picked: date):
        self.current_year = picked.year
        self.current_month = picked.month
        self.refresh()

    def open_add_record(self):
        RecordFormPopup(on_save=self._add_record, title="Yeni Kayıt").open()

    def _add_record(self, rec: Dict):
        try:
            self.store.add(rec)
            d = parse_date(rec["date"])
            self.current_year = d.year
            self.current_month = d.month
            self.refresh()
        except Exception as exc:
            show_message("Kayıt Eklenemedi", str(exc))

    def open_edit_record(self, rec: Dict):
        RecordFormPopup(on_save=lambda updated: self._update_record(rec["id"], updated), record=rec, title="Kaydı Düzenle").open()

    def _update_record(self, record_id: str, updated: Dict):
        try:
            self.store.update(record_id, updated)
            d = parse_date(updated["date"])
            self.current_year = d.year
            self.current_month = d.month
            self.refresh()
        except Exception as exc:
            show_message("Kayıt Güncellenemedi", str(exc))

    def open_record_actions(self, rec: Dict):
        box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        box.add_widget(label(format_date_tr(rec.get("date", today_iso())), size=14, color=COLORS["muted"], bold=True))
        box.add_widget(label(rec.get("title", "Kayıt"), size=18, color=COLORS["text"], bold=True))

        edit_btn = button("Düzenle", bg=COLORS["primary"])
        delete_btn = button("Sil", bg=COLORS["danger"])
        close_btn = button("Vazgeç", bg=(0.78, 0.80, 0.84, 1), fg=COLORS["text"])
        box.add_widget(edit_btn)
        box.add_widget(delete_btn)
        box.add_widget(close_btn)

        popup = Popup(title="Kayıt İşlemleri", content=box, size_hint=(0.90, None), height=dp(310), auto_dismiss=True)
        edit_btn.bind(on_release=lambda *_: (popup.dismiss(), self.open_edit_record(rec)))
        delete_btn.bind(on_release=lambda *_: (popup.dismiss(), self.confirm_delete(rec)))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def confirm_delete(self, rec: Dict):
        box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        box.add_widget(label("Bu kayıt silinsin mi?", size=18, color=COLORS["text"], bold=True))
        box.add_widget(label(rec.get("title", "Kayıt"), size=15, color=COLORS["muted"]))
        actions = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        no_btn = button("Vazgeç", bg=(0.78, 0.80, 0.84, 1), fg=COLORS["text"])
        yes_btn = button("Evet, Sil", bg=COLORS["danger"])
        actions.add_widget(no_btn)
        actions.add_widget(yes_btn)
        box.add_widget(actions)
        popup = Popup(title="Silme Onayı", content=box, size_hint=(0.90, None), height=dp(240), auto_dismiss=False)
        no_btn.bind(on_release=popup.dismiss)
        yes_btn.bind(on_release=lambda *_: (popup.dismiss(), self._delete_record(rec.get("id"))))
        popup.open()

    def _delete_record(self, record_id: str):
        try:
            self.store.delete(record_id)
            self.refresh()
        except Exception as exc:
            show_message("Kayıt Silinemedi", str(exc))

    def show_data_path(self):
        message = (
            "Kayıtlar artık uygulamanın kendi güvenli klasöründe tutuluyor.\n\n"
            f"Klasör:\n{self.store.data_dir}\n\n"
            f"Dosya:\n{self.store.path}\n\n"
            "Not: Android'da bu klasör normal dosya yöneticisinde görünmeyebilir. Bu bilinçli: Error 13 yememek için "
            "uygulamanın özel alanı kullanılıyor."
        )
        box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        box.add_widget(label(message, size=14, color=COLORS["text"]))
        copy_btn = button("Yolu Kopyala", bg=COLORS["primary"])
        ok_btn = button("Tamam", bg=(0.78, 0.80, 0.84, 1), fg=COLORS["text"])
        box.add_widget(copy_btn)
        box.add_widget(ok_btn)
        popup = Popup(title="Kayıt Yeri", content=box, size_hint=(0.92, None), height=dp(420), auto_dismiss=True)
        copy_btn.bind(on_release=lambda *_: (Clipboard.copy(self.store.path), show_message("Kopyalandı", "Kayıt dosyası yolu panoya kopyalandı.")))
        ok_btn.bind(on_release=popup.dismiss)
        popup.open()


class MaasTakipApp(App):
    def build(self):
        self.title = f"{APP_TITLE} v{APP_VERSION}"
        Window.clearcolor = COLORS["bg"]
        self.store = RecordStore(self)
        self.store.load()
        return MainScreen(self.store)


if __name__ == "__main__":
    MaasTakipApp().run()
