import os
from typing import Dict, List
from urllib.parse import quote_plus

import requests


SAMPLE_JOBS = [
    {
        "title": "Java Backend Developer",
        "company": "Amazon",
        "location": "Bangalore",
        "skills": ["Java", "Spring Boot", "SQL", "AWS", "Docker", "Microservices"],
        "apply_link": "https://www.linkedin.com/jobs/search/?keywords=java%20backend%20developer%20amazon",
        "description": "Build scalable Java services, Spring Boot APIs, SQL workflows, and cloud-native deployments on AWS.",
    },
    {
        "title": "Python AI Engineer",
        "company": "Infosys",
        "location": "Hyderabad",
        "skills": ["Python", "Machine Learning", "NLP", "Docker", "AWS"],
        "apply_link": "https://www.linkedin.com/jobs/search/?keywords=python%20ai%20engineer%20infosys",
        "description": "Develop AI services, NLP pipelines, model deployment, and production-grade ML systems.",
    },
    {
        "title": "Full Stack React Node Developer",
        "company": "TCS",
        "location": "Pune",
        "skills": ["React", "Node.js", "JavaScript", "MongoDB", "REST API", "Docker"],
        "apply_link": "https://www.linkedin.com/jobs/search/?keywords=react%20node%20developer%20tcs",
        "description": "Create modern React frontends and Node.js APIs with MongoDB-backed business workflows.",
    },
    {
        "title": "Cloud Data Engineer",
        "company": "Accenture",
        "location": "Chennai",
        "skills": ["Python", "SQL", "AWS", "Docker", "Kubernetes", "Data Science"],
        "apply_link": "https://www.linkedin.com/jobs/search/?keywords=cloud%20data%20engineer%20accenture",
        "description": "Build data platforms using Python, SQL, containers, and Kubernetes on cloud infrastructure.",
    },
    {
        "title": "Senior Software Engineer - Microservices",
        "company": "Walmart Global Tech",
        "location": "Bangalore",
        "skills": ["Java", "Spring Boot", "Microservices", "Docker", "Kubernetes", "AWS"],
        "apply_link": "https://www.linkedin.com/jobs/search/?keywords=senior%20software%20engineer%20microservices%20walmart",
        "description": "Design distributed systems, secure APIs, and production microservices for large-scale platforms.",
    },
]


def _linkedin_search_link(skills: List[str]) -> str:
    query = quote_plus(" ".join(skills[:4]) if skills else "software engineer")
    return f"https://www.linkedin.com/jobs/search/?keywords={query}"


def fetch_jobs(skills: List[str], location: str = "India") -> List[Dict]:
    api_key = os.getenv("JSEARCH_API_KEY")
    if not api_key:
        return SAMPLE_JOBS

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
        return SAMPLE_JOBS

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
                "skills": job_skills or skills[:5],
                "apply_link": item.get("job_apply_link") or _linkedin_search_link([title, company]),
                "description": description,
            }
        )
    return jobs or SAMPLE_JOBS
