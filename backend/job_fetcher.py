import os
from typing import Dict, List
from urllib.parse import quote_plus

import requests


ROLE_TEMPLATES = [
    {
        "title": "Python Backend Developer",
        "trigger_skills": {"Python", "FastAPI", "Django", "Flask"},
        "required_skills": ["Python", "FastAPI", "SQL", "Docker", "AWS"],
        "companies": ["Infosys", "Zoho", "Paytm"],
    },
    {
        "title": "Java Spring Boot Developer",
        "trigger_skills": {"Java", "Spring Boot"},
        "required_skills": ["Java", "Spring Boot", "SQL", "Microservices", "Docker"],
        "companies": ["TCS", "Amazon", "Cognizant"],
    },
    {
        "title": "React Frontend Developer",
        "trigger_skills": {"React", "JavaScript", "TypeScript"},
        "required_skills": ["React", "JavaScript", "TypeScript", "REST API", "Git"],
        "companies": ["Swiggy", "Flipkart", "Razorpay"],
    },
    {
        "title": "Full Stack Developer",
        "trigger_skills": {"React", "Node.js", "MongoDB", "SQL"},
        "required_skills": ["React", "Node.js", "MongoDB", "REST API", "Docker"],
        "companies": ["Freshworks", "Meesho", "Capgemini"],
    },
    {
        "title": "Data Engineer",
        "trigger_skills": {"Python", "SQL", "AWS", "Data Science"},
        "required_skills": ["Python", "SQL", "AWS", "Docker", "Kubernetes"],
        "companies": ["Accenture", "Wipro", "Fractal"],
    },
    {
        "title": "Machine Learning Engineer",
        "trigger_skills": {"Machine Learning", "Data Science", "NLP", "PyTorch", "TensorFlow"},
        "required_skills": ["Python", "Machine Learning", "NLP", "Docker", "AWS"],
        "companies": ["NVIDIA", "Samsung Research", "HCLTech"],
    },
    {
        "title": "Cloud DevOps Engineer",
        "trigger_skills": {"AWS", "Azure", "GCP", "Docker", "Kubernetes", "CI/CD"},
        "required_skills": ["AWS", "Docker", "Kubernetes", "CI/CD", "Linux"],
        "companies": ["IBM", "Tech Mahindra", "LTIMindtree"],
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


def _linkedin_search_link(keywords: List[str], location: str = "India") -> str:
    query = quote_plus(" ".join(word for word in keywords if word).strip() or "software engineer")
    location_param = quote_plus(location)
    return f"https://www.linkedin.com/jobs/search/?keywords={query}&location={location_param}"


def _company_choices(template: Dict, matched_skills: List[str]) -> List[str]:
    companies = list(template.get("companies", []))
    if "AWS" in matched_skills and "Amazon" not in companies:
        companies.insert(0, "Amazon")
    if "React" in matched_skills and "Meta" not in companies:
        companies.insert(0, "Meta")
    if "Machine Learning" in matched_skills and "Google" not in companies:
        companies.insert(0, "Google")
    return companies[:3] or ["LinkedIn Jobs"]


def _unique_skills(skills: List[str]) -> List[str]:
    seen = set()
    ordered = []
    for skill in skills:
        if skill and skill not in seen:
            seen.add(skill)
            ordered.append(skill)
    return ordered


def _build_required_skills(base_skills: List[str]) -> List[str]:
    required = list(base_skills[:4])
    for skill in base_skills[:3]:
        for related in RELATED_SKILLS.get(skill, []):
            required.append(related)
    return _unique_skills(required)[:6]


def _generate_dynamic_jobs(skills: List[str], location: str) -> List[Dict]:
    normalized_skills = _unique_skills(skills)
    jobs: List[Dict] = []

    for template in ROLE_TEMPLATES:
        if template["trigger_skills"].intersection(normalized_skills):
            matched_skills = sorted(template["trigger_skills"].intersection(normalized_skills))
            required_skills = _unique_skills(template["required_skills"] + normalized_skills[:2])[:6]
            for company in _company_choices(template, matched_skills):
                jobs.append(
                    {
                        "title": template["title"],
                        "company": company,
                        "location": location,
                        "skills": required_skills,
                        "apply_link": _linkedin_search_link([template["title"], company, *matched_skills[:2]], location),
                        "description": (
                            f"Open opportunities for {template['title']} at {company} focused on "
                            f"{', '.join(required_skills[:5])}."
                        ),
                    }
                )

    if jobs:
        return jobs

    inferred_skills = normalized_skills[:5] or ["Software Engineer"]
    role_label = f"{inferred_skills[0]} Developer" if normalized_skills else "Software Engineer"
    return [
        {
            "title": role_label,
            "company": "LinkedIn Jobs",
            "location": location,
            "skills": _build_required_skills(inferred_skills),
            "apply_link": _linkedin_search_link([role_label, *inferred_skills], location),
            "description": (
                "Dynamic LinkedIn search generated from resume skills: "
                f"{', '.join(inferred_skills)}."
            ),
        }
    ]


def fetch_jobs(skills: List[str], location: str = "India") -> List[Dict]:
    api_key = os.getenv("JSEARCH_API_KEY")
    if not api_key:
        return _generate_dynamic_jobs(skills, location)

    params = {
        "query": " ".join(skills[:5]) or "software engineer",
        "page": "1",
        "num_pages": "1",
        "country": "in",
        "date_posted": "all",
    }
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }
    try:
        response = requests.get(
            "https://jsearch.p.rapidapi.com/search",
            headers=headers,
            params=params,
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return _generate_dynamic_jobs(skills, location)

    jobs: List[Dict] = []
    for item in payload.get("data", []):
        title = item.get("job_title") or "Software Engineer"
        company = item.get("employer_name") or "Unknown Company"
        description = item.get("job_description") or ""
        job_skills = [skill for skill in skills if skill.lower() in description.lower()]
        jobs.append(
            {
                "title": title,
                "company": company,
                "location": item.get("job_city") or location,
                "skills": job_skills or _build_required_skills(skills),
                "apply_link": item.get("job_apply_link") or _linkedin_search_link([title, *skills[:2]], location),
                "description": description or f"Job search result for skills: {', '.join(skills[:5])}",
            }
        )
    return jobs or _generate_dynamic_jobs(skills, location)
