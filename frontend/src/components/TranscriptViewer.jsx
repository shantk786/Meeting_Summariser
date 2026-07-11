import { getFileUrl } from '../services/api';

function TranscriptViewer({ meeting }) {
  if (!meeting) {
    return null;
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <span className="section-tag">Transcript</span>
          <h3>Speech-to-text output</h3>
        </div>
        {meeting.file_url ? (
          <audio className="audio-player" controls src={getFileUrl(meeting.file_url)} />
        ) : null}
      </div>
      <div className="transcript-box">
        {meeting.transcript || 'Transcript is not available yet.'}
      </div>
    </section>
  );
}

export default TranscriptViewer;
