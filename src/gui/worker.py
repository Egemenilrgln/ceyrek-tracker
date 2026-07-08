import logging
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from src.gold_api import get_gold_data

logger = logging.getLogger(__name__)

class GoldWorker(QThread):
    """
    Altın verilerini arka planda asenkron olarak çeken işçi sınıfı.
    Aylık 100 istek kotasını korumak için çok uzun aralıklarla çalışır.
    """
    # Arayüze veriyi güvenli şekilde iletmek için sinyal tanımlıyoruz
    data_received = pyqtSignal(dict)

    def __init__(self, interval_seconds: int = 28800, parent=None):
        super().__init__(parent)
        # 28800 saniye = 8 saat. Kota yayılımı için ideal süredir.
        self.interval_ms = interval_seconds * 1000  # PyQt milisaniye bekler
        self.timer = None

    def run(self):
        """Thread başladığında çalışan ana döngü altyapısı."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.fetch_data)
        
        # Uygulama ilk açıldığında hemen ilk kontrolü tetikle
        self.fetch_data()
        
        # Zamanlayıcıyı başlat (8 saatte bir tetiklenecek şekilde)
        self.timer.start(self.interval_ms)
        
        # Thread'in kendi event loop'unu başlat ve açık tut
        self.exec()

    def fetch_data(self):
        """Veri çekme işini tetikler ve sonucu sinyal ile ana pencereye gönderir."""
        logger.info("GoldWorker veri kontrolünü tetikledi...")
        
        # gold_api.py içerisindeki cache kontrollü fonksiyonu çağırıyoruz
        # Eğer 8 saat dolmadıysa bu fonksiyon doğrudan diskteki json'ı dönecek, kotaya dokunmayacaktır.
        gold_data = get_gold_data()
        
        # Sonucu ana arayüze (GUI Thread) fırlat
        self.data_received.emit(gold_data)

    def stop(self):
        """Uygulama kapatılırken zamanlayıcıyı ve thread'i güvenli şekilde sonlandırır."""
        if self.timer:
            self.timer.stop()
        self.quit()
        self.wait()