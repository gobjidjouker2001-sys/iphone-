import subprocess
import os
import sys

def install_requirements():
    """تثبيت كافة الأدوات اللازمة للنظام ولغة بايثون"""
    print("[+] جاري التحقق من المتطلبات وتثبيتها...")
    try:
        # تثبيت أدوات النظام لـ Kali
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y", 
                        "libimobiledevice6", "libimobiledevice-utils", 
                        "ifuse", "usbmuxd", "python3-pyqt6"], check=True)
        print("[✔] تم تثبيت أدوات النظام بنجاح.")
    except Exception as e:
        print(f"[✘] خطأ أثناء التثبيت: {e}")

class IPhoneCore:
    def __init__(self):
        self.device_id = None

    def get_device_list(self):
        try:
            output = subprocess.check_output(["idevice_id", "-l"]).decode('utf-8').strip()
            if output:
                self.device_id = output.split('\n')[0]
                return self.device_id
            return None
        except:
            return None

    def get_all_info(self):
        if not self.get_device_list(): return "لا يوجد جهاز متصل أو لم يتم الضغط على 'وثوق'"
        try:
            info = subprocess.check_output(["ideviceinfo"]).decode('utf-8')
            return info
        except:
            return "خطأ: تأكد من إلغاء قفل الشاشة والضغط على 'وثوق'."

    def restart_device(self):
        if self.get_device_list():
            subprocess.run(["idevicediagnostics", "restart"])
            return "تم إرسال أمر إعادة التشغيل."
        return "الجهاز غير متصل."

    def get_live_logs(self, callback):
        """سحب السجلات الحية (مفيد جداً للشاشات المعطلة)"""
        process = subprocess.Popen(["idevicesyslog"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in process.stdout:
            callback(line)

# تشغيل التثبيت عند استدعاء الملف لأول مرة
if __name__ == "__main__":
    install_requirements()
