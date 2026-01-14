import React, { useState, useCallback } from 'react';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [uploadMessage, setUploadMessage] = useState(null);

  // Fetch stats on load
  React.useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_URL}/stats`);
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch(`${API_URL}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, top_k: 5 }),
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setError(null);
    setUploadMessage(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_URL}/ingest`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const data = await response.json();
      setUploadMessage(`${data.filename}: ${data.chunks_added} chunks indexed`);
      fetchStats();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Semantic RAG Search</h1>
        <p className="subtitle">Search your documents with AI-powered semantic understanding</p>
      </header>

      <main className="main">
        {/* Stats */}
        {stats && (
          <div className="stats">
            <span>Documents indexed: {stats.total_documents}</span>
            <span>Model: {stats.model_name}</span>
          </div>
        )}

        {/* Upload Section */}
        <section className="upload-section">
          <label className="upload-btn">
            {uploading ? 'Uploading...' : 'Upload Document'}
            <input
              type="file"
              accept=".pdf,.md,.markdown,.txt,.text"
              onChange={handleFileUpload}
              disabled={uploading}
            />
          </label>
          <span className="upload-hint">Supports PDF, Markdown, and Text files</span>
          {uploadMessage && <div className="upload-success">{uploadMessage}</div>}
        </section>

        {/* Search Form */}
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question about your documents..."
            className="search-input"
            disabled={loading}
          />
          <button type="submit" className="search-btn" disabled={loading || !query.trim()}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>

        {/* Error */}
        {error && <div className="error">{error}</div>}

        {/* Results */}
        {results && (
          <div className="results">
            {/* Generated Answer */}
            <section className="answer-section">
              <h2>Answer</h2>
              <p className="answer">{results.answer}</p>
            </section>

            {/* Source Passages */}
            <section className="passages-section">
              <h2>Source Passages</h2>
              <div className="passages">
                {results.results.map((result, index) => (
                  <div key={index} className="passage">
                    <div className="passage-header">
                      <span className="passage-source">{result.metadata.source}</span>
                      <span className="passage-score">
                        Score: {(result.score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <p className="passage-text">{result.text}</p>
                  </div>
                ))}
              </div>
            </section>
          </div>
        )}
      </main>

      <footer className="footer">
        <p>Open-source Semantic RAG Application</p>
      </footer>
    </div>
  );
}

export default App;
