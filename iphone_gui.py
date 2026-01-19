import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, 
                             QWidget, QPushButton, QLabel, QHBoxLayout, QFrame)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QIcon
from iphone_core import IPhoneCore, install_requirements

class LogWorker(QThread):
    log_signal = pyqtSignal(str)
    def __init__(self, core):
        super().__init__()
        self.core = core
        self.running = True

    def run(self):
        self.core.get_live_logs(self.log_callback)

    def log_callback(self, line):
        if self.running:
            self.log_signal.emit(line)

class IPhoneManagerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # التأكد من تثبيت المتطلبات قبل بدء الواجهة
        install_requirements()
        self.core = IPhoneCore()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("iKali Pro - iPhone Manager")
        self.resize(1000, 700)
        self.setWindowIcon(QIcon("logo.png"))
        self.setStyleSheet("background-color: #1a1a1a; color: #ffffff;")

        central_widget = QWidget()
        main_layout = QVBoxLayout()

        # --- الشريط العلوي مع اللوجو ---
        header_layout = QHBoxLayout()
        self.logo_label = QLabel()
        pix = QPixmap("logo.png")
        if not pix.isNull():
            self.logo_label.setPixmap(pix.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio))
        
        header_text = QVBoxLayout()
        title = QLabel("iKali Rescue Tool")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00d2ff;")
        self.status_label = QLabel("الحالة: في انتظار توصيل USB...")
        self.status_label.setStyleSheet("color: #ffcc00;")
        
        header_text.addWidget(title)
        header_text.addWidget(self.status_label)
        
        header_layout.addWidget(self.logo_label)
        header_layout.addLayout(header_text)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # --- منطقة الأزرار ---
        btn_frame = QFrame()
        btn_layout = QHBoxLayout()
        
        btns = [
            ("🔍 فحص الاتصال", self.check_conn, "#34495e"),
            ("📋 جلب البيانات", self.show_info, "#34495e"),
            ("📜 سجل الحماية", self.start_logs, "#2980b9"),
            ("🔄 ريستارت", self.force_reboot, "#c0392b")
        ]

        for text, func, color in btns:
            b = QPushButton(text)
            b.setMinimumHeight(45)
            b.setStyleSheet(f"background-color: {color}; font-weight: bold; border-radius: 5px;")
            b.clicked.connect(func)
            btn_layout.addWidget(b)

        btn_frame.setLayout(btn_layout)
        main_layout.addWidget(btn_frame)

        # --- شاشة العرض السوداء ---
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("background-color: #000000; color: #00ff00; font-family: monospace; border: 1px solid #333;")
        main_layout.addWidget(self.console)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def check_conn(self):
        udid = self.core.get_device_list()
        if udid:
            self.status_label.setText(f"✅ متصل: {udid[:15]}...")
            self.console.append(f"[+] تم اكتشاف الجهاز بنجاح. UDID: {udid}")
        else:
            self.status_label.setText("❌ لا يوجد جهاز متصل.")

    def show_info(self):
        self.console.clear()
        self.console.append("[*] جاري استخراج بيانات الآيفون...")
        self.console.append(self.core.get_all_info())

    def start_logs(self):
        self.console.append("[*] بدء سحب الـ Syslog الحقيقي...")
        self.worker = LogWorker(self.core)
        self.worker.log_signal.connect(lambda l: self.console.append(l.strip()))
        self.worker.start()

    def force_reboot(self):
        res = self.core.restart_device()
        self.console.append(f"[!] {res}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IPhoneManagerGUI()
    window.show()
    sys.exit(app.exec())
