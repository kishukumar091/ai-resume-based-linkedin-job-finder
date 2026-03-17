export default function SavedJobsPanel({ jobs }) {
  return (
    <section className="panel">
      <div className="section-header">
        <div>
          <p className="eyebrow">Bookmarks</p>
          <h2>Saved jobs</h2>
        </div>
      </div>
      <div className="saved-list">
        {jobs.length === 0 ? (
          <p className="empty-state">No saved jobs yet.</p>
        ) : (
          jobs.map((job) => (
            <article className="saved-card" key={job.id}>
              <div>
                <h3>{job.title}</h3>
                <p>{job.company} • {job.location}</p>
              </div>
              <div>
                <strong>{job.match_score}%</strong>
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
