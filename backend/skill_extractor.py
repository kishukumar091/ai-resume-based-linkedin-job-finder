import os
import re
from typing import Dict, List, Set

import spacy


DEFAULT_SKILLS = {
    "java",
    "python",
    "react",
    "node.js",
    "node",
    "spring boot",
    "sql",
    "mongodb",
    "aws",
    "docker",
    "kubernetes",
    "machine learning",
    "data science",
    "fastapi",
    "django",
    "flask",
    "typescript",
    "javascript",
    "rest api",
    "microservices",
    "redis",
    "postgresql",
    "mysql",
    "azure",
    "gcp",
    "tensorflow",
    "pytorch",
    "nlp",
    "langchain",
    "git",
    "ci/cd",
}


SKILL_ALIASES = {
    "node": "Node.js",
    "node.js": "Node.js",
    "react": "React",
    "java": "Java",
    "python": "Python",
    "spring boot": "Spring Boot",
    "sql": "SQL",
    "mongodb": "MongoDB",
    "aws": "AWS",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "machine learning": "Machine Learning",
    "data science": "Data Science",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "typescript": "TypeScript",
    "javascript": "JavaScript",
    "rest api": "REST API",
    "microservices": "Microservices",
    "redis": "Redis",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "azure": "Azure",
    "gcp": "GCP",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "nlp": "NLP",
    "langchain": "LangChain",
    "git": "Git",
    "ci/cd": "CI/CD",
}


def _load_nlp():
    model_name = os.getenv("SPACY_MODEL", "en_core_web_sm")
    try:
        return spacy.load(model_name)
    except OSError:
        return spacy.blank("en")


NLP = _load_nlp()


def extract_skills(text: str) -> List[str]:
    lowered = text.lower()
    discovered: Set[str] = set()
    for skill in DEFAULT_SKILLS:
        pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"
        if re.search(pattern, lowered):
            discovered.add(SKILL_ALIASES.get(skill, skill.title()))

    noun_chunks = []
    doc = NLP(text)
    if doc.has_annotation("DEP"):
        noun_chunks = [chunk.text.lower().strip() for chunk in doc.noun_chunks]

    for chunk in noun_chunks:
        for skill in DEFAULT_SKILLS:
            if skill in chunk:
                discovered.add(SKILL_ALIASES.get(skill, skill.title()))

    return sorted(discovered)


def resume_improvement_suggestions(text: str, skills: List[str]) -> List[str]:
    suggestions: List[str] = []
    lowered = text.lower()
    if "experience" not in lowered:
        suggestions.append("Add a dedicated experience section with measurable impact and delivery outcomes.")
    if "project" not in lowered:
        suggestions.append("Highlight 2-3 projects with technology stack, architecture choices, and business results.")
    if len(skills) < 6:
        suggestions.append("Mention more concrete technical skills and tools to improve matching accuracy.")
    if "%" not in text and "improved" not in lowered:
        suggestions.append("Include quantified achievements such as latency reduction, revenue impact, or automation savings.")
    if "linkedin.com" not in lowered:
        suggestions.append("Add a LinkedIn profile URL so recruiters can validate your profile quickly.")
    return suggestions or [
        "Your resume already has solid technical coverage. Tighten bullet points with outcome-driven metrics for even better ranking."
    ]


def build_skill_profile(skills: List[str]) -> Dict[str, List[str]]:
    grouped = {
        "backend": [skill for skill in skills if skill in {"Java", "Python", "Node.js", "Spring Boot", "FastAPI", "Django", "Flask"}],
        "frontend": [skill for skill in skills if skill in {"React", "JavaScript", "TypeScript"}],
        "data": [skill for skill in skills if skill in {"SQL", "MongoDB", "PostgreSQL", "MySQL", "Machine Learning", "Data Science", "NLP"}],
        "cloud_devops": [skill for skill in skills if skill in {"AWS", "Azure", "GCP", "Docker", "Kubernetes", "CI/CD"}],
    }
    return grouped
