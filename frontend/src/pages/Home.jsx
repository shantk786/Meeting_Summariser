import { useEffect, useMemo, useState } from 'react';

import ActionItems from '../components/ActionItems';
import AudioUploader from '../components/AudioUploader';
import LoadingSpinner from '../components/LoadingSpinner';
import SummaryCard from '../components/SummaryCard';
import TranscriptViewer from '../components/TranscriptViewer';
import { deleteMeeting, fetchMeeting, fetchMeetings, getFileUrl, processMeeting, uploadAudio } from '../services/api';

function Home() {
  const [meetings, setMeetings] = useState([]);
  const [selectedMeetingId, setSelectedMeetingId] = useState('');
  const [selectedMeeting, setSelectedMeeting] = useState(null);
  const [query, setQuery] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  const [error, setError] = useState('');
  const [isBusy, setIsBusy] = useState(false);

  const selectedMeetingFromList = useMemo(
    () => meetings.find((meeting) => meeting.id === selectedMeetingId) || selectedMeeting,
    [meetings, selectedMeetingId, selectedMeeting],
  );

  const loadMeetings = async (search = query) => {
    const data = await fetchMeetings(search);
    setMeetings(data.items || []);
    if (!selectedMeetingId && data.items?.length) {
      setSelectedMeetingId(data.items[0].id);
    }
  };

  const loadMeeting = async (meetingId) => {
    const data = await fetchMeeting(meetingId);
    setSelectedMeeting(data);
    setSelectedMeetingId(meetingId);
  };

  useEffect(() => {
    loadMeetings().catch((loadError) => setError(loadError?.response?.data?.detail || loadError.message));
  }, []);

  useEffect(() => {
    if (selectedMeetingId) {
      loadMeeting(selectedMeetingId).catch((loadError) => setError(loadError?.response?.data?.detail || loadError.message));
    }
  }, [selectedMeetingId]);

  const handleUpload = async (file) => {
    setError('');
    setStatusMessage('Uploading file...');
    setIsBusy(true);
    try {
      const uploadResponse = await uploadAudio(file);
      setSelectedMeetingId(uploadResponse.meeting.id);
      setStatusMessage('Transcribing audio and generating insights...');
      await processMeeting(uploadResponse.meeting.id);
      await loadMeetings(query);
      const processed = await fetchMeeting(uploadResponse.meeting.id);
      setSelectedMeeting(processed);
      setStatusMessage('Meeting processed successfully.');
    } catch (uploadError) {
      setError(uploadError?.response?.data?.detail || uploadError.message || 'Something went wrong.');
      setStatusMessage('');
    } finally {
      setIsBusy(false);
    }
  };

  const handleSearch = async (event) => {
    const value = event.target.value;
    setQuery(value);
    try {
      await loadMeetings(value);
    } catch (searchError) {
      setError(searchError?.response?.data?.detail || searchError.message);
    }
  };

  const handleDelete = async (meetingId) => {
    setError('');
    try {
      await deleteMeeting(meetingId);
      const updated = meetings.filter((meeting) => meeting.id !== meetingId);
      setMeetings(updated);
      const nextSelected = updated[0] || null;
      setSelectedMeetingId(nextSelected?.id || '');
      setSelectedMeeting(nextSelected || null);
    } catch (deleteError) {
      setError(deleteError?.response?.data?.detail || deleteError.message);
    }
  };

  const handleRowDelete = async (event, meetingId) => {
    event.stopPropagation();
    await handleDelete(meetingId);
  };

  const handleDownload = (meeting) => {
    const payload = {
      filename: meeting.filename,
      summary: meeting.summary,
      key_points: meeting.key_points || [],
      decisions: meeting.decisions || [],
      action_items: meeting.action_items || [],
      transcript: meeting.transcript || '',
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `${meeting.filename.replace(/\.[^.]+$/, '') || 'meeting'}-summary.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  const handleCopy = async (meeting) => {
    const text = `${meeting.filename}\n\n${meeting.summary}\n\nKey Points:\n${(meeting.key_points || []).map((item) => `- ${item}`).join('\n')}\n\nDecisions:\n${(meeting.decisions || []).map((item) => `- ${item}`).join('\n')}\n\nAction Items:\n${(meeting.action_items || []).map((item) => `- ${item.task} | Owner: ${item.owner || 'Not mentioned'} | Deadline: ${item.deadline || 'Not mentioned'} | Priority: ${item.priority || 'Not mentioned'}`).join('\n')}`;
    await navigator.clipboard.writeText(text);
    setStatusMessage('Summary copied to clipboard.');
  };

  return (
    <div className="page-container">
      <section className="hero">
        <div className="hero-copy">
          <span className="section-tag">Production-ready AI workflow</span>
          <h2>Turn meeting recordings into summaries, decisions, and action items.</h2>
          <p>
            Built with React, FastAPI, Whisper transcription, and Gemini 2.5 Flash. Upload a recording, let the backend process it, and review the transcript and insight dashboard in one place.
          </p>
        </div>
        <div className="status-stack">
          <div className="status-card">
            <strong>Upload</strong>
            <span>Store audio securely</span>
          </div>
          <div className="status-card">
            <strong>Transcribe</strong>
            <span>Convert speech to text</span>
          </div>
          <div className="status-card">
            <strong>Summarize</strong>
            <span>Generate structured JSON</span>
          </div>
        </div>
      </section>

      <AudioUploader onUpload={handleUpload} isBusy={isBusy} />

      {statusMessage ? <div className="info-banner">{statusMessage}</div> : null}
      {error ? <div className="error-banner">{error}</div> : null}

      {isBusy ? <LoadingSpinner /> : null}

      <section className="workspace-grid">
        <aside className="panel history-panel">
          <div className="panel-header">
            <div>
              <span className="section-tag">History</span>
              <h3>Processed meetings</h3>
            </div>
          </div>
          <input
            className="search-input"
            placeholder="Search meeting filenames"
            value={query}
            onChange={handleSearch}
          />
          <div className="meeting-list">
            {meetings.length === 0 ? <p className="muted">No meetings yet. Upload a recording to start.</p> : null}
            {meetings.map((meeting) => (
              <button
                type="button"
                key={meeting.id}
                className={`meeting-row ${selectedMeetingFromList?.id === meeting.id ? 'active' : ''}`}
                onClick={() => setSelectedMeetingId(meeting.id)}
              >
                <div>
                  <strong>{meeting.filename}</strong>
                  <span>{new Date(meeting.created_at).toLocaleString()}</span>
                </div>
                <span className={`status-badge ${meeting.status}`}>{meeting.status}</span>
                <span className="delete-link" onClick={(event) => handleRowDelete(event, meeting.id)}>Delete</span>
              </button>
            ))}
          </div>
        </aside>

        <div className="details-column">
          <SummaryCard meeting={selectedMeetingFromList} onDownload={handleDownload} onCopy={handleCopy} />
          <TranscriptViewer meeting={selectedMeetingFromList} />
          <ActionItems meeting={selectedMeetingFromList} />
          {selectedMeetingFromList?.file_url ? (
            <section className="panel">
              <div className="panel-header">
                <div>
                  <span className="section-tag">Audio</span>
                  <h3>Original recording</h3>
                </div>
              </div>
              <audio className="audio-player wide" controls src={getFileUrl(selectedMeetingFromList.file_url)} />
            </section>
          ) : null}
        </div>
      </section>
    </div>
  );
}

export default Home;
