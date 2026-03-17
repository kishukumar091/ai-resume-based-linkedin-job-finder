import { UploadCloud } from "lucide-react";

export default function ResumeUpload({ onFileSelected, onAnalyze, loading, fileName }) {
  return (
    <section className="panel hero-panel">
      <div>
        <p className="eyebrow">AI Resume Intelligence</p>
        <h1>AI Resume Based LinkedIn Job Finder</h1>
        <p className="hero-copy">
          Upload your resume to extract skills, generate job matches, analyze skill gaps,
          and track opportunities in one focused dashboard.
        </p>
      </div>

      <label className="upload-zone">
        <input
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={(event) => onFileSelected(event.target.files?.[0] || null)}
        />
        <UploadCloud size={34} />
        <span>{fileName || "Choose a PDF or DOCX resume"}</span>
      </label>

      <button className="primary-button" onClick={onAnalyze} disabled={loading || !fileName}>
        {loading ? "Analyzing Resume..." : "Analyze Resume"}
      </button>
    </section>
  );
}
