import { useEffect, useState } from "react";
import ResumeUpload from "./components/ResumeUpload";
import JobResults from "./components/JobResults";
import SkillAnalysis from "./components/SkillAnalysis";
import SavedJobsPanel from "./pages/SavedJobsPanel";
import { fetchSavedJobs, saveJob, uploadResume } from "./services/api";

export default function App() {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [savedJobs, setSavedJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [savingId, setSavingId] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    fetchSavedJobs()
      .then(setSavedJobs)
      .catch(() => setSavedJobs([]));
  }, []);

  const handleAnalyze = async () => {
    if (!file) {
      return;
    }
    try {
      setLoading(true);
      setError("");
      const data = await uploadResume(file);
      setAnalysis(data);
    } catch (uploadError) {
      setError(uploadError?.response?.data?.detail || "Failed to analyze resume.");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveJob = async (job) => {
    const identifier = `${job.title}-${job.company}`;
    try {
      setSavingId(identifier);
      await saveJob(job);
      const jobs = await fetchSavedJobs();
      setSavedJobs(jobs);
    } finally {
      setSavingId("");
    }
  };

  return (
    <main className="app-shell">
      <div className="background-orb orb-one" />
      <div className="background-orb orb-two" />

      <section className="top-grid">
        <ResumeUpload
          onFileSelected={setFile}
          onAnalyze={handleAnalyze}
          loading={loading}
          fileName={file?.name}
        />
        <SavedJobsPanel jobs={savedJobs} />
      </section>

      {error ? <div className="error-banner">{error}</div> : null}

      {analysis ? (
        <>
          <SkillAnalysis
            skillGaps={analysis.top_skill_gaps}
            suggestions={analysis.resume_improvement_suggestions}
            skills={analysis.extracted_skills}
            dashboard={analysis.dashboard}
          />
          <JobResults jobs={analysis.recommended_jobs} onSaveJob={handleSaveJob} savingId={savingId} />
        </>
      ) : (
        <section className="panel placeholder-panel">
          <p className="eyebrow">How It Works</p>
          <h2>Upload a resume to unlock AI-powered job discovery.</h2>
          <p>
            The system parses resume text, extracts role-specific skills, performs semantic job matching,
            highlights missing skills, and returns direct LinkedIn application links.
          </p>
        </section>
      )}
    </main>
  );
}
