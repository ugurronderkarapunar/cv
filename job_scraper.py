import requests
from bs4 import BeautifulSoup
import time

def search_kariyer_net(keywords, location="Türkiye"):
    # Kariyer.net arama URL'si (örnek)
    # Gerçekte daha karmaşık olabilir, bu demo amaçlı
    base_url = "https://www.kariyer.net/is-ilanlari"
    params = {
        "keywords": keywords,
        "location": location
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = []
        # Örnek: ilan kartlarını seç (gerçek selector'lar siteye göre değişir)
        for item in soup.select(".ilan-card")[:10]:  # ilk 10 ilan
            title_elem = item.select_one(".pozisyon")
            company_elem = item.select_one(".firma")
            link_elem = item.select_one("a")
            if title_elem and link_elem:
                title = title_elem.text.strip()
                company = company_elem.text.strip() if company_elem else ""
                link = "https://www.kariyer.net" + link_elem.get("href")
                jobs.append({
                    "title": title,
                    "company": company,
                    "link": link,
                    "source": "Kariyer.net",
                    "description": ""  # Detay sayfasından çekilebilir
                })
        return jobs
    except Exception as e:
        print(f"Kariyer.net hatası: {e}")
        return []

def search_indeed_tr(keywords):
    base_url = "https://tr.indeed.com/iş"
    params = {"q": keywords, "l": "Türkiye"}
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = []
        for card in soup.select(".job_seen_beacon")[:10]:
            title_elem = card.select_one("h2 a")
            company_elem = card.select_one(".companyName")
            link_elem = card.select_one("a")
            if title_elem and link_elem:
                title = title_elem.text.strip()
                company = company_elem.text.strip() if company_elem else ""
                link = "https://tr.indeed.com" + link_elem.get("href")
                jobs.append({
                    "title": title,
                    "company": company,
                    "link": link,
                    "source": "Indeed",
                    "description": ""
                })
        return jobs
    except Exception as e:
        print(f"Indeed hatası: {e}")
        return []

def fetch_jobs(skills):
    # Skills listesinden anahtar kelime oluştur (ilk 3 yetenek)
    keyword = " ".join(skills[:3]) if skills else "yazılım"
    kariyer_jobs = search_kariyer_net(keyword)
    indeed_jobs = search_indeed_tr(keyword)
    return kariyer_jobs + indeed_jobs
