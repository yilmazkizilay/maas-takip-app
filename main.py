import pandas as pd
import os
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView

def dosya_yolunu_al(dosya_adi):
    # Bu satır, uygulamanın Android'deki "özel kutusunu" bulur
    from kivy.app import App
    import os
    
    # Eğer uygulama çalışıyorsa özel klasörü bul, yoksa (bilgisayardaysan) olduğun yere yaz
    try:
        yol = App.get_running_app().user_data_dir
    except:
        yol = "."
        
    return os.path.join(yol, dosya_adi)
  
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
        # Telefonun güvenli klasörüne dosyayı kaydet
        self.file_name = os.path.join(self.user_data_dir, 'maas_verileri.csv')
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

        # Sonuç Listesi (Görsel tablo)
        self.scroll = ScrollView()
        self.liste_label = Label(text="Henüz kayıt yok...", size_hint_y=None, halign='center')
        self.liste_label.bind(texture_size=self.liste_label.setter('size'))
        self.scroll.add_widget(self.liste_label)
        layout.add_widget(self.scroll)

        self.toplam_label = Label(text="TOPLAM: 0 TL", bold=True, size_hint_y=None, height=50)
        layout.add_widget(self.toplam_label)

        self.listeyi_tazele()
        return layout

    def dosya_hazirla(self):
        if not os.path.exists(self.file_name):
            pd.DataFrame(columns=['Tarih', 'Giris', 'Cikis', 'Kazanc']).to_csv(self.file_name, index=False)

    def kaydet_isleme(self, instance):
        tarih = self.tarih_in.text
        g, c = self.giris_in.text, self.cikis_in.text
        gun_ay = tarih[:5] # "23.04" gibi
        
        try:
            # Mesai Hesabı
            fark = (datetime.strptime(c, '%H:%M') - datetime.strptime(g, '%H:%M')).seconds / 3600
            fazla_mesai = max(0, (fark - 1) - 8)
            mesai_para = fazla_mesai * (SAATLIK_UCRET * MESAI_CARPANI)
            
            # Tatil Ekstrası (+1 yevmiye)
            ek_yevmiye = GUNLUK_SABIT_HAKEDIS if gun_ay in TATIL_TAKVIMI else 0
            
            # Günlük Toplam
            gunluk_toplam = round(GUNLUK_SABIT_HAKEDIS + mesai_para + ek_yevmiye, 2)

            df = pd.read_csv(self.file_name)
            df = df[df['Tarih'] != tarih] # Varsa eskiyi sil
            yeni = pd.DataFrame([[tarih, g, c, gunluk_toplam]], columns=['Tarih', 'Giris', 'Cikis', 'Kazanc'])
            df = pd.concat([df, yeni], ignore_index=True)
            df.to_csv(dosya_yolunu_al('maaslar.csv'), index=False)
            self.listeyi_tazele()
        except:
            self.liste_label.text = "HATA: Saatleri kontrol et!"

    def listeyi_tazele(self):
        df = pd.read_csv(self.file_name)
        if not df.empty:
            metin = ""
            for _, row in df.iterrows():
                metin += f"{row['Tarih']} | {row['Giris']}-{row['Cikis']} | {row['Kazanc']} TL\n"
            self.liste_label.text = metin
            self.toplam_label.text = f"TOPLAM HAK EDİŞ: {df['Kazanc'].sum():,.2f} TL"

if __name__ == "__main__":
    MaasApp().run()
