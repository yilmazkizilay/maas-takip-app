import os
import csv
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class MaasApp(App):
    def build(self):
        # Dosya yolunu Android'e göre ayarla
        self.file_path = os.path.join(self.user_data_dir, 'maas_kayitlari.csv')
        
        # Dosya yoksa başlığı oluştur
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write("Tarih\n")
            
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.lbl = Label(text="Maaş Takip Sistemi\n\nKayıt için butona basın", halign='center')
        layout.add_widget(self.lbl)
        
        btn = Button(text="BUGÜNÜ KAYDET", size_hint_y=None, height=100, background_color=(0, 0.7, 0.3, 1))
        btn.bind(on_press=self.kaydet)
        layout.add_widget(btn)
        
        return layout

    def kaydet(self, instance):
        simdi = datetime.now().strftime('%d.%m.%Y %H:%M')
        with open(self.file_path, 'a', encoding='utf-8') as f:
            f.write(f"{simdi}\n")
        self.lbl.text = f"Başarıyla Kaydedildi:\n{simdi}"

if __name__ == "__main__":
    MaasApp().run()
