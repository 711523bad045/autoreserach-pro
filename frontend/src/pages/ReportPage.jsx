import { useEffect, useRef, useState } from "react";
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
  const [askedQuestion, setAskedQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [asking, setAsking] = useState(false);

  const [progress, setProgress] = useState(0);
  const [chatOpen, setChatOpen] = useState(false);
  const reportPanelRef = useRef(null);

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

  const handleReportScroll = () => {
    const el = reportPanelRef.current;
    if (!el) return;
    const max = el.scrollHeight - el.clientHeight;
    const pct = max > 0 ? (el.scrollTop / max) * 100 : 0;
    setProgress(Math.min(100, Math.max(0, pct)));
  };

  const expandToIEEE = async () => {
    if (loading) return;

    setLoading(true);
    setLoadingText("Converting to IEEE format...");

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
    setLoadingText("Splitting report...");

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

    setAskedQuestion(question);
    setAsking(true);
    setAnswer("");
    setQuestion("");

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
          <h2>Generating your research report...</h2>
          <p>This may take a few minutes. Please wait.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="report-container">
      {/* Reading progress */}
      <div className="progress-rail">
        <div className="progress-fill" style={{ width: `${progress}%` }}></div>
      </div>

      {/* Top Navigation */}
      <nav className="top-nav">
        <button onClick={() => navigate("/")} className="btn-back">
          ← Back
        </button>
        <div className="nav-titles">
          <span className="nav-eyebrow">Research Report</span>
          <h1>{report.title}</h1>
        </div>
      </nav>

      {/* Action Buttons */}
      <div className="action-bar">
        <div className="toolbar-group">
          <button onClick={expandToIEEE} disabled={loading} className="btn-action primary">
            View IEEE Format
          </button>
          <button onClick={splitAndViewSections} disabled={loading} className="btn-action">
            View Sections
          </button>
        </div>

        <div className="toolbar-divider"></div>

        <div className="toolbar-group">
          <span className="toolbar-label">Export</span>
          <button onClick={() => downloadReport("word")} className="btn-action">
            Word
          </button>
          <button onClick={() => downloadReport("pdf")} className="btn-action">
            PDF
          </button>
        </div>
      </div>

      {loading && <div className="loading-banner">{loadingText}</div>}

      {/* Main Content Area */}
      <div className="content-grid">
        {/* Report Content */}
        <div className="report-panel" ref={reportPanelRef} onScroll={handleReportScroll}>
          <h2>Report Content</h2>
          <div className="report-content">
            {report.full_content.split("\n").map((line, index) => {
              if (line.includes("[[IMAGE:architecture]]")) {
                return (
                  <div key={index} className="figure">
                    <img
                      src={`http://127.0.0.1:8000/generated_diagrams/${projectId}_architecture.png`}
                      alt="Architecture"
                      className="report-image"
                    />
                  </div>
                );
              }

              if (line.includes("[[IMAGE:workflow]]")) {
                return (
                  <div key={index} className="figure">
                    <img
                      src={`http://127.0.0.1:8000/generated_diagrams/${projectId}_workflow.png`}
                      alt="Workflow"
                      className="report-image"
                    />
                  </div>
                );
              }

              if (line.includes("[[IMAGE:accuracy]]")) {
                return (
                  <div key={index} className="figure">
                    <img
                      src={`http://127.0.0.1:8000/generated_diagrams/${projectId}_accuracy.png`}
                      alt="Accuracy"
                      className="report-image"
                    />
                  </div>
                );
              }

              if (line.includes("[[IMAGE:comparison]]")) {
                return (
                  <div key={index} className="figure">
                    <img
                      src={`http://127.0.0.1:8000/generated_diagrams/${projectId}_comparison.png`}
                      alt="Comparison"
                      className="report-image"
                    />
                  </div>
                );
              }

              return <p key={index}>{line}</p>;
            })}
          </div>
        </div>

        {/* Sidebar */}
        <div className="sidebar">
          {/* Sources */}
          <div className="sources-panel">
            <h3>Sources ({sources.length})</h3>
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
        </div>
      </div>

      {/* Floating Q&A launcher */}
      <button
        className="chat-fab"
        onClick={() => setChatOpen((open) => !open)}
        aria-label={chatOpen ? "Close chat" : "Ask about this report"}
      >
        <span className="chat-fab-icon">{chatOpen ? "×" : "💬"}</span>
      </button>

      {/* Floating Q&A popup */}
      {chatOpen && (
        <>
          <div className="chat-popup-backdrop" onClick={() => setChatOpen(false)}></div>
          <div className="chat-widget">
            <div className="chat-header">
              <span className="chat-avatar">AI</span>
              <div className="chat-header-text">
                <h3>Ask about this report</h3>
                <p className="chat-sub">Answers are grounded in the content above</p>
              </div>
              <button
                className="btn-chat-close"
                onClick={() => setChatOpen(false)}
                aria-label="Close chat"
              >
                ×
              </button>
            </div>

            <div className="chat-thread">
              {!askedQuestion && !asking && (
                <div className="chat-bubble assistant">
                  <p>Ask me anything about this report — findings, methods, or a specific section.</p>
                </div>
              )}

              {askedQuestion && (
                <div className="chat-bubble user">
                  <p>{askedQuestion}</p>
                </div>
              )}

              {asking && (
                <div className="chat-bubble assistant typing">
                  <span className="typing-dot"></span>
                  <span className="typing-dot"></span>
                  <span className="typing-dot"></span>
                </div>
              )}

              {answer && !asking && (
                <div className="chat-bubble assistant">
                  <p>{answer}</p>
                </div>
              )}
            </div>

            <div className="chat-input-row">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask something about this report..."
                className="question-input"
                onKeyDown={(e) => e.key === "Enter" && askFromReport()}
                autoFocus
              />
              <button
                onClick={askFromReport}
                disabled={asking || !question.trim()}
                className="btn-ask"
                aria-label="Send question"
              >
                →
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default ReportPage;