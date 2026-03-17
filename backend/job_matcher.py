from typing import Dict, List

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:  # pragma: no cover
    SentenceTransformer = None
    cosine_similarity = None


MODEL = None


def _get_model():
    global MODEL
    if MODEL is not None or SentenceTransformer is None:
        return MODEL
    try:
        MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        MODEL = None
    return MODEL


def _semantic_score(resume_text: str, job_description: str) -> float:
    model = _get_model()
    if model is None or cosine_similarity is None:
        resume_terms = set(resume_text.lower().split())
        job_terms = set(job_description.lower().split())
        union = resume_terms | job_terms
        if not union:
            return 0.0
        return len(resume_terms & job_terms) / len(union)

    embeddings = model.encode([resume_text, job_description])
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return max(float(similarity), 0.0)


def rank_jobs(resume_text: str, resume_skills: List[str], jobs: List[Dict]) -> List[Dict]:
    ranked_jobs: List[Dict] = []
    resume_skill_set = {skill.lower() for skill in resume_skills}

    for job in jobs:
        required_skills = job.get("skills", [])
        matched_skills = sorted(skill for skill in required_skills if skill.lower() in resume_skill_set)
        missing_skills = sorted(skill for skill in required_skills if skill.lower() not in resume_skill_set)

        overlap_score = len(matched_skills) / len(required_skills) if required_skills else 0.0
        semantic = _semantic_score(resume_text, job.get("description", ""))
        final_score = (0.7 * overlap_score) + (0.3 * semantic)

        ranked_jobs.append(
            {
                **job,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "match_score": round(final_score * 100, 2),
                "semantic_score": round(semantic * 100, 2),
            }
        )

    ranked_jobs.sort(key=lambda item: item["match_score"], reverse=True)
    return ranked_jobs


def summarize_skill_gap(jobs: List[Dict]) -> List[str]:
    missing = {}
    for job in jobs:
        for skill in job.get("missing_skills", []):
            missing[skill] = missing.get(skill, 0) + 1
    ranked = sorted(missing.items(), key=lambda item: item[1], reverse=True)
    return [skill for skill, _ in ranked[:10]]
