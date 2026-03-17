import { AlertCircle, Lightbulb, TrendingUp } from "lucide-react";

export default function SkillAnalysis({ skillGaps, suggestions, skills, dashboard }) {
  return (
    <section className="analysis-grid">
      <article className="panel stat-panel">
        <p className="eyebrow">Dashboard</p>
        <div className="stats">
          <div>
            <span>Jobs Found</span>
            <strong>{dashboard?.jobs_found ?? 0}</strong>
          </div>
          <div>
            <span>Avg Match</span>
            <strong>{dashboard?.average_match_score ?? 0}%</strong>
          </div>
          <div>
            <span>Top Role</span>
            <strong>{dashboard?.top_role ?? "N/A"}</strong>
          </div>
        </div>
      </article>

      <article className="panel">
        <div className="icon-title">
          <AlertCircle size={18} />
          <h2>Skill Gap Analysis</h2>
        </div>
        <div className="chip-row">
          {skillGaps.map((skill) => (
            <span className="chip chip-warning" key={skill}>
              {skill}
            </span>
          ))}
        </div>
      </article>

      <article className="panel">
        <div className="icon-title">
          <Lightbulb size={18} />
          <h2>Resume Improvement Suggestions</h2>
        </div>
        <ul className="insight-list">
          {suggestions.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </article>

      <article className="panel">
        <div className="icon-title">
          <TrendingUp size={18} />
          <h2>Extracted Skills</h2>
        </div>
        <div className="chip-row">
          {skills.map((skill) => (
            <span className="chip" key={skill}>
              {skill}
            </span>
          ))}
        </div>
      </article>
    </section>
  );
}
