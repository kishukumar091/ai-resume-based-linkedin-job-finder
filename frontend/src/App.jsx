import { useEffect, useState } from "react";
import ResumeUpload from "./components/ResumeUpload";
import JobResults from "./components/JobResults";
import SkillAnalysis from "./components/SkillAnalysis";
import SavedJobsPanel from "./pages/SavedJobsPanel";
import { fetchJobs, fetchSavedJobs, saveJob, uploadResume } from "./services/api";

export default function App() {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [savedJobs, setSavedJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filterLoading, setFilterLoading] = useState(false);
  const [savingId, setSavingId] = useState("");
  const [error, setError] = useState("");
  const [country, setCountry] = useState("us");
  const [location, setLocation] = useState("United States");
  const [preferredRole, setPreferredRole] = useState("");

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
      setCountry(data.selected_country || "us");
      setLocation(data.selected_location || "United States");
      setPreferredRole(data.selected_role || data.role_options?.[0] || "");
    } catch (uploadError) {
      setError(uploadError?.response?.data?.detail || "Failed to analyze resume.");
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshJobs = async () => {
    if (!analysis?.analysis_id) {
      return;
    }
    try {
      setFilterLoading(true);
      setError("");
      const data = await fetchJobs(analysis.analysis_id, { location, preferredRole, preferredCountry: country });
      setAnalysis((current) => ({
        ...current,
        recommended_jobs: data.jobs,
        dashboard: data.dashboard,
        top_skill_gaps: data.top_skill_gaps,
        country_options: data.country_options || current.country_options,
        role_options: data.role_options || current.role_options,
        selected_country: data.selected_country,
        selected_location: data.selected_location,
        selected_role: data.selected_role
      }));
    } catch (jobsError) {
      setError(jobsError?.response?.data?.detail || "Failed to fetch jobs for the selected filters.");
    } finally {
      setFilterLoading(false);
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
          <section className="panel filter-panel">
            <div>
              <p className="eyebrow">Job Filters</p>
              <h2>Choose your target role and location</h2>
            </div>
            <div className="filter-grid">
              <label className="field-group">
                <span>Country</span>
                <select
                  className="text-input"
                  value={country}
                  onChange={(event) => setCountry(event.target.value)}
                >
                  {(analysis.country_options?.length
                    ? analysis.country_options
                    : [{ code: "us", label: "United States" }]).map((item) => (
                    <option value={item.code} key={item.code}>
                      {item.label}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field-group">
                <span>Preferred Location</span>
                <input
                  className="text-input"
                  value={location}
                  onChange={(event) => setLocation(event.target.value)}
                  placeholder="Enter location, for example Chicago or Bangalore"
                />
              </label>
              <label className="field-group">
                <span>Preferred Job Role</span>
                <select
                  className="text-input"
                  value={preferredRole}
                  onChange={(event) => setPreferredRole(event.target.value)}
                >
                  {(analysis.role_options?.length ? analysis.role_options : ["Software Engineer"]).map((role) => (
                    <option value={role} key={role}>
                      {role}
                    </option>
                  ))}
                </select>
              </label>
              <button className="primary-button" onClick={handleRefreshJobs} disabled={filterLoading}>
                {filterLoading ? "Updating Jobs..." : "Search Jobs"}
              </button>
            </div>
          </section>
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
