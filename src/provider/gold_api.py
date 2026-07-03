import requests

def get_gold_data():
    """
    Truncgil Finans API'si kullanılarak canlı veri çekilir.
    API'nin anahtar isimlendirmelerindeki (Türkçe karakter, tire vb.) 
    değişikliklere karşı esnek arama mantığı içerir.
    """
    url = "https://finans.truncgil.com/today.json"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        # Gelen JSON içinde çeyrek altını dinamik olarak bul
        ceyrek_data = None
        for key, value in data.items():
            anahtar = key.lower()
            if "çeyrek" in anahtar or "ceyrek" in anahtar:
                ceyrek_data = value
                break
                
        if ceyrek_data:
            # Truncgil bazen "Alış" bazen "buying" kullanabilir, ikisine de hazır olalım
            alis_ham = ceyrek_data.get("Alış", ceyrek_data.get("buying", "0"))
            satis_ham = ceyrek_data.get("Satış", ceyrek_data.get("selling", "0"))
            
            alis_str = str(alis_ham).replace(".", "").replace(",", ".")
            satis_str = str(satis_ham).replace(".", "").replace(",", ".")
            
            return {
                "status": "success",
                "alis": float(alis_str),
                "satis": float(satis_str)
            }
            
        # Eğer yine de bulamazsa, JSON içindeki mevcut anahtarları terminale yazdırarak görelim
        mevcut_anahtarlar = list(data.keys())[:15]
        return {"status": "error", "message": f"Çeyrek anahtarı bulunamadı. Gelenler: {mevcut_anahtarlar}"}
        
    except Exception as e:
        return {"status": "error", "message": f"Bağlantı hatası: {str(e)}"}