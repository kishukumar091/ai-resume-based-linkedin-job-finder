# API Documentation

Base URL: `http://localhost:8000`

## `POST /upload_resume`

Consumes multipart form-data with a single `file` field.

Example response:

```json
{
  "analysis_id": "689000000000000000000001",
  "filename": "resume.pdf",
  "extracted_skills": ["Python", "React", "AWS"],
  "skill_profile": {
    "backend": ["Python"],
    "frontend": ["React"],
    "data": [],
    "cloud_devops": ["AWS"]
  },
  "resume_improvement_suggestions": [
    "Highlight 2-3 projects with technology stack, architecture choices, and business results."
  ],
  "recommended_jobs": [
    {
      "title": "Python AI Engineer",
      "company": "Infosys",
      "location": "Hyderabad",
      "match_score": 88.5,
      "matched_skills": ["Python", "AWS"],
      "missing_skills": ["Machine Learning", "NLP", "Docker"],
      "apply_link": "https://www.linkedin.com/jobs/search/?keywords=python%20ai%20engineer%20infosys"
    }
  ],
  "top_skill_gaps": ["Docker", "NLP"],
  "dashboard": {
    "jobs_found": 5,
    "average_match_score": 76.4,
    "top_role": "Python AI Engineer",
    "daily_alert_enabled": true
  }
}
```

## `GET /jobs`

Query params:

- `analysis_id`: MongoDB-backed analysis identifier

## `GET /skills-gap`

Query params:

- `analysis_id`: MongoDB-backed analysis identifier

## `POST /saved-jobs`

Request body:

```json
{
  "title": "Full Stack React Node Developer",
  "company": "TCS",
  "location": "Pune",
  "match_score": 84,
  "apply_link": "https://www.linkedin.com/jobs/search/?keywords=react%20node%20developer%20tcs",
  "missing_skills": ["Docker"]
}
```

## `GET /saved-jobs`

Returns all bookmarked jobs sorted by saved date descending.

## `GET /job-alerts`

Optional query params:

- `analysis_id`

Returns daily alert metadata and a small job list for notification use cases.
