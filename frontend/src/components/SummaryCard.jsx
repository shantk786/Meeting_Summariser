function SummaryCard({ meeting, onDownload, onCopy }) {
  if (!meeting) {
    return (
      <section className="panel empty-panel">
        <h3>No meeting selected</h3>
        <p>Your processed summary will appear here after upload.</p>
      </section>
    );
  }

  return (
    <section className="panel summary-panel">
      <div className="panel-header">
        <div>
          <span className="section-tag">Executive summary</span>
          <h3>{meeting.filename}</h3>
        </div>
        <div className="panel-actions">
          <button type="button" className="ghost-button" onClick={() => onCopy(meeting)}>
            Copy summary
          </button>
          <button type="button" className="ghost-button" onClick={() => onDownload(meeting)}>
            Download
          </button>
        </div>
      </div>

      <div className="summary-text">{meeting.summary || 'Summary will appear after processing.'}</div>

      <div className="two-column-grid">
        <div>
          <h4>Key Discussion Points</h4>
          <ul className="bullet-list">
            {(meeting.key_points || []).map((point, index) => (
              <li key={`${point}-${index}`}>{point}</li>
            ))}
          </ul>
        </div>
        <div>
          <h4>Decisions</h4>
          <ul className="bullet-list">
            {(meeting.decisions || []).map((decision, index) => (
              <li key={`${decision}-${index}`}>{decision}</li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}

export default SummaryCard;
