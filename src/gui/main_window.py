import sys
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QGridLayout, QHBoxLayout, QLabel, QPushButton, QSystemTrayIcon, QMenu
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QIcon, QAction
from src.gui.worker import GoldWorker
from PySide6.QtWidgets import QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Taskbar ikonu
        import sys
        import os
        if sys.platform == "win32":
            import ctypes
            myappid = 'egemen.ceyrektakip.widget.1.0' 
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            
        from PySide6.QtGui import QIcon
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(os.path.dirname(current_dir))
        icon_path = os.path.join(root_dir, "assets", "icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Çeyrek Altın")
        self.setFixedSize(300, 170)
        self.last_alis = 0.0
        self.last_satis = 0.0
        
        # Sürükleme (Pencereyi taşıma) için gerekli değişkenler
        self.drag_position = QPoint()
        
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowMinimizeButtonHint)
        # Köşelerin arkasında işletim sistemi çirkinliği kalmaması için şeffaflık izni
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Merkez Widget Tanımlama
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # PREMIUM GRADYAN VE KOYU GECE MAVİSİ
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
                font-size: 14px;
                padding-bottom: 2px; 
            }
            
            /* Buton Hover Renkleri */
            QPushButton#minimize_btn:hover {
                color: #00d2d3; /* Küçültme için yumuşak mavi/turkuaz */
            }
            QPushButton#close_btn:hover {
                color: #ff4d4d; /* Kapatma için kırmızı */
            }
        """)
        
        # Ana Düzen
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(15, 12, 15, 12)
        self.main_layout.setSpacing(6)
        
        # --- ÜST BAR VE DÜZENİ ---
        self.top_bar_layout = QHBoxLayout()
        self.top_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.top_bar_layout.setSpacing(6)
        
        # 1. YENİ: SOL ÜST KÖŞE CANLI PANELİ (Kapsayıcı Tek Bir Dış Widget)
        self.live_badge = QWidget()
        self.live_badge.setObjectName("live_badge") # Stili sadece bu dış kutuya kilitlemek için ID verdik
        
        # Sadece dış çerçeveye stil uygula, içindeki etiketlere border bulaşmasını engelle
        self.live_badge.setStyleSheet("""
            QWidget#live_badge {
                background-color: rgba(255, 59, 48, 0.06); /* %6 hafif kırmızı dolgu */
                border: 1px solid rgba(255, 59, 48, 0.45);  /* %35 şık kırmızı dış çerçeve */
                border-radius: 4px;
            }
        """)

        # Canlı Panel
        self.live_panel_layout = QHBoxLayout(self.live_badge)
        self.live_panel_layout.setSpacing(5)
        self.live_panel_layout.setContentsMargins(5, 2, 6, 2)
        
        self.live_dot = QLabel("●")
        self.live_dot.setStyleSheet("font-size: 10px; color: #ff3b30; font-weight: bold; background: transparent; border: none;")
        
        self.live_text = QLabel("CANLI")
        self.live_text.setStyleSheet("font-size: 9px; font-weight: bold; color: #ff3b30; letter-spacing: 1px; background: transparent; border: none;")
        
        self.live_panel_layout.addWidget(self.live_dot)
        self.live_panel_layout.addWidget(self.live_text)
        
        self.top_bar_layout.addWidget(self.live_badge)
        self.top_bar_layout.addStretch()
        
        # Pencere Küçültme
        self.minimize_button = QPushButton("—")
        self.minimize_button.setObjectName("minimize_btn")
        self.minimize_button.setProperty("class", "nav_btn")
        self.minimize_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.minimize_button.setFixedSize(16, 16)
        self.minimize_button.clicked.connect(self.showMinimized)
        self.top_bar_layout.addWidget(self.minimize_button)
        
        # Kapatma
        self.close_button = QPushButton("✕")
        self.close_button.setObjectName("close_btn")
        self.close_button.setProperty("class", "nav_btn")
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.setFixedSize(16, 16)
        self.close_button.clicked.connect(self.close)
        self.top_bar_layout.addWidget(self.close_button)
        
        self.main_layout.addLayout(self.top_bar_layout)
        
        # İki sütun (Alış/Satış)
        self.price_grid = QGridLayout()
        self.price_grid.setSpacing(10)
        
        # Alış Sütunu
        self.alis_title = QLabel("ALIŞ")
        self.alis_title.setStyleSheet("font-size: 10px; color: #6e6e73; font-weight: bold; padding-top: 15px; letter-spacing: 1px;")
        self.alis_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.alis_label = QLabel("0.00")
        # Satış etiketindeki stil yapısının birebir aynısını uyguluyoruz
        self.alis_label.setStyleSheet("font-size: 20px; color: #f5f5f7; font-weight: bold; padding-bottom: 10px;")
        self.alis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Satış Sütunu
        self.satis_title = QLabel("SATIŞ")
        self.satis_title.setStyleSheet("font-size: 10px; color: #6e6e73; font-weight: bold; padding-top: 15px; letter-spacing: 1px;")
        self.satis_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.satis_label = QLabel("0.00")
        self.satis_label.setStyleSheet("font-size: 20px; color: #dcdde1; font-weight: bold; padding-bottom: 10px;")
        self.satis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Izgaraya Kilitleme
        self.price_grid.addWidget(self.alis_title, 0, 0)
        self.price_grid.addWidget(self.satis_title, 0, 1)
        self.price_grid.addWidget(self.alis_label, 1, 0)
        self.price_grid.addWidget(self.satis_label, 1, 1)
        
        self.main_layout.addLayout(self.price_grid)
        
        # Günlük Değişim Etiketi
        self.degisim_label = QLabel("Günlük Değişim: %0.00 ▬")
        self.degisim_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.degisim_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #6e6e73; padding-top: 2px;")
        self.main_layout.addWidget(self.degisim_label)
        
        # Alt Durum Çubuğu
        self.status_label = QLabel("Güncelleniyor...")
        self.status_label.setStyleSheet("font-size: 10px; color: #6e6e73; padding-top: 4px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.status_label)
        
        # SİSTEM TEPSİSİ KURULUMU
        self.tray_icon = QSystemTrayIcon(self)
        import os
        from PySide6.QtGui import QIcon
        
        current_dir = os.path.dirname(os.path.abspath(__file__)) # src/gui klasörü
        root_dir = os.path.dirname(os.path.dirname(current_dir)) # Ana proje klasörü
        icon_path = os.path.join(root_dir, "assets", "icon.ico") # assets/icon.ico yolu
        
        self.tray_icon.setIcon(QIcon(icon_path)) 
        
        tray_menu = QMenu()
        show_action = QAction("Göster", self)
        
        # Onay kutulu "Ekrana Sabitle" seçeneği
        self.always_on_top_action = QAction("Ekrana Sabitle", self)
        self.always_on_top_action.setCheckable(True)
        
        quit_action = QAction("Çıkış", self)
        
        # Sinyal bağlantıları
        show_action.triggered.connect(self.showNormal)
        self.always_on_top_action.triggered.connect(self.toggle_always_on_top)
        quit_action.triggered.connect(self.force_quit)

        
        # Sistem Tepsisi Menü sıralaması
        tray_menu.addAction(show_action)
        tray_menu.addAction(self.always_on_top_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()        
        self.tray_icon.activated.connect(self.tray_icon_activated)

        self.worker = GoldWorker(interval_seconds=10)
        self.worker.data_received.connect(self.update_ui)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.start()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def toggle_always_on_top(self):
        """Sağ alttaki menüden 'Ekrana Sabitle' tıklandığında pencereyi en üstte tutar."""
        flags = self.windowFlags()
        if self.always_on_top_action.isChecked():
            self.setWindowFlags(flags | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags & ~Qt.WindowType.WindowStaysOnTopHint)
        
        # Bayrak değişiminden sonra pencerenin kaybolmaması için yeniden gösteriyoruz
        self.show()
        self.activateWindow()

    def tray_icon_activated(self, reason):
        """
        Sistem tepsisi ikonuna tıklandığında (tek veya çift tıklama), pencerenin 
        mevcut odağına göre onu ekrana getirir veya aşağıya (tepsiye) gizler.
        """
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            if self.isVisible() and self.isActiveWindow():
                self.hide()
            else:
                self.showNormal()
                self.activateWindow()

    def update_ui(self, data):
        if self.live_dot.styleSheet() == "font-size: 10px; color: #ff3b30; font-weight: bold; background: transparent; border: none;":
            self.live_dot.setStyleSheet("font-size: 10px; color: #9e231b; font-weight: bold; background: transparent; border: none;")
        else:
            self.live_dot.setStyleSheet("font-size: 10px; color: #ff3b30; font-weight: bold; background: transparent; border: none;")

        current_alis = data.get('alis', 0)
        current_satis = data.get('satis', 0)
        
        if self.last_alis != 0.0:
            if current_alis > self.last_alis:
                self.alis_label.setStyleSheet("font-size: 20px; color: #4caf50; font-weight: bold; padding-bottom: 10px;")
            elif current_alis < self.last_alis:
                self.alis_label.setStyleSheet("font-size: 20px; color: #f44336; font-weight: bold; padding-bottom: 10px;")
            else:
                self.alis_label.setStyleSheet("font-size: 20px; color: #f5f5f7; font-weight: bold; padding-bottom: 10px;")
        else:
            self.alis_label.setStyleSheet("font-size: 20px; color: #f5f5f7; font-weight: bold; padding-bottom: 10px;")
                
        if self.last_satis != 0.0:
            if current_satis > self.last_satis:
                self.satis_label.setStyleSheet("font-size: 20px; color: #4caf50; font-weight: bold; padding-bottom: 10px;")
            elif current_satis < self.last_satis:
                self.satis_label.setStyleSheet("font-size: 20px; color: #f44336; font-weight: bold; padding-bottom: 10px;")
            else:
                self.satis_label.setStyleSheet("font-size: 20px; color: #dcdde1; font-weight: bold; padding-bottom: 10px;")
        else:
            self.satis_label.setStyleSheet("font-size: 20px; color: #dcdde1; font-weight: bold; padding-bottom: 10px;")
                
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
        self.status_label.setText(f"Son Güncelleme: {datetime.now().strftime('%H:%M:%S')}")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def handle_error(self, error_msg):
        print(f"[DEBUG] Alınan Hata: {error_msg}")
        self.status_label.setText("Veri güncellenirken sorun oluştu.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()

    def force_quit(self):
        self.worker.stop()
        QSystemTrayIcon.hide(self.tray_icon)
        sys.exit()