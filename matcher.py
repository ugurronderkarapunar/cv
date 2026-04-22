def calculate_match_score(cv_data, job):
    # Basit bir skorlama algoritması
    score = 0
    cv_skills = set(cv_data["skills"])
    # İlan başlığı ve şirket adı üzerinden basit eşleme (daha iyisi için ilan açıklaması gerek)
    job_text = (job["title"] + " " + job["company"]).lower()
    
    for skill in cv_skills:
        if skill in job_text:
            score += 10
    
    # Tecrübe bonusu (örnek: 3+ yıl -> +20)
    if cv_data["experience_years"] >= 3:
        score += 20
    elif cv_data["experience_years"] >= 1:
        score += 10
    
    # Eğitim bonusu
    if cv_data["education"] in ["Lisans", "Yüksek Lisans", "Master"]:
        score += 15
    
    return min(score, 100)  # max 100
