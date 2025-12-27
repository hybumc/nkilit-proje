from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
import os

# Tam Ekran ve Pencere Ayarları
Window.fullscreen = 'auto'
Window.borderless = True

kv = """
<MainScreen>:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: (0.1, 0.1, 0.1, 1)
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        size_hint_y: 0.1
        canvas.before:
            Color:
                rgba: (1, 1, 1, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: '  N-KİLİT KURULUM SİSTEMİ'
            color: (0, 0, 0, 1)
            halign: 'left'
            text_size: self.size
        Label:
            text: 'N-KİLİT V2  '
            bold: True
            color: (0, 0.47, 0.84, 1)
            halign: 'right'
            text_size: self.size

    BoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 15
        canvas.before:
            Color:
                rgba: (1, 1, 1, 1)
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [25, 25, 0, 0]

        TextInput:
            id: cihaz_adi
            hint_text: 'Cihaz Kimliği / Adı'
            size_hint_y: None
            height: '50dp'
            multiline: False

        TextInput:
            id: admin_sifre
            hint_text: 'Yönetici Panel Şifresi'
            password: True
            size_hint_y: None
            height: '50dp'

        TextInput:
            id: kilit_sifre
            hint_text: 'Ana Kilit Şifresi'
            password: True
            size_hint_y: None
            height: '50dp'

        Label:
            id: hata_mesaji
            text: 'Sistemi kurduktan sonra cihaz kilitlenecektir.'
            color: (0.5, 0.5, 0.5, 1)
            size_hint_y: None
            height: '30dp'

        Button:
            text: 'SİSTEMİ VE KORUMAYI AKTİF ET'
            size_hint_y: None
            height: '65dp'
            bold: True
            background_normal: ''
            background_color: (0, 0.47, 0.84, 1)
            on_press: app.validate_and_save()

<ControlPanel>:
    size_hint: (None, None)
    size: ("180dp", "120dp")
    pos_hint: {'right': 1, 'y': 0}
    orientation: 'vertical'
    spacing: 8
    padding: 12
    canvas.before:
        Color:
            rgba: (0, 0, 0, 0.9)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [30, 0, 0, 0]
    Button:
        text: 'CİHAZI KİLİTLE'
        bold: True
        background_color: (0.9, 0.1, 0.1, 1)
        on_press: app.show_lock_screen()
    Button:
        text: 'ARKA PLANA AT'
        bold: True
        on_press: app.hide_app()
"""

class MainScreen(BoxLayout): pass
class ControlPanel(BoxLayout): pass

class NKilitApp(App):
    locked = False

    def build(self):
        self.store = JsonStore('config.json')
        Window.bind(on_request_close=self.prevent_exit)
        Window.bind(on_keyboard=self.on_key_down)
        
        # 10 KAT GÜVENLİK: Her 0.5 saniyede bir ekranı zorla geri getirir
        Clock.schedule_interval(self.enforce_kiosk_mode, 0.5)
        
        Builder.load_string(kv)
        if self.store.exists('setup'):
            Clock.schedule_once(lambda dt: self.show_lock_screen(), 0.1)
            return FloatLayout()
        return MainScreen()

    def prevent_exit(self, *args):
        return self.locked

    def on_key_down(self, window, key, *args):
        if key in [27, 82, 1073742094] and self.locked:
            return True # Geri tuşu, Menü tuşu ve Uygulama Değiştiriciyi engelle
        return False

    def enforce_kiosk_mode(self, dt):
        """Ultra-Agresif Koruma Döngüsü"""
        if self.locked and platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                Intent = autoclass('android.content.Intent')
                
                # Uygulamayı tüm katmanların üzerine zorla çıkar
                intent = Intent(activity, PythonActivity)
                intent.setFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT | Intent.FLAG_ACTIVITY_SINGLE_TOP)
                activity.startActivity(intent)
            except:
                pass

    def validate_and_save(self):
        # Önceki hatayı çözen ID kontrolü
        ids = self.root.ids
        c_ad = ids.cihaz_adi.text.strip()
        a_s = ids.admin_sifre.text.strip()
        k_s = ids.kilit_sifre.text.strip()
        
        if not c_ad or not a_s or not k_s:
            ids.hata_mesaji.text = "Tüm alanları doldurmak zorunludur!"
            ids.hata_mesaji.color = (1, 0, 0, 1)
            return
            
        self.store.put('setup', cihaz_adi=c_ad, admin_sifre=a_s, kilit_sifre=k_s)
        self.show_lock_screen()

    def show_lock_screen(self, *args):
        self.locked = True
        self.root.clear_widgets()
        Window.clearcolor = (0, 0, 0, 1)
        config = self.store.get('setup')
        
        layout = FloatLayout()
        
        # Kilit Başlığı
        layout.add_widget(Label(
            text=f"SİSTEM KORUMASI: {config['cihaz_adi'].upper()}",
            pos_hint={'center_x': 0.5, 'top': 0.95},
            size_hint=(1, None), height='50dp', font_size='18sp', color=(0.5, 0.5, 0.5, 1)
        ))

        layout.add_widget(Label(
            text="ERİŞİM KISITLANDI", font_size='42sp', bold=True,
            color=(1, 0, 0, 1), pos_hint={'center_x': 0.5, 'center_y': 0.65}
        ))

        self.pass_input = TextInput(
            hint_text='KİLİT ŞİFRESİ', password=True, multiline=False,
            size_hint=(0.5, 0.08), pos_hint={'center_x': 0.5, 'center_y': 0.48},
            halign='center', font_size='22sp'
        )
        layout.add_widget(self.pass_input)

        btn = Button(
            text='CİHAZ KİLİDİNİ AÇ', size_hint=(0.5, 0.09),
            pos_hint={'center_x': 0.5, 'center_y': 0.38},
            bold=True, background_normal='', background_color=(0, 0.6, 0, 1)
        )
        btn.bind(on_press=self.check_unlock)
        layout.add_widget(btn)

        admin_btn = Button(
            text='ADMİN GİRİŞİ', size_hint=(None, None), size=("150dp", "55dp"),
            pos_hint={'right': 0.98, 'y': 0.02}, background_color=(0, 0.47, 0.84, 1), bold=True
        )
        admin_btn.bind(on_press=self.open_admin_login_popup)
        layout.add_widget(admin_btn)

        self.root.add_widget(layout)

    def check_unlock(self, instance):
        if self.pass_input.text == self.store.get('setup')['kilit_sifre']:
            self.locked = False
            self.root.clear_widgets()
            Window.clearcolor = (0.1, 0.1, 0.1, 1)
            self.root.add_widget(ControlPanel())
        else:
            self.pass_input.text = ""
            self.pass_input.hint_text = "ŞİFRE HATALI!"

    def open_admin_login_popup(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Yönetici Doğrulaması"))
        self.admin_pass_field = TextInput(password=True, multiline=False, size_hint_y=None, height='45dp', halign='center')
        content.add_widget(self.admin_pass_field)
        btn_box = BoxLayout(spacing=10, size_hint_y=None, height='50dp')
        login_btn = Button(text="ONAYLA", background_color=(0, 0.5, 1, 1), bold=True)
        login_btn.bind(on_press=self.verify_admin_popup)
        cancel_btn = Button(text="İPTAL")
        btn_box.add_widget(login_btn)
        btn_box.add_widget(cancel_btn)
        content.add_widget(btn_box)
        self.popup = Popup(title='YETKİLİ ERİŞİMİ', content=content, size_hint=(0.7, 0.4), auto_dismiss=False)
        cancel_btn.bind(on_press=self.popup.dismiss)
        self.popup.open()

    def verify_admin_popup(self, instance):
        if self.admin_pass_field.text == self.store.get('setup')['admin_sifre']:
            self.popup.dismiss()
            self.open_admin_panel()
        else:
            self.admin_pass_field.text = ""
            self.admin_pass_field.hint_text = "ŞİFRE YANLIŞ!"

    def open_admin_panel(self):
        content = BoxLayout(orientation='vertical', spacing=12, padding=15)
        btns = [
            ("KİLİT ŞİFRESİNİ GÜNCELLE", self.change_lock_pass_dialog),
            ("SİSTEMİ SIFIRLA VE ÇIK", self.factory_reset),
            ("PANELİ KAPAT", lambda x: self.admin_panel_popup.dismiss())
        ]
        for txt, func in btns:
            b = Button(text=txt, size_hint_y=None, height='55dp', bold=True)
            b.bind(on_press=func)
            content.add_widget(b)
        self.admin_panel_popup = Popup(title='YÖNETİCİ PANELİ', content=content, size_hint=(0.8, 0.6))
        self.admin_panel_popup.open()

    def factory_reset(self, instance):
        if os.path.exists('config.json'): os.remove('config.json')
        self.stop()

    def hide_app(self):
        if platform == 'android':
            from jnius import autoclass
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            activity.moveTaskToBack(True)

    def change_lock_pass_dialog(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        new_pass = TextInput(hint_text="Yeni Şifre", multiline=False, size_hint_y=None, height='45dp')
        content.add_widget(new_pass)
        save_btn = Button(text="KAYDET", background_color=(0, 0.7, 0, 1))
        def save_it(x):
            if new_pass.text:
                config = self.store.get('setup')
                self.store.put('setup', cihaz_adi=config['cihaz_adi'], admin_sifre=config['admin_sifre'], kilit_sifre=new_pass.text)
                p.dismiss()
        save_btn.bind(on_press=save_it)
        content.add_widget(save_btn)
        p = Popup(title="Şifre Değiştir", content=content, size_hint=(0.6, 0.35))
        p.open()

if __name__ == '__main__':
    NKilitApp().run()E", size_hint=(0.4, 0.12), pos_hint={'center_x': 0.5, 'center_y': 0.28}, background_color=[0.9,0.1,0.1,1], bold=True)
        b2.bind(on_press=lambda x: setattr(self.manager, 'current', 'lock'))
        
        l.add_widget(b1); l.add_widget(b2)
        self.add_widget(l)

    def hide_app(self, instance):
        try:
            from jnius import autoclass
            autoclass('org.kivy.android.PythonActivity').mActivity.moveTaskToBack(True)
        except:
            App.get_running_app().stop()

class BRTKilitApp(App):
    def build(self):
        # GERİ TUŞUNU VE KAPATMAYI ENGELLE
        Window.bind(on_request_close=self.block_exit)
        self.sm = ScreenManager(transition=FadeTransition())
        self.refresh()
        return self.sm

    def block_exit(self, *args):
        # Geri tuşuna basıldığında hiçbir şey yapma
        return True

    def refresh(self):
        self.sm.clear_widgets()
        store = JsonStore('config.json')
        self.sm.add_widget(SetupScreen(name='setup'))
        self.sm.add_widget(LockScreen(name='lock'))
        self.sm.add_widget(AdminPanel(name='admin'))
        self.sm.add_widget(UserArea(name='user_area'))
        self.sm.current = 'lock' if store.exists('settings') else 'setup'

if __name__ == '__main__':
    BRTKilitApp().run()
