import streamlit as st
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from docx import Document
import re
import time

# ---------- CV PARSER ----------
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def extract_skills(text):
    skill_keywords = [
        "python", "java", "javascript", "react", "angular", "vue", "node.js", "django", "flask",
        "sql", "postgresql", "mysql", "mongodb", "docker", "kubernetes", "aws", "azure", "git",
        "html", "css", "typescript", "c#", "c++", "php", "laravel", "spring", "selenium", "pytest"
    ]
    found = []
    text_lower = text.lower()
    for skill in skill_keywords:
        if skill in text_lower:
            found.append(skill)
    return found

def extract_experience_years(text):
    patterns = [r'(\d+)\s*yıl', r'(\d+)\s*years', r'(\d+)\s+year']
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return int(match.group(1))
    return 0

def extract_education(text):
    edu_keywords = ["lisans", "yüksek lisans", "doktora", "üniversite", "bachelor", "master", "phd"]
    for keyword in edu_keywords:
        if keyword in text.lower():
            return keyword.title()
    return "Belirtilmemiş"

def parse_cv(uploaded_file):
    if uploaded_file.name.endswith('.pdf'):
        text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith('.docx'):
        text = extract_text_from_docx(uploaded_file)
    else:
        st.error("Sadece PDF veya DOCX destekleniyor")
        return None
    return {
        "skills": extract_skills(text),
        "experience_years": extract_experience_years(text),
        "education": extract_education(text),
        "full_text": text[:1000]
    }

# ---------- JOB SCRAPER ----------
def search_kariyer_net(keywords):
    base_url = "https://www.kariyer.net/is-ilanlari"
    params = {"keywords": keywords, "location": "Türkiye"}
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = []
        for item in soup.select(".ilan-card")[:10]:
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
                    "source": "Kariyer.net"
                })
        return jobs
    except Exception as e:
        st.warning(f"Kariyer.net hatası: {e}")
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
                    "source": "Indeed"
                })
        return jobs
    except Exception as e:
        st.warning(f"Indeed hatası: {e}")
        return []

def fetch_jobs(skills):
    keyword = " ".join(skills[:3]) if skills else "yazılım"
    with st.spinner(f"'{keyword}' için ilanlar taranıyor..."):
        kariyer_jobs = search_kariyer_net(keyword)
        indeed_jobs = search_indeed_tr(keyword)
    return kariyer_jobs + indeed_jobs

# ---------- MATCHER ----------
def calculate_match_score(cv_data, job):
    score = 0
    cv_skills = set(cv_data["skills"])
    job_text = (job["title"] + " " + job["company"]).lower()
    for skill in cv_skills:
        if skill in job_text:
            score += 10
    if cv_data["experience_years"] >= 3:
        score += 20
    elif cv_data["experience_years"] >= 1:
        score += 10
    if cv_data["education"] in ["Lisans", "Yüksek Lisans", "Master"]:
        score += 15
    return min(score, 100)

# ---------- STREAMLIT UI ----------
st.set_page_config(page_title="CV ile İş Eşleştirici", page_icon="📄")
st.title("📄 CV ile İş Eşleştirici (Türkiye)")
st.markdown("CV'nizi yükleyin, size uygun iş ilanlarını Kariyer.net ve Indeed üzerinden bulalım.")

uploaded_cv = st.file_uploader("CV'nizi seçin (PDF veya DOCX)", type=["pdf", "docx"])

if uploaded_cv is not None:
    with st.spinner("CV okunuyor ve yetenekler çıkarılıyor..."):
        cv_data = parse_cv(uploaded_cv)
    
    if cv_data:
        st.subheader("📊 CV'den Çıkarılan Bilgiler")
        col1, col2, col3 = st.columns(3)
        col1.metric("Yetenek Sayısı", len(cv_data["skills"]))
        col2.metric("Tecrübe (yıl)", cv_data["experience_years"])
        col3.metric("Eğitim", cv_data["education"])
        
        with st.expander("🔧 Tespit Edilen Yetenekler"):
            st.write(", ".join(cv_data["skills"]) if cv_data["skills"] else "Hiçbiri tespit edilemedi.")
        
        # İş ilanlarını getir
        jobs = fetch_jobs(cv_data["skills"])
        
        if jobs:
            # Skor hesapla
            for job in jobs:
                job["match_score"] = calculate_match_score(cv_data, job)
            jobs.sort(key=lambda x: x["match_score"], reverse=True)
            
            st.subheader(f"🎯 Eşleşen İlanlar ({len(jobs)} adet)")
            for job in jobs:
                with st.container():
                    st.markdown(f"### {job['title']}")
                    st.write(f"**Şirket:** {job['company']}")
                    st.write(f"**Kaynak:** {job['source']}")
                    st.progress(job["match_score"] / 100, text=f"Eşleşme Skoru: %{job['match_score']}")
                    st.markdown(f"[🔗 İlana Git ve Başvur]({job['link']})")
                    st.divider()
        else:
            st.warning("Hiç ilan bulunamadı. Farklı anahtar kelimeler veya daha sonra tekrar deneyin.")
