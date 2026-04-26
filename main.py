import os
import csv
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

# --- HESAPLAMA AYARLARI ---
AYLIK_SABIT_MAAS = 38500
GUNLUK_SABIT_HAKEDIS = round(AYLIK_SABIT_MAAS / 30, 2)
SAATLIK_UCRET = AYLIK_SABIT_MAAS / 225
MESAI_CARPANI = 1.5
# 2026 Resmi Tatiller
TATIL_TAKVIMI = ["01.01", "23.04", "01.05", "19.05", "15.07", "30.08", "29.10", 
                 "20.03", "21.03", "22.03", "27.05", "28.05", "29.05", "30.05"]

class MaasApp(App):
    def build(self):
        self.title = "Maaş & Mesai Takip"
        # Android'de güvenli yazma klasörü
        self.file_path = os.path.join(self.user_data_dir, 'maas_verileri.csv')
        self.dosya_hazirla()
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Giriş Alanları
        layout.add_widget(Label(text="Tarih (GG.AA.YYYY):", size_hint_y=None, height=30))
        self.tarih_in = TextInput(text=datetime.now().strftime('%d.%m.%Y'), multiline=False)
        layout.add_widget(self.tarih_in)

        layout.add_widget(Label(text="Giriş - Çıkış Saatleri:", size_hint_y=None, height=30))
        time_box = BoxLayout(spacing=10, size_hint_y=None, height=50)
        self.giris_in = TextInput(text="09:00", multiline=False)
        self.cikis_in = TextInput(text="18:00", multiline=False)
        time_box.add_widget(self.giris_in)
        time_box.add_widget(self.cikis_in)
        layout.add_widget(time_box)

        # Butonlar
        self.btn_kaydet = Button(text="KAYDET / GÜNCELLE", background_color=(0.1, 0.6, 0.3, 1), size_hint_y=None, height=60)
        self.btn_kaydet.bind(on_press=self.kaydet_isleme)
        layout.add_widget(self.btn_kaydet)

        # Sonuç Listesi
        self.scroll = ScrollView()
        self.liste_label = Label(text="Henüz kayıt yok...", size_hint_y=None, halign='center', valign='top')
        self.liste_label.bind(texture_size=self.liste_label.setter('size'))
        self.scroll.add_widget(self.liste_label)
        layout.add_widget(self.scroll)

        self.toplam_label = Label(text="TOPLAM: 0 TL", bold=True, size_hint_y=None, height=50)
        layout.add_widget(self.toplam_label)

        self.listeyi_tazele()
        return layout

    def dosya_hazirla(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Tarih', 'Giris', 'Cikis', 'Kazanc'])

    def kaydet_isleme(self, instance):
        tarih = self.tarih_in.text
        g, c = self.giris_in.text, self.cikis_in.text
        gun_ay = tarih[:5]
        
        try:
            # Mesai Hesabı
            f1 = datetime.strptime(g, '%H:%M')
            f2 = datetime.strptime(c, '%H:%M')
            fark = (f2 - f1).seconds / 3600
            
            fazla_mesai = max(0, (fark - 1) - 8)
            mesai_para = fazla_mesai * (SAATLIK_UCRET * MESAI_CARPANI)
            
            # Tatil Ekstrası
            ek_yevmiye = GUNLUK_SABIT_HAKEDIS if gun_ay in TATIL_TAKVIMI else 0
            gunluk_toplam = round(GUNLUK_SABIT_HAKEDIS + mesai_para + ek_yevmiye, 2)

            # Veriyi oku ve güncelle (Pandas'sız versiyon)
            satirlar = []
            guncellendi = False
            if os.path.exists(self.file_path):
                with open(self.file_path, mode='r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    header = next(reader)
                    for row in reader:
                        if row[0] == tarih:
                            satirlar.append([tarih, g, c, gunluk_toplam])
                            guncellendi = True
                        else:
                            satirlar.append(row)
            
            if not guncellendi:
                satirlar.append([tarih, g, c, gunluk_toplam])

            # Geri yaz
            with open(self.file_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Tarih', 'Giris', 'Cikis', 'Kazanc'])
                writer.writerows(satirlar)

            self.listeyi_tazele()
        except Exception as e:
            self.liste_label.text = f"HATA: {str(e)}"

    def listeyi_tazele(self):
        if not os.path.exists(self.file_path):
            return

        total = 0
        metin = ""
        with open(self.file_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # başlığı atla
            for row in reader:
                metin += f"{row[0]} | {row[1]}-{row[2]} | {row[3]} TL\n"
                total += float(row[3])
        
        self.liste_label.text = metin if metin else "Henüz kayıt yok..."
        self.toplam_label.text = f"TOPLAM HAK EDİŞ: {total:,.2f} TL"

if __name__ == "__main__":
    MaasApp().run()
