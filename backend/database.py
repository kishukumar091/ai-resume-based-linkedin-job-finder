import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255))
    resume_text: Mapped[str] = mapped_column(Text)
    extracted_skills: Mapped[List[str]] = mapped_column(JSON)
    skill_profile: Mapped[Dict[str, List[str]]] = mapped_column(JSON)
    resume_improvement_suggestions: Mapped[List[str]] = mapped_column(JSON)
    recommended_jobs: Mapped[List[Dict[str, Any]]] = mapped_column(JSON)
    top_skill_gaps: Mapped[List[str]] = mapped_column(JSON)
    dashboard: Mapped[Dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255))
    company: Mapped[str] = mapped_column(String(255))
    location: Mapped[str] = mapped_column(String(255))
    match_score: Mapped[float] = mapped_column(Float)
    apply_link: Mapped[str] = mapped_column(Text)
    missing_skills: Mapped[List[str]] = mapped_column(JSON)
    saved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Database:
    def __init__(self) -> None:
        mysql_url = os.getenv(
            "MYSQL_URL",
            "mysql+pymysql://root:password@localhost:3306/linkedin_job_finder",
        )
        self._engine = create_engine(mysql_url, pool_pre_ping=True)
        self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)
        self._resume_fallback: Dict[str, Dict[str, Any]] = {}
        self._saved_jobs_fallback: Dict[str, Dict[str, Any]] = {}
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        try:
            Base.metadata.create_all(self._engine)
        except SQLAlchemyError:
            # Keep the app usable in local/dev mode even when MySQL is unavailable.
            pass

    def save_resume_analysis(self, payload: Dict[str, Any]) -> str:
        record = ResumeAnalysis(
            filename=payload["filename"],
            resume_text=payload["resume_text"],
            extracted_skills=payload["extracted_skills"],
            skill_profile=payload["skill_profile"],
            resume_improvement_suggestions=payload["resume_improvement_suggestions"],
            recommended_jobs=payload["recommended_jobs"],
            top_skill_gaps=payload["top_skill_gaps"],
            dashboard=payload["dashboard"],
            created_at=payload.get("created_at", datetime.utcnow()),
        )

        try:
            with self._session_factory() as session:
                session.add(record)
                session.commit()
                session.refresh(record)
                return str(record.id)
        except SQLAlchemyError:
            identifier = uuid4().hex
            self._resume_fallback[identifier] = {"id": identifier, **payload}
            return identifier

    def get_resume_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        if analysis_id in self._resume_fallback:
            return self._resume_fallback[analysis_id]

        try:
            record_id = int(analysis_id)
        except ValueError:
            return None

        try:
            with self._session_factory() as session:
                record = session.get(ResumeAnalysis, record_id)
                if not record:
                    return None
                return {
                    "id": str(record.id),
                    "filename": record.filename,
                    "resume_text": record.resume_text,
                    "extracted_skills": record.extracted_skills,
                    "skill_profile": record.skill_profile,
                    "resume_improvement_suggestions": record.resume_improvement_suggestions,
                    "recommended_jobs": record.recommended_jobs,
                    "top_skill_gaps": record.top_skill_gaps,
                    "dashboard": record.dashboard,
                    "created_at": record.created_at,
                }
        except SQLAlchemyError:
            return None

    def save_job(self, payload: Dict[str, Any]) -> str:
        record = SavedJob(
            title=payload["title"],
            company=payload["company"],
            location=payload["location"],
            match_score=payload["match_score"],
            apply_link=payload["apply_link"],
            missing_skills=payload.get("missing_skills", []),
            saved_at=payload.get("saved_at", datetime.utcnow()),
        )

        try:
            with self._session_factory() as session:
                session.add(record)
                session.commit()
                session.refresh(record)
                return str(record.id)
        except SQLAlchemyError:
            identifier = uuid4().hex
            self._saved_jobs_fallback[identifier] = {"id": identifier, **payload}
            return identifier

    def get_saved_jobs(self) -> List[Dict[str, Any]]:
        try:
            with self._session_factory() as session:
                records = session.query(SavedJob).order_by(SavedJob.saved_at.desc()).all()
                return [
                    {
                        "id": str(record.id),
                        "title": record.title,
                        "company": record.company,
                        "location": record.location,
                        "match_score": record.match_score,
                        "apply_link": record.apply_link,
                        "missing_skills": record.missing_skills,
                        "saved_at": record.saved_at,
                    }
                    for record in records
                ]
        except SQLAlchemyError:
            return sorted(
                self._saved_jobs_fallback.values(),
                key=lambda item: item.get("saved_at", datetime.min),
                reverse=True,
            )


db = Database()
