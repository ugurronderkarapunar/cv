from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from cv_parser import parse_cv
from job_scraper import fetch_jobs
from matcher import calculate_match_score

app = FastAPI(title="CV ile İş Eşleştirici")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "jobs": None, "cv_data": None})

@app.post("/match")
async def match_cv(request: Request, cv_file: UploadFile = File(...)):
    # CV'yi parse et
    cv_data = parse_cv(cv_file)
    
    # İlanları getir
    jobs = fetch_jobs(cv_data["skills"])
    
    # Her ilan için skor hesapla
    for job in jobs:
        job["match_score"] = calculate_match_score(cv_data, job)
    
    # Skora göre sırala
    jobs.sort(key=lambda x: x["match_score"], reverse=True)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "jobs": jobs,
        "cv_data": cv_data
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
