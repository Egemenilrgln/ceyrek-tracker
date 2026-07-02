import sys
from PySide6.QtWidgets import QMainWindow,  QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from src.gui.worker import GoldWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Çeyrek Altın Takipçisi")
        self.setFixedSize(350, 200) # Sabit pencere boyutu
        
        # Ana Widget ve Layout Kurulumu
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Arayüz Elemanları (Etiketler)
        self.title_label = QLabel("Canlı Çeyrek Altın Fiyatı")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        
        self.price_layout = QHBoxLayout()
        self.alis_label = QLabel("Alış: Yükleniyor...")
        self.alis_label.setStyleSheet("font-size: 14px; color: green; font-weight: bold;")
        self.satis_label = QLabel("Satış: Yükleniyor...")
        self.satis_label.setStyleSheet("font-size: 14px; color: red; font-weight: bold;")
        
        self.price_layout.addWidget(self.alis_label)
        self.price_layout.addWidget(self.satis_label)
        
        self.status_label = QLabel("Veri bekleniyor...")
        self.status_label.setStyleSheet("font-size: 11px; color: gray;")
        
        # Düzenleri Birleştirme
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addLayout(self.price_layout)
        self.main_layout.addWidget(self.status_label)
        
        # ---- ARKA PLAN İŞÇİSİ (WORKER) ENTEGRASYONU ----
        # Anlık güncelleme sıklığını saniye cinsinden veriyoruz (Örn: 10 saniyede bir)
        self.worker = GoldWorker(interval_seconds=10)
        
        # Worker'dan gelen sinyalleri arayüz fonksiyonlarına bağlıyoruz (Sinyal-Slot Mekanizması)
        self.worker.data_received.connect(self.update_ui)
        self.worker.error_occurred.connect(self.handle_error)
        
        # Arka plan thread'ini başlatıyoruz
        self.worker.start()

    def update_ui(self, data):
        """Worker başarıyla veri çektiğinde tetiklenir"""
        alis_fiyati = data.get("alis", 0)
        satis_fiyati = data.get("satis", 0)
        
        # Arayüzdeki metinleri güncelliyoruz
        self.alis_label.setText(f"Alış: {alis_fiyati:,.2f} TL")
        self.satis_label.setText(f"Satış: {satis_fiyati:,.2f} TL")
        
        from datetime import datetime
        su_an = datetime.now().strftime("%H:%M:%S")
        self.status_label.setText(f"Son Güncelleme: {su_an} (Canlı)")

    def handle_error(self, error_msg):
        """Worker hata aldığında tetiklenir"""
        self.status_label.setText(f"Hata: {error_msg}")

    def closeEvent(self, event):
        """Uygulama kapatılırken arka plan thread'ini de güvenle kapatır"""
        self.worker.stop()
        event.accept()