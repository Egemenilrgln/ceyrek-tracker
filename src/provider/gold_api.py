import requests

def get_gold_data():
    """
    Bigpara üzerinden canlı çeyrek altın verilerini çeker.
    Mimarideki 'Veri Sağlayıcı (Data Provider)' katmanıdır.
    """
    # Bigpara'nın canlı borsa/altın verilerini dağıttığı güncel widget/api adresi
    url = "https://bigpara.hurriyet.com.tr/api/v1/market/data" 
    
    # Gerçek bir tarayıcı gibi davranmak için gerekli başlıklar
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://bigpara.hurriyet.com.tr/altin/ceyrek-altin-fiyati/"
    }
    
    try:
        # 5 saniyelik zaman aşımı ile isteği gönderiyoruz
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        # Bigpara API yanıt yapısı içinden çeyrek altını (Genelde SGLDC veya 'ceyrek-altin' koduyla tutulur) arıyoruz.
        # Eğer doğrudan widget API'si farklı bir şemada dönerse yedek olarak HTML kazıma (BeautifulSoup) devreye girmelidir.
        
        # Alternatif ve en garanti Scraping yöntemi (HTML parse):
        if not data or "data" not in data:
            return _fetch_via_scraping()
            
        # API verisi başarılı geldiyse süzme işlemi:
        for item in data.get("data", []):
            if item.get("code") == "SGLDC" or "ceyrek" in item.get("name", "").lower():
                return {
                    "status": "success",
                    "alis": float(item.get("bid", 0)),
                    "satis": float(item.get("ask", 0)),
                    "degisim": float(item.get("percentage_change", 0))
                }
                
        # API'de bulunamazsa doğrudan sayfayı kazımaya yönlendir
        return _fetch_via_scraping()

    except Exception as e:
        # Herhangi bir ağ hatasında yedek mekanizmayı dene
        return _fetch_via_scraping()

def _fetch_via_scraping():
    """
    API hata verirse veya yapısı değişirse yedek olarak çalışan HTML Kazıma mekanizması.
    """
    from bs4 import BeautifulSoup
    
    url = "https://bigpara.hurriyet.com.tr/altin/ceyrek-altin-fiyati/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Bigpara sayfasındaki fiyat hücrelerinin sınıfları (Kendi kaynak kodundan süzülmüştür)
        # Sitedeki <span class="value Node-Alis"> veya benzeri yapıları hedefler.
        alis_element = soup.find("span", {"class": "textAlis"}) or soup.find(class_="Node-Alis")
        satis_element = soup.find("span", {"class": "textSatis"}) or soup.find(class_="Node-Satis")
        
        if alis_element and satis_element:
            # "10.075,00" -> 10075.00 dönüşümü
            alis = float(alis_element.text.strip().replace(".", "").replace(",", "."))
            satis = float(satis_element.text.strip().replace(".", "").replace(",", "."))
            return {
                "status": "success",
                "alis": alis,
                "satis": satis,
                "degisim": 0.0
            }
    except Exception as scraping_error:
        print(f"Yedek kazıma sistemi de başarısız oldu: {scraping_error}")
        
    return {"status": "error", "message": "Veri çekilemedi."}