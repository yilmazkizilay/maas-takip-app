import os
import csv
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class MaasApp(App):
    def build(self):
        self.file_path = os.path.join(self.user_data_dir, 'kayitlar.csv')
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f: f.write("Tarih\n")
            
        layout = BoxLayout(orientation='vertical', padding=20)
        self.lbl = Label(text="Maaş Takip Sistemi\nKayıt için butona bas")
        layout.add_widget(self.lbl)
        
        btn = Button(text="BUGÜNÜ KAYDET", size_hint_y=None, height=100)
        btn.bind(on_press=self.kaydet)
        layout.add_widget(btn)
        return layout

    def kaydet(self, obj):
        tarih = datetime.now().strftime('%d.%m.%Y %H:%M')
        with open(self.file_path, 'a') as f:
            f.write(f"{tarih}\n")
        self.lbl.text = f"Kaydedildi:\n{tarih}"

if __name__ == "__main__":
    MaasApp().run()
