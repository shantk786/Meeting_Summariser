function ActionItems({ meeting }) {
  if (!meeting) {
    return null;
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <span className="section-tag">Next steps</span>
          <h3>Action items</h3>
        </div>
      </div>
      <div className="action-list">
        {(meeting.action_items || []).map((item, index) => (
          <article key={`${item.task}-${index}`} className="action-item">
            <h4>{item.task}</h4>
            <dl>
              <div>
                <dt>Owner</dt>
                <dd>{item.owner || 'Not mentioned'}</dd>
              </div>
              <div>
                <dt>Deadline</dt>
                <dd>{item.deadline || 'Not mentioned'}</dd>
              </div>
              <div>
                <dt>Priority</dt>
                <dd>{item.priority || 'Not mentioned'}</dd>
              </div>
            </dl>
          </article>
        ))}
        {(!meeting.action_items || meeting.action_items.length === 0) ? <p className="muted">No action items were extracted.</p> : null}
      </div>
    </section>
  );
}

export default ActionItems;
