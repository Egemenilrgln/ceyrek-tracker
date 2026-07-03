import sys
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QGridLayout, QLabel, QSystemTrayIcon, QMenu
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction
from src.gui.worker import GoldWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Çeyrek Altın")
        self.setFixedSize(300, 170)
        self.last_alis = 0.0
        self.last_satis = 0.0
        
        # Arka Plan
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    x1: 0, y1: 0, 
                    x2: 1, y2: 1,
                    stop: 0 #111a24, 
                    stop: 0.5 #0b1118, 
                    stop: 1 #05080c
                );
            }
            
            QLabel {
                background: transparent;
                font-family: 'Segoe UI', 'Inter', 'Helvetica', sans-serif;
            }
        """)
        
        # Merkez Widget ve Ana Düzen
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 15, 20, 15)
        self.main_layout.setSpacing(8)
        
        # 1. Üst Başlık
        self.title_label = QLabel("ÇEYREK ALTIN")
        self.title_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #a4a4a8; letter-spacing: 2px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.title_label)
        
        # 2. İki Sütunlu Milimetrik Grid Düzeni (Alış / Satış)
        self.price_grid = QGridLayout()
        self.price_grid.setSpacing(10)
        
        # Alış Sütunu Ögeleri
        self.alis_title = QLabel("ALIŞ")
        self.alis_title.setStyleSheet("font-size: 10px; color: #6e6e73; font-weight: bold;")
        self.alis_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.alis_label = QLabel("0.00")
        self.alis_label.setStyleSheet("font-size: 20px; color: #f5f5f7; font-weight: 500;") # Gümüş
        self.alis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Satış Sütunu Ögeleri
        self.satis_title = QLabel("SATIŞ")
        self.satis_title.setStyleSheet("font-size: 10px; color: #6e6e73; font-weight: bold;")
        self.satis_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.satis_label = QLabel("0.00")
        self.satis_label.setStyleSheet("font-size: 20px; color: #dcdde1; font-weight: bold;") # Titanyum
        self.satis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Ögeleri Izgaraya Kilitleme (Widget, Satır, Sütun)
        self.price_grid.addWidget(self.alis_title, 0, 0)
        self.price_grid.addWidget(self.satis_title, 0, 1)
        self.price_grid.addWidget(self.alis_label, 1, 0)
        self.price_grid.addWidget(self.satis_label, 1, 1)
        
        self.main_layout.addLayout(self.price_grid)
        
        # 3. Günlük Değişim Etiketi
        self.degisim_label = QLabel("Günlük Değişim: %0.00 ▬")
        self.degisim_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.degisim_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #6e6e73; padding-top: 2px;")
        self.main_layout.addWidget(self.degisim_label)
        
        # 4. Alt Durum Çubuğu (Tekil ve Temiz Yerleşim)
        self.status_label = QLabel("Güncelleniyor...")
        self.status_label.setStyleSheet("font-size: 10px; color: #6e6e73; padding-top: 4px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.status_label)
        
        # ---- SYSTEM TRAY (SİSTEM TEPSİSİ) KURULUMU ----
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        
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
        
        self.tray_icon.activated.connect(self.tray_icon_activated)

        self.worker = GoldWorker(interval_seconds=10)
        self.worker.data_received.connect(self.update_ui)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.start()

    def update_ui(self, data):
        current_alis = data.get('alis', 0)
        current_satis = data.get('satis', 0)
        
        # ALIŞ fiyatı kontrolü ve renk değişimi
        if self.last_alis != 0.0:
            if current_alis > self.last_alis:
                self.alis_label.setStyleSheet("font-size: 20px; color: #4caf50; font-weight: 500;") # Artış - Yeşil
            elif current_alis < self.last_alis:
                self.alis_label.setStyleSheet("font-size: 20px; color: #f44336; font-weight: 500;") # Düşüş - Kırmızı
            else:
                self.alis_label.setStyleSheet("font-size: 20px; color: #f5f5f7; font-weight: 500;") # Nötr - Gümüş
                
        # SATIŞ fiyatı kontrolü ve renk değişimi
        if self.last_satis != 0.0:
            if current_satis > self.last_satis:
                self.satis_label.setStyleSheet("font-size: 20px; color: #4caf50; font-weight: bold;") # Artış - Yeşil
            elif current_satis < self.last_satis:
                self.satis_label.setStyleSheet("font-size: 20px; color: #f44336; font-weight: bold;") # Düşüş - Kırmızı
            else:
                self.satis_label.setStyleSheet("font-size: 20px; color: #dcdde1; font-weight: bold;") # Nötr - Titanyum
                
        # Fiyatları arayüze yazdır (Hizalamayı bozmamak için alignment'ı koru)
        self.alis_label.setText(f"{current_alis:,.2f}")
        self.satis_label.setText(f"{current_satis:,.2f}")
        self.alis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.satis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # --- GÜNLÜK DEĞİŞİM RENK VE OK MANTIĞI ---
        degisim = data.get('degisim', 0.0)
        
        if degisim > 0:
            self.degisim_label.setText(f"Günlük Değişim: +%{degisim:.2f} ▲")
            self.degisim_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #4caf50; padding-top: 2px;")
        elif degisim < 0:
            self.degisim_label.setText(f"Günlük Değişim: %{degisim:.2f} ▼")
            self.degisim_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #f44336; padding-top: 2px;")
        else:
            self.degisim_label.setText(f"Günlük Değişim: %0.00 ▬")
            self.degisim_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #6e6e73; padding-top: 2px;")
        self.degisim_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.last_alis = current_alis
        self.last_satis = current_satis
        
        from datetime import datetime
        self.status_label.setText(f"Canlı • Son Güncelleme: {datetime.now().strftime('%H:%M:%S')}")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def handle_error(self, error_msg):
        print(f"[DEBUG] Alınan Hata: {error_msg}")
        self.status_label.setText("Veri güncellenirken sorun oluştu.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()

    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()

    def force_quit(self):
        self.worker.stop()
        QSystemTrayIcon.hide(self.tray_icon)
        sys.exit()