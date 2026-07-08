# Çeyrek Altın Takip Uygulaması (Gold Tracker)

Bu proje, anlık olarak altın (Çeyrek Altın) fiyatlarını resmi bir API üzerinden çeken ve kullanıcıya şık bir masaüstü arayüzü ile sunan bir Python uygulamasıdır. Proje, kaynak tüketimini minimumda tutmak ve kota dostu çalışmak üzere modüler bir mimariyle tasarlanmıştır.

## 🛠️ Kullanılan Teknolojiler & Kütüphaneler

* **Dil:** Python
* **Arayüz (GUI):** PySide6 / PyQt6 (Qt framework)
* **Ağ İstekleri:** Requests
* **Veri Formatı:** JSON

## 📐 Proje Mimarisi

Proje, katmanlı ve genişletilebilir bir klasör yapısına sahiptir. Bu sayede arayüz kodları ile veri çekme (backend) mantığı birbirinden tamamen izole edilmiştir:

```text
ceyrek_tracker/
│
├── src/
│   ├── gui/          # Arayüz tasarımları, pencereler ve asenkron worker'lar
│   ├── core/         # Uygulamanın ana mantığı ve yardımcı araçlar
│   └── provider/     # API entegrasyonları ve veri çekme katmanı
│
├── gold_cache.json   # Kota koruması sağlayan yerel önbellek dosyası
└── main.py           # Uygulamanın giriş noktası (Entry Point)