monitor_code = """
from time import sleep
from jnius import autoclass
from kivy.utils import platform

def start_monitor():
    if platform != 'android':
        return

    # Android Sistem Servislerini ve Ana Aktiviteyi Bağla
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    
    while True:
        try:
            # Ana uygulama ön planda mı kontrol et, değilse zorla başlat
            activity = PythonActivity.mActivity
            if activity:
                # Uygulamayı öne getiren Intent
                intent = Intent(activity, PythonActivity)
                intent.setFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT | Intent.FLAG_ACTIVITY_NEW_TASK)
                activity.startActivity(intent)
        except Exception as e:
            print(f"Monitor Hatasi: {e}")
        
        # 1 saniyede bir kontrol et (Batarya ve performans dengesi için)
        sleep(1.0)

if __name__ == '__main__':
    start_monitor()
"""

with open("monitor.py", "w") as f:
    f.write(monitor_code)

print("monitor.py başarıyla oluşturuldu. Şimdi APK derleme adımına geçebilirsin.")