function Navbar() {
  return (
    <header className="navbar">
      <div>
        <span className="brand-mark">AI</span>
        <div>
          <h1>Meeting Summarizer</h1>
          <p>Upload audio, transcribe it, and turn meetings into action.</p>
        </div>
      </div>
      <div className="navbar-pill">React + FastAPI + Gemini</div>
    </header>
  );
}

export default Navbar;
