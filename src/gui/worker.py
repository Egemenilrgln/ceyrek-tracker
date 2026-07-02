import time
from PySide6.QtCore import QThread, Signal
from src.provider.gold_api import get_gold_data

class GoldWorker(QThread):
    """
    Altın fiyatlarını arka planda sürekli çeken iş parçacığı (Thread).
    Bu sayede veri çekilirken masaüstü arayüzü donmaz.
    """
    # Yeni veri geldiğinde arayüze tetiklenecek sinyaller
    data_received = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, interval_seconds=60):
        super().__init__()
        self.interval = interval_seconds
        self.is_running = True

    def run(self):
        """Thread başladığında çalışacak döngü"""
        while self.is_running:
            # gold_api.py içindeki fonksiyonu çağırıyoruz
            result = get_gold_data()
            
            if result and result.get("status") == "success":
                # Veriyi başarılı şekilde arayüze gönder
                self.data_received.emit(result)
            else:
                # Hata durumunu arayüze bildir
                error_msg = result.get("message", "Bilinmeyen bir hata oluştu.")
                self.error_occurred.emit(error_msg)
            
            # Belirlenen süre kadar arka planda uyu (bekle)
            time.sleep(self.interval)

    def stop(self):
        """Thread'i güvenli şekilde durdurmak için"""
        self.is_running = False
        self.quit()
        self.wait()