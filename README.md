# AI Resume Based LinkedIn Job Finder

A production-style full stack application that analyzes resumes, extracts technical skills, matches them against relevant jobs, and returns ranked opportunities with LinkedIn application links.

## Features

- Resume upload for PDF and DOCX files
- Text extraction and skill detection using rule-based NLP with spaCy support
- AI-assisted job ranking with semantic similarity using sentence-transformers
- LinkedIn-style job recommendations with direct application links
- Skill gap analysis and resume improvement suggestions
- MySQL-backed resume analyses and saved jobs
- Dashboard metrics and daily alert endpoint
- Modern responsive React UI

## Project Structure

```text
linkedin-job-finder/
  backend/
    main.py
    resume_parser.py
    skill_extractor.py
    job_fetcher.py
    job_matcher.py
    database.py
    requirements.txt
  frontend/
    src/
      components/
      pages/
      services/
    package.json
```

## Backend Setup

1. Create a virtual environment and install dependencies:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

2. Create a MySQL database, for example:

```sql
CREATE DATABASE linkedin_job_finder;
```

3. Configure environment variables as needed:

```bash
set MYSQL_URL=mysql+pymysql://root:password@localhost:3306/linkedin_job_finder
set JSEARCH_API_KEY=your_api_key_here
set CORS_ALLOW_ORIGINS=http://localhost:5173
```

4. Start the API:

```bash
uvicorn main:app --reload
```

The backend runs at `http://localhost:8000`.

## Frontend Setup

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Optional frontend environment:

```bash
set VITE_API_BASE_URL=http://localhost:8000
```

3. Start the app:

```bash
npm run dev
```

The frontend runs at `http://localhost:5173`.

## API Documentation

FastAPI exposes Swagger docs automatically at:

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

### Endpoints

#### `POST /upload_resume`

Uploads a resume, extracts text, detects skills, fetches jobs, ranks matches, and stores the analysis.

Response fields:

- `analysis_id`
- `filename`
- `extracted_skills`
- `skill_profile`
- `resume_improvement_suggestions`
- `recommended_jobs`
- `top_skill_gaps`
- `dashboard`

#### `GET /jobs?analysis_id=<id>`

Returns ranked jobs for a previous analysis.

#### `GET /skills-gap?analysis_id=<id>`

Returns missing skills and resume improvement suggestions.

#### `POST /saved-jobs`

Bookmarks a job.

Example body:

```json
{
  "title": "Java Backend Developer",
  "company": "Amazon",
  "location": "Bangalore",
  "match_score": 92,
  "apply_link": "https://www.linkedin.com/jobs/view/3984759391",
  "missing_skills": ["Docker", "AWS"]
}
```

#### `GET /saved-jobs`

Returns all bookmarked jobs.

#### `GET /job-alerts?analysis_id=<id>`

Returns the current daily alert summary for the analyzed resume.

## Matching Algorithm

1. Extract text from the resume.
2. Identify skills from known technology phrases and spaCy-derived language chunks.
3. Query jobs using extracted skills.
4. Compute overlap score:

```text
score = matched_required_skills / total_required_skills
```

5. Compute semantic similarity between the resume text and job description using embeddings.
6. Rank jobs with:

```text
final_score = 0.7 * overlap_score + 0.3 * semantic_score
```

## Notes

- The app supports JSearch when `JSEARCH_API_KEY` is configured.
- Without an API key, it falls back to curated sample jobs with direct LinkedIn search links.
- MySQL must be running locally or reachable through `MYSQL_URL`.
- Tables are created automatically on backend startup.
- The sentence-transformers model downloads on first run.

## Future Enhancements

- User authentication
- Scheduled alert emails or WhatsApp delivery
- OpenAI or Gemini-powered resume rewriting
- LinkedIn OAuth and job application tracking
