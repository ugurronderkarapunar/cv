import re
from PyPDF2 import PdfReader
from docx import Document

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
    # Basit bir yetenek listesi (genişletilebilir)
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
    # Örnek: "5 yıl", "3 years" gibi kalıpları bul
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

def parse_cv(file):
    filename = file.filename
    if filename.endswith('.pdf'):
        text = extract_text_from_pdf(file.file)
    elif filename.endswith('.docx'):
        text = extract_text_from_docx(file.file)
    else:
        raise ValueError("Desteklenen format: PDF veya DOCX")
    
    return {
        "skills": extract_skills(text),
        "experience_years": extract_experience_years(text),
        "education": extract_education(text),
        "full_text": text[:1000]  # İstatistik için
    }
