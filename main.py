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
        self.title = "Maaş Takip"
        self.file_path = os.path.join(self.user_data_dir, 'maaslar.csv')
        self.dosya_hazirla()
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        layout.add_widget(Label(text="Kayıt Tarihi:", size_hint_y=None, height=30))
        
        self.tarih_in = TextInput(text=datetime.now().strftime('%d.%m.%Y'), multiline=False)
        layout.add_widget(self.tarih_in)

        btn = Button(text="KAYDET", background_color=(0, 0.6, 0.2, 1), size_hint_y=None, height=60)
        btn.bind(on_press=self.kaydet)
        layout.add_widget(btn)

        self.scroll = ScrollView()
        self.liste = Label(text="Kayıtlar burada görünecek", size_hint_y=None, halign='center')
        self.liste.bind(texture_size=self.liste.setter('size'))
        self.scroll.add_widget(self.liste)
        layout.add_widget(self.scroll)

        self.listeyi_yenile()
        return layout

    def dosya_hazirla(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(['Tarih'])

    def kaydet(self, instance):
        with open(self.file_path, 'a', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow([self.tarih_in.text])
        self.listeyi_yenile()

    def listeyi_yenile(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.liste.text = f.read()

if __name__ == "__main__":
    MaasApp().run()
