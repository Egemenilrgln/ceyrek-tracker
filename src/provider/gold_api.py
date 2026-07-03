import requests

def get_gold_data():
    """
    Truncgil Finans API'si kullanılarak canlı veri çekilir.
    """
    url = "https://finans.truncgil.com/today.json"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        ceyrek_data = None
        for key, value in data.items():
            anahtar = key.lower()
            if "çeyrek" in anahtar or "ceyrek" in anahtar:
                ceyrek_data = value
                break
                
        if ceyrek_data:
            alis_ham = ceyrek_data.get("Alış", ceyrek_data.get("buying", "0"))
            satis_ham = ceyrek_data.get("Satış", ceyrek_data.get("selling", "0"))
            
            # YENİ: Değişim verisini çekiyoruz
            degisim_ham = ceyrek_data.get("Değişim", ceyrek_data.get("degisim", "0"))
            
            alis_str = str(alis_ham).replace(".", "").replace(",", ".")
            satis_str = str(satis_ham).replace(".", "").replace(",", ".")
            
            # YENİ: Değişim verisindeki % işaretini temizleyip float yapıyoruz
            degisim_str = str(degisim_ham).replace("%", "").replace(",", ".").strip()
            try:
                degisim_float = float(degisim_str)
            except ValueError:
                degisim_float = 0.0

            return {
                "status": "success",
                "alis": float(alis_str),
                "satis": float(satis_str),
                "degisim": degisim_float # YENİ EKLENDİ
            }
            
        mevcut_anahtarlar = list(data.keys())[:15]
        return {"status": "error", "message": f"Çeyrek anahtarı bulunamadı. Gelenler: {mevcut_anahtarlar}"}
        
    except Exception as e:
        return {"status": "error", "message": f"Bağlantı hatası: {str(e)}"}