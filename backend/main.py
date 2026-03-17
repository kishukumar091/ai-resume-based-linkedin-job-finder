import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db
from job_fetcher import fetch_jobs
from job_matcher import rank_jobs, summarize_skill_gap
from resume_parser import extract_text
from skill_extractor import build_skill_profile, extract_skills, resume_improvement_suggestions


app = FastAPI(
    title="AI Resume Based LinkedIn Job Finder",
    description="Upload resumes, extract skills, rank matching jobs, and analyze skill gaps.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SavedJobRequest(BaseModel):
    title: str
    company: str
    location: str
    match_score: float
    apply_link: str
    missing_skills: List[str] = []


class ResumeAnalysisResponse(BaseModel):
    analysis_id: str
    filename: str
    extracted_skills: List[str]
    skill_profile: dict
    resume_improvement_suggestions: List[str]
    recommended_jobs: List[dict]
    top_skill_gaps: List[str]
    dashboard: dict


@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.post("/upload_resume", response_model=ResumeAnalysisResponse)
async def upload_resume(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        resume_text = extract_text(content, file.content_type, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    extracted_skills = extract_skills(resume_text)
    jobs = fetch_jobs(extracted_skills)
    ranked_jobs = rank_jobs(resume_text, extracted_skills, jobs)[:10]
    skill_gaps = summarize_skill_gap(ranked_jobs)
    improvement_suggestions = resume_improvement_suggestions(resume_text, extracted_skills)
    skill_profile = build_skill_profile(extracted_skills)

    dashboard = {
        "jobs_found": len(ranked_jobs),
        "average_match_score": round(
            sum(job["match_score"] for job in ranked_jobs) / len(ranked_jobs), 2
        )
        if ranked_jobs
        else 0,
        "top_role": ranked_jobs[0]["title"] if ranked_jobs else None,
        "daily_alert_enabled": True,
    }

    record = {
        "filename": file.filename,
        "resume_text": resume_text,
        "extracted_skills": extracted_skills,
        "skill_profile": skill_profile,
        "resume_improvement_suggestions": improvement_suggestions,
        "recommended_jobs": ranked_jobs,
        "top_skill_gaps": skill_gaps,
        "dashboard": dashboard,
        "created_at": datetime.utcnow(),
    }
    analysis_id = db.save_resume_analysis(record)

    return ResumeAnalysisResponse(
        analysis_id=analysis_id,
        filename=file.filename,
        extracted_skills=extracted_skills,
        skill_profile=skill_profile,
        resume_improvement_suggestions=improvement_suggestions,
        recommended_jobs=ranked_jobs,
        top_skill_gaps=skill_gaps,
        dashboard=dashboard,
    )


@app.get("/jobs")
def get_jobs(analysis_id: str = Query(...)):
    record = db.get_resume_analysis(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Resume analysis not found.")
    return {
        "analysis_id": analysis_id,
        "jobs": record["recommended_jobs"],
        "dashboard": record["dashboard"],
    }


@app.get("/skills-gap")
def get_skills_gap(analysis_id: str = Query(...)):
    record = db.get_resume_analysis(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Resume analysis not found.")
    return {
        "analysis_id": analysis_id,
        "top_skill_gaps": record["top_skill_gaps"],
        "resume_improvement_suggestions": record["resume_improvement_suggestions"],
    }


@app.post("/saved-jobs")
def save_job(job: SavedJobRequest):
    payload = {**job.model_dump(), "saved_at": datetime.utcnow()}
    saved_id = db.save_job(payload)
    return {"id": saved_id, "message": "Job bookmarked successfully."}


@app.get("/saved-jobs")
def get_saved_jobs():
    return {"jobs": db.get_saved_jobs()}


@app.get("/job-alerts")
def get_daily_job_alerts(analysis_id: Optional[str] = Query(default=None)):
    record = db.get_resume_analysis(analysis_id) if analysis_id else None
    jobs = record["recommended_jobs"][:5] if record else []
    return {
        "enabled": True,
        "frequency": "daily",
        "next_run_hint": "09:00 local time",
        "recommended_alert_jobs": jobs,
    }
