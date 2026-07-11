function LoadingSpinner({ label = 'Processing meeting...' }) {
  return (
    <div className="loading-card">
      <div className="spinner" aria-hidden="true" />
      <div>
        <strong>{label}</strong>
        <p>The audio is being transcribed and summarized.</p>
      </div>
    </div>
  );
}

export default LoadingSpinner;
