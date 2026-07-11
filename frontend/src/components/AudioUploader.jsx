import { useMemo, useState } from 'react';

const ACCEPTED_TYPES = ['.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.webm', '.mp4'];

function AudioUploader({ onUpload, isBusy }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const acceptedHint = useMemo(() => ACCEPTED_TYPES.join(','), []);
  const acceptedDisplay = useMemo(() => ACCEPTED_TYPES.join(', '), []);

  const handleFile = (file) => {
    if (!file) return;
    setSelectedFile(file);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (selectedFile) {
      await onUpload(selectedFile);
    }
  };

  return (
    <section className={`upload-card ${isDragging ? 'dragging' : ''}`}>
      <div className="upload-copy">
        <span className="section-tag">Step 1</span>
        <h2>Upload a meeting recording</h2>
        <p>Drop an audio file or choose one from your device. The backend stores it, transcribes it, and generates a structured summary.</p>
      </div>

      <form onSubmit={handleSubmit}>
        <label
          className="dropzone"
          onDragOver={(event) => {
            event.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(event) => {
            event.preventDefault();
            setIsDragging(false);
            handleFile(event.dataTransfer.files?.[0]);
          }}
        >
          <input
            type="file"
            accept={acceptedHint}
            onChange={(event) => handleFile(event.target.files?.[0])}
          />
          <div>
            <strong>Drag & drop your audio file here</strong>
            <p>{selectedFile ? selectedFile.name : `Supported: ${acceptedDisplay}`}</p>
          </div>
        </label>

        <div className="upload-actions">
          <button type="submit" className="primary-button" disabled={!selectedFile || isBusy}>
            {isBusy ? 'Processing...' : 'Upload and summarize'}
          </button>
          <span className="file-meta">
            {selectedFile ? `${(selectedFile.size / (1024 * 1024)).toFixed(2)} MB` : 'No file selected'}
          </span>
        </div>
      </form>
    </section>
  );
}

export default AudioUploader;
