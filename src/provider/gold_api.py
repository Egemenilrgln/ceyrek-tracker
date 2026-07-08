import json
import logging
import os
import time
import requests

logger = logging.getLogger(__name__)

# Kendi profilinden aldığın gerçek API anahtarını buraya yapıştır
API_KEY = "YOUR_COLLECTAPI_KEY_HERE"

# Fiyatların bilgisayarında saklanacağı yerel dosya adı
CACHE_FILE = "gold_cache.json"
# Kota yayma süresi: 8 saat (saniye cinsinden)
CACHE_DURATION = 28800

def get_gold_data(timeout: int = 10) -> dict:
    current_time = time.time()

    # 1. ÖNBELLEK (CACHE) KONTROLÜ: Daha önce kaydedilmiş veri var mı?
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
            
            # Verinin kaydedildiği zaman ile şu anki zamanı karşılaştırıyoruz
            timestamp = cache_data.get("timestamp", 0)
            if current_time - timestamp < CACHE_DURATION:
                logger.info("Veri internetten çekilmedi, yerel önbellekten (cache) okundu.")
                # Bilgisayarda saklanan eski veriyi doğrudan arayüze döndür
                return cache_data.get("data")
        except Exception as e:
            logger.error(f"Önbellek okunurken hata oluştu, internete yönlendiriliyor: {e}")

    # 2. GERÇEK İSTEK: Önbellek yoksa veya 8 saatten eskiyse internete çık
    logger.info("Önbellek eski veya bulunamadı. Resmi API'ye istek atılıyor...")
    url = "https://api.collectapi.com/economy/goldPrice"
    headers = {
        "content-type": "application/json",
        "authorization": API_KEY
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        json_data = response.json()
        
        if not json_data.get("success"):
            return {"status": "error", "message": "API isteği başarısız oldu."}

        ceyrek_data = None
        for item in json_data.get("result", []):
            if item.get("name") == "Çeyrek Altın":
                ceyrek_data = item
                break
                
        if not ceyrek_data:
            return {"status": "error", "message": "Çeyrek Altın bulunamadı."}

        # Arayüzün beklediği temiz veri formatı
        result_data = {
            "status": "success",
            "alis": float(ceyrek_data.get("buy", 0.0)),
            "satis": float(ceyrek_data.get("sell", 0.0)),
            "degisim": 0.0
        }

        # 3. ÖNBELLEĞE KAYDETME: Yeni çekilen veriyi zaman damgasıyla bilgisayara kaydet
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump({"timestamp": current_time, "data": result_data}, f, ensure_ascii=False, indent=4)
            logger.info("Yeni veri başarıyla yerel önbelleğe kaydedildi.")
        except Exception as e:
            logger.error(f"Veri önbelleğe yazılamadı: {e}")

        return result_data

    except requests.exceptions.RequestException as e:
        msg = f"API bağlantı hatası: {e}"
        logger.error(msg)
        return {"status": "error", "message": msg}
        
    except (ValueError, TypeError) as e:
        msg = f"Veri ayrıştırma hatası: {e}"
        logger.error(msg)
        return {"status": "error", "message": msg}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(get_gold_data())