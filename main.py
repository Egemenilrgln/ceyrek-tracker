import sys
from PySide6.QtWidgets import QApplication
from src.gui.main_window import MainWindow

def main():
    # Qt Uygulamasını başlatıyoruz
    app = QApplication(sys.argv)
    
    # Ana penceremizi yaratıyoruz
    window = MainWindow()
    window.show()
    
    # Uygulama kapatılana kadar ana döngüyü açık tutuyoruz
    sys.exit(app.exec())

if __name__ == "__main__":
    main()