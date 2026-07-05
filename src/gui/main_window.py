import sys
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QGridLayout, QHBoxLayout, QLabel, QPushButton, QSystemTrayIcon, QMenu
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QIcon, QAction
from src.gui.worker import GoldWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Çeyrek Altın")
        self.setFixedSize(300, 170)
        self.last_alis = 0.0
        self.last_satis = 0.0
        
        # Sürükleme (Pencereyi taşıma) için gerekli değişkenler
        self.drag_position = QPoint()
        
        # Beyaz üst barı kaldırıyoruz
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        # Köşelerin arkasında işletim sistemi çirkinliği kalmaması için şeffaflık izni
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Merkez Widget Tanımlama
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # --- PREMIUM GRADAYAN VE KOYU GECE MAVİSİ ---
        self.central_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1: 0, y1: 0, 
                    x2: 1, y2: 1,
                    stop: 0 #111a24, 
                    stop: 0.5 #0b1118, 
                    stop: 1 #05080c
                );
                border-radius: 12px;
            }
            
            QLabel {
                background: transparent;
                font-family: 'Segoe UI', 'Inter', 'Helvetica', sans-serif;
            }
            
            /* Üst Bar Butonlarının Ortak Stili */
            QPushButton.nav_btn {
                background: transparent;
                color: #6e6e73;
                font-size: 13px;
                font-weight: bold;
                border: none;
                padding: 0px;
            }
            QPushButton#minimize_btn {
                font-size: 15px;
                padding-bottom: 3px; /* Çizgiyi yukarı çekip kareyle hizalar */
            }
            
            /* Buton Hover Renkleri */
            QPushButton#minimize_btn:hover {
                color: #00d2d3; /* Küçültme için yumuşak mavi/turkuaz */
            }
            QPushButton#maximize_btn:hover {
                color: #ff9f43; /* Tam ekran için soft turuncu (Şimdilik işlevsiz) */
            }
            QPushButton#close_btn:hover {
                color: #ff4d4d; /* Kapatma için kırmızı */
            }
        """)
        
        # Ana Düzen
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(15, 12, 15, 12)
        self.main_layout.setSpacing(6)
        
        # --- ÜST BAR VE ÜÇLÜ BUTON DÜZENİ ---
        self.top_bar_layout = QHBoxLayout()
        self.top_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.top_bar_layout.setSpacing(6) # Butonların kendi arasındaki boşluk
        
        # Başlığı tam ortalamak için sol tarafa görünmez bir esneklik veriyoruz
        self.top_bar_layout.addStretch()
        
        # Pencere Küçültme Butonu (Minimize)
        self.minimize_button = QPushButton("—")
        self.minimize_button.setObjectName("minimize_btn")
        self.minimize_button.setProperty("class", "nav_btn")
        self.minimize_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.minimize_button.setFixedSize(16, 16)
        self.minimize_button.clicked.connect(self.showMinimized) # Pencereyi aşağıya indirir
        self.top_bar_layout.addWidget(self.minimize_button)
        
        # Kapatma Butonu (Close)
        self.close_button = QPushButton("✕")
        self.close_button.setObjectName("close_btn")
        self.close_button.setProperty("class", "nav_btn")
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.setFixedSize(16, 16)
        self.close_button.clicked.connect(self.close)
        self.top_bar_layout.addWidget(self.close_button)
        
        self.main_layout.addLayout(self.top_bar_layout)
        
        # 2. İki Sütunlu Milimetrik Grid Düzeni (Alış / Satış)
        self.price_grid = QGridLayout()
        self.price_grid.setSpacing(10)
        
        # Alış Sütunu Ögeleri
        self.alis_title = QLabel("ALIŞ")
        self.alis_title.setStyleSheet("font-size: 10px; color: #6e6e73; font-weight: bold;")
        self.alis_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.alis_label = QLabel("0.00")
        self.alis_label.setStyleSheet("font-size: 20px; color: #f5f5f7; font-weight: 500;")
        self.alis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Satış Sütunu Ögeleri
        self.satis_title = QLabel("SATIŞ")
        self.satis_title.setStyleSheet("font-size: 10px; color: #6e6e73; font-weight: bold;")
        self.satis_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.satis_label = QLabel("0.00")
        self.satis_label.setStyleSheet("font-size: 20px; color: #dcdde1; font-weight: bold;")
        self.satis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Ögeleri Izgaraya Kilitleme
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
        
        # 4. Alt Durum Çubuğu
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

        # Worker
        self.worker = GoldWorker(interval_seconds=10)
        self.worker.data_received.connect(self.update_ui)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.start()

    # --- PENCEREYİ SÜRÜKLEME MANTIĞI ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def update_ui(self, data):
        current_alis = data.get('alis', 0)
        current_satis = data.get('satis', 0)
        
        if self.last_alis != 0.0:
            if current_alis > self.last_alis:
                self.alis_label.setStyleSheet("font-size: 20px; color: #4caf50; font-weight: 500;")
            elif current_alis < self.last_alis:
                self.alis_label.setStyleSheet("font-size: 20px; color: #f44336; font-weight: 500;")
            else:
                self.alis_label.setStyleSheet("font-size: 20px; color: #f5f5f7; font-weight: 500;")
                
        if self.last_satis != 0.0:
            if current_satis > self.last_satis:
                self.satis_label.setStyleSheet("font-size: 20px; color: #4caf50; font-weight: bold;")
            elif current_satis < self.last_satis:
                self.satis_label.setStyleSheet("font-size: 20px; color: #f44336; font-weight: bold;")
            else:
                self.satis_label.setStyleSheet("font-size: 20px; color: #dcdde1; font-weight: bold;")
                
        self.alis_label.setText(f"{current_alis:,.2f}")
        self.satis_label.setText(f"{current_satis:,.2f}")
        self.alis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.satis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
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