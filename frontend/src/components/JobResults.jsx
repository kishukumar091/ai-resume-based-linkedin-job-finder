import { Bookmark, MapPin, ExternalLink, Building2 } from "lucide-react";

export default function JobResults({ jobs, onSaveJob, savingId }) {
  return (
    <section className="panel">
      <div className="section-header">
        <div>
          <p className="eyebrow">Matched Opportunities</p>
          <h2>Top LinkedIn-ready job recommendations</h2>
        </div>
      </div>

      <div className="job-grid">
        {jobs.map((job, index) => (
          <article className="job-card" key={`${job.title}-${job.company}-${index}`}>
            <div className="job-card-top">
              <div>
                <h3>{job.title}</h3>
                <p className="muted-line">
                  <Building2 size={16} /> {job.company}
                </p>
                <p className="muted-line">
                  <MapPin size={16} /> {job.location}
                </p>
              </div>
              <div className="score-badge">{job.match_score}% match</div>
            </div>

            <div className="chip-row">
              {job.matched_skills?.map((skill) => (
                <span className="chip chip-success" key={skill}>
                  {skill}
                </span>
              ))}
            </div>

            <div className="gap-block">
              <p>Missing skills</p>
              <div className="chip-row">
                {(job.missing_skills?.length ? job.missing_skills : ["No major gaps"]).map((skill) => (
                  <span className="chip chip-warning" key={skill}>
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            <div className="job-actions">
              <a className="secondary-button" href={job.apply_link} target="_blank" rel="noreferrer">
                <ExternalLink size={16} />
                Apply
              </a>
              <button
                className="ghost-button"
                onClick={() => onSaveJob(job)}
                disabled={savingId === `${job.title}-${job.company}`}
              >
                <Bookmark size={16} />
                {savingId === `${job.title}-${job.company}` ? "Saving..." : "Save"}
              </button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
