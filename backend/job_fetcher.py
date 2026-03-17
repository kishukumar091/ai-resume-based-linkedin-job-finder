import os
from typing import Dict, List

import requests


ROLE_TEMPLATES = [
    {
        "title": "Python Backend Developer",
        "trigger_skills": {"Python", "FastAPI", "Django", "Flask"},
    },
    {
        "title": "Java Spring Boot Developer",
        "trigger_skills": {"Java", "Spring Boot"},
    },
    {
        "title": "React Frontend Developer",
        "trigger_skills": {"React", "JavaScript", "TypeScript"},
    },
    {
        "title": "Full Stack Developer",
        "trigger_skills": {"React", "Node.js", "MongoDB", "SQL"},
    },
    {
        "title": "Data Engineer",
        "trigger_skills": {"Python", "SQL", "AWS", "Data Science"},
    },
    {
        "title": "Machine Learning Engineer",
        "trigger_skills": {"Machine Learning", "Data Science", "NLP", "PyTorch", "TensorFlow"},
    },
    {
        "title": "Cloud DevOps Engineer",
        "trigger_skills": {"AWS", "Azure", "GCP", "Docker", "Kubernetes", "CI/CD"},
    },
]


RELATED_SKILLS = {
    "Python": ["FastAPI", "SQL", "Docker", "AWS"],
    "Java": ["Spring Boot", "Microservices", "SQL", "Docker"],
    "React": ["JavaScript", "TypeScript", "REST API", "Git"],
    "Node.js": ["JavaScript", "MongoDB", "REST API", "Docker"],
    "Machine Learning": ["Python", "NLP", "PyTorch", "TensorFlow"],
    "Data Science": ["Python", "SQL", "Machine Learning", "AWS"],
    "AWS": ["Docker", "Kubernetes", "CI/CD", "Linux"],
}


def _normalize_location(location: str) -> str:
    if location and location.strip():
        return location
    return os.getenv("SERPAPI_LOCATION", "United States")


def _normalize_gl() -> str:
    return os.getenv("SERPAPI_GL", "us").strip().lower() or "us"


def get_country_options() -> List[Dict[str, str]]:
    return [
        {"code": "us", "label": "United States"},
        {"code": "in", "label": "India"},
        {"code": "uk", "label": "United Kingdom"},
        {"code": "ca", "label": "Canada"},
        {"code": "au", "label": "Australia"},
        {"code": "de", "label": "Germany"},
    ]


def _normalize_hl() -> str:
    return os.getenv("SERPAPI_HL", "en").strip().lower() or "en"


def _debug_enabled() -> bool:
    return os.getenv("SERPAPI_DEBUG", "true").strip().lower() in {"1", "true", "yes", "on"}


def _debug_log(message: str) -> None:
    if _debug_enabled():
        print(f"[job_fetcher] {message}")


def _unique_items(items: List[str]) -> List[str]:
    seen = set()
    ordered = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def _build_required_skills(base_skills: List[str]) -> List[str]:
    required = list(base_skills[:4])
    for skill in base_skills[:3]:
        for related in RELATED_SKILLS.get(skill, []):
            required.append(related)
    return _unique_items(required)[:6]


def _infer_role_queries(skills: List[str]) -> List[str]:
    normalized_skills = _unique_items(skills)
    queries: List[str] = []

    for template in ROLE_TEMPLATES:
        if template["trigger_skills"].intersection(normalized_skills):
            queries.append(template["title"])

    if queries:
        return queries[:4]

    if not normalized_skills:
        return ["Software Engineer"]

    lead = normalized_skills[0]
    if lead in {"Python", "Java", "Node.js"}:
        return [f"{lead} Developer"]
    if lead in {"React", "JavaScript", "TypeScript"}:
        return ["Frontend Developer"]
    if lead in {"Machine Learning", "Data Science", "NLP"}:
        return ["Machine Learning Engineer"]
    return [f"{lead} Engineer"]


def get_role_options(skills: List[str]) -> List[str]:
    return _infer_role_queries(skills)


def _serpapi_query(skills: List[str], preferred_role: str = "") -> str:
    normalized_skills = _unique_items(skills)
    role = preferred_role.strip() if preferred_role and preferred_role.strip() else _infer_role_queries(normalized_skills)[0]
    primary_skills = " ".join(normalized_skills[:3])
    return " ".join(part for part in [role, primary_skills] if part).strip()


def _extract_required_skills(description: str, resume_skills: List[str]) -> List[str]:
    description_lower = description.lower()
    matched = [skill for skill in resume_skills if skill.lower() in description_lower]
    if matched:
        return _unique_items(matched)
    return _build_required_skills(resume_skills)


def _extract_apply_link(job: Dict) -> str:
    apply_options = job.get("apply_options") or []
    for option in apply_options:
        link = option.get("link")
        if link:
            return link
    return job.get("share_link") or ""


def fetch_jobs(
    skills: List[str],
    location: str = "United States",
    preferred_role: str = "",
    preferred_country: str = "",
) -> List[Dict]:
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        _debug_log("SERPAPI_API_KEY is missing; returning no jobs.")
        return []

    normalized_location = _normalize_location(location)
    query = _serpapi_query(skills, preferred_role)
    selected_country = preferred_country.strip().lower() if preferred_country and preferred_country.strip() else _normalize_gl()
    params = {
        "engine": "google_jobs",
        "q": query,
        "location": normalized_location,
        "gl": selected_country,
        "hl": _normalize_hl(),
        "api_key": api_key,
    }

    _debug_log(
        f"Starting SerpAPI search with query='{query}', location='{normalized_location}', "
        f"gl='{params['gl']}', hl='{params['hl']}', skills={skills}"
    )

    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=20)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        _debug_log(f"SerpAPI request failed: {exc}")
        return []

    jobs_results = payload.get("jobs_results") or []
    _debug_log(f"SerpAPI returned {len(jobs_results)} raw jobs.")

    jobs: List[Dict] = []
    seen_job_ids = set()

    for item in jobs_results:
        job_id = item.get("job_id")
        if job_id and job_id in seen_job_ids:
            continue
        if job_id:
            seen_job_ids.add(job_id)

        description = item.get("description") or ""
        apply_link = _extract_apply_link(item)
        if not apply_link:
            continue

        jobs.append(
            {
                "title": item.get("title") or "Software Engineer",
                "company": item.get("company_name") or "Unknown Company",
                "location": item.get("location") or normalized_location,
                "skills": _extract_required_skills(description, skills),
                "apply_link": apply_link,
                "description": description or f"SerpAPI result for query: {query}",
                "source": "serpapi",
            }
        )

    _debug_log(f"Returning {len(jobs[:20])} SerpAPI jobs.")
    return jobs[:20]
