import sys
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSystemTrayIcon, QMenu
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction
from src.gui.worker import GoldWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Çeyrek Altın")
        self.setFixedSize(300, 150)
        
        # Modern Koyu & Krem Monokrom Stil (CSS)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e24;
            }
            QLabel {
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        
        # Merkez Widget ve Düzen
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        self.title_label = QLabel("ÇEYREK ALTIN")
        self.title_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #a4a4a8; letter-spacing: 2px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Fiyat Alanı
        self.price_layout = QHBoxLayout()
        self.price_layout.setSpacing(15)
        
        # Alış ve Satış dikey blokları
        self.alis_v_layout = QVBoxLayout()
        self.alis_title = QLabel("ALIŞ")
        self.alis_title.setStyleSheet("font-size: 10px; color: #6e6e73; font-weight: bold;")
        self.alis_label = QLabel("0.00")
        self.alis_label.setStyleSheet("font-size: 20px; color: #f5f5f7; font-weight: 500;")
        self.alis_v_layout.addWidget(self.alis_title)
        self.alis_v_layout.addWidget(self.alis_label)
        
        self.satis_v_layout = QVBoxLayout()
        self.satis_title = QLabel("SATIŞ")
        self.satis_title.setStyleSheet("font-size: 10px; color: #6e6e73; font-weight: bold;")
        self.satis_label = QLabel("0.00")
        self.satis_label.setStyleSheet("font-size: 20px; color: #e2b13c; font-weight: bold;") # Altın tonu vurgu
        self.satis_v_layout.addWidget(self.satis_title)
        self.satis_v_layout.addWidget(self.satis_label)
        
        self.price_layout.addLayout(self.alis_v_layout)
        self.price_layout.addLayout(self.satis_v_layout)
        
        # Durum Çubuğu
        self.status_label = QLabel("Güncelleniyor...")
        self.status_label.setStyleSheet("font-size: 10px; color: #6e6e73;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Düzen birleştirme
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addLayout(self.price_layout)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.status_label)
        
        # ---- SYSTEM TRAY (SİSTEM TEPSİSİ) KURULUMU ----
        self.tray_icon = QSystemTrayIcon(self)
        # Not: assets/icon.ico dosyan yoksa standart bir sistem ikonu çeker:
        self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        
        # Sağ tık menüsü
        tray_menu = QMenu()
        show_action = QAction("Göster", self)
        quit_action = QAction("Çıkış", self)
        
        show_action.triggered.connect(self.showNormal)
        quit_action.triggered.connect(self.force_quit)
        
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # İkona çift tıklandığında pencereyi aç
        self.tray_icon.activated.connect(self.tray_icon_activated)

        # Worker poketini bağlama (10 saniyede bir günceller)
        self.worker = GoldWorker(interval_seconds=10)
        self.worker.data_received.connect(self.update_ui)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.start()

    def update_ui(self, data):
        self.alis_label.setText(f"{data.get('alis', 0):,.2f}")
        self.satis_label.setText(f"{data.get('satis', 0):,.2f}")
        
        from datetime import datetime
        self.status_label.setText(f"Canlı • Son Güncelleme: {datetime.now().strftime('%H:%M:%S')}")

    def handle_error(self, error_msg):
        """Worker hata aldığında tetiklenir"""
        print(f"[DEBUG] Alınan Hata: {error_msg}") # Hatayı terminale basıyoruz
        self.status_label.setText("Veri güncellenirken sorun oluştu.")

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()

    def closeEvent(self, event):
        """Kapatma butonuna basınca uygulamayı gizle, kapatma"""
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore() # Kapatma işlemini iptal et, sadece gizle

    def force_quit(self):
        """Sağ tık menüsünden tamamen çıkış için"""
        self.worker.stop()
        QSystemTrayIcon.hide(self.tray_icon)
        sys.exit()