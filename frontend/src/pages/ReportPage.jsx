import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api";
import "../styles/ReportPage.css";

function ReportPage() {
  const { projectId } = useParams();
  const navigate = useNavigate();

  const [report, setReport] = useState(null);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingText, setLoadingText] = useState("");

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [asking, setAsking] = useState(false);

  useEffect(() => {
    loadReport();
    loadSources();

    // Start polling for live updates
    const interval = setInterval(() => {
      loadReport();
      loadSources();
    }, 3000);

    return () => clearInterval(interval);
  }, [projectId]);

  const loadReport = async () => {
    try {
      const res = await api.get(`/projects/${projectId}/report`);
      setReport(res.data);
    } catch (err) {
      console.error("No report yet");
    }
  };

  const loadSources = async () => {
    try {
      const res = await api.get(`/projects/${projectId}/sources`);
      setSources(res.data);
    } catch (err) {
      setSources([]);
    }
  };

  const expandToIEEE = async () => {
    if (loading) return;

    setLoading(true);
    setLoadingText(" Converting to IEEE format...");

    try {
      await api.post(`/projects/${projectId}/expand_to_ieee`);
      navigate(`/ieee/${projectId}`);
    } catch (err) {
      alert("Failed to convert to IEEE");
    }

    setLoading(false);
    setLoadingText("");
  };

  const splitAndViewSections = async () => {
    if (loading) return;

    setLoading(true);
    setLoadingText(" Splitting report...");

    try {
      await api.post(`/projects/${projectId}/split_report`);
      navigate(`/sections/${projectId}`);
    } catch (err) {
      alert("Failed to split report");
    }

    setLoading(false);
    setLoadingText("");
  };

  const askFromReport = async () => {
    if (!question.trim() || asking) return;

    setAsking(true);
    setAnswer("");

    try {
      const res = await api.post(
        `/projects/${projectId}/ask_from_report?question=${encodeURIComponent(question)}`
      );
      setAnswer(res.data.answer);
    } catch (err) {
      alert("Failed to get answer");
    }

    setAsking(false);
  };

  const downloadReport = (type) => {
    const url = `${api.defaults.baseURL}/projects/${projectId}/download/${type}`;
    window.open(url, "_blank");
  };

  if (!report) {
    return (
      <div className="report-container">
        <div className="loading-screen">
          <div className="spinner"></div>
          <h2> Generating your research report...</h2>
          <p>This may take a few minutes. Please wait.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="report-container">
      {/* Top Navigation */}
      <nav className="top-nav">
        <button onClick={() => navigate("/")} className="btn-back">
          ← Back to Projects
        </button>
        <h1>{report.title}</h1>
      </nav>

      {/* Action Buttons */}
      <div className="action-bar">
        <button onClick={expandToIEEE} disabled={loading} className="btn-action">
           View IEEE Format
        </button>
        <button onClick={splitAndViewSections} disabled={loading} className="btn-action">
           View Sections
        </button>
        <button onClick={() => downloadReport("word")} className="btn-action">
          ⬇ Download Word
        </button>
        <button onClick={() => downloadReport("pdf")} className="btn-action">
          ⬇ Download PDF
        </button>
      </div>

      {loading && (
        <div className="loading-banner">
          {loadingText}
        </div>
      )}

      {/* Main Content Area */}
      <div className="content-grid">
        {/* Report Content */}
        <div className="report-panel">
          <h2> Report Content</h2>
          <div className="report-content">
            <pre>{report.full_content}</pre>
          </div>
        </div>

        {/* Sidebar */}
        <div className="sidebar">
          {/* Sources */}
          <div className="sources-panel">
            <h3>🔗 Sources ({sources.length})</h3>
            <div className="sources-list">
              {sources.length === 0 ? (
                <p className="empty-text">No sources yet...</p>
              ) : (
                sources.map((source, idx) => (
                  <a
                    key={source.id}
                    href={source.url}
                    target="_blank"
                    rel="noreferrer"
                    className="source-link"
                  >
                    {idx + 1}. {source.title || source.url}
                  </a>
                ))
              )}
            </div>
          </div>

          {/* Q&A Section */}
          <div className="qa-panel">
            <h3>❓ Ask Questions</h3>
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask something about this report..."
              className="question-input"
              onKeyPress={(e) => e.key === "Enter" && askFromReport()}
            />
            <button
              onClick={askFromReport}
              disabled={asking || !question.trim()}
              className="btn-ask"
            >
              {asking ? "🤔 Thinking..." : "Ask"}
            </button>

            {answer && (
              <div className="answer-box">
                <strong>Answer:</strong>
                <p>{answer}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ReportPage;