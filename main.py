import os
import csv
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

class MaasApp(App):
    def build(self):
        self.title = "Maaş & Mesai Takip"
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

        self.btn_kaydet = Button(text="KAYDET / GÜNCELLE", background_color=(0.1, 0.6, 0.3, 1), size_hint_y=None, height=60)
        self.btn_kaydet.bind(on_press=self.kaydet_isleme)
        layout.add_widget(self.btn_kaydet)

        self.scroll = ScrollView()
        self.liste_label = Label(text="Henüz kayıt yok...", size_hint_y=None, halign='center', valign='top')
        self.liste_label.bind(texture_size=self.liste_label.setter('size'))
        self.scroll.add_widget(self.liste_label)
        layout.add_widget(self.scroll)

        self.listeyi_tazele()
        return layout

    def dosya_hazirla(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Tarih', 'Giris', 'Cikis'])

    def kaydet_isleme(self, instance):
        tarih, g, c = self.tarih_in.text, self.giris_in.text, self.cikis_in.text
        try:
            with open(self.file_path, mode='a', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow([tarih, g, c])
            self.listeyi_tazele()
        except Exception as e:
            self.liste_label.text = f"HATA: {str(e)}"

    def listeyi_tazele(self):
        if os.path.exists(self.file_path):
            metin = ""
            with open(self.file_path, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    metin += f"{row[0]} | {row[1]}-{row[2]}\n"
            self.liste_label.text = metin if metin else "Henüz kayıt yok..."

if __name__ == "__main__":
    MaasApp().run()
