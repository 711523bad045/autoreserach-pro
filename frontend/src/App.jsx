import { useEffect, useState } from "react";
import { api } from "./api";

function App() {
  const [projects, setProjects] = useState([]);
  const [newTitle, setNewTitle] = useState("");
  const [selectedProject, setSelectedProject] = useState(null);

  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingText, setLoadingText] = useState("");

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [asking, setAsking] = useState(false);

  const [sections, setSections] = useState([]);
  const [showSections, setShowSections] = useState(false);

  const [sources, setSources] = useState([]);
  const [ieeeReport, setIeeeReport] = useState(null);

  // ------------------------
  // Load projects
  // ------------------------
  const loadProjects = async () => {
    const res = await api.get("/projects/");
    setProjects(res.data);
  };

  useEffect(() => {
    loadProjects();
  }, []);

  // ------------------------
  // Load sources from DB
  // ------------------------
  const loadSources = async (projectId) => {
    try {
      const res = await api.get(`/projects/${projectId}/sources`);
      setSources(res.data);
    } catch (err) {
      console.error("Failed to load sources");
      setSources([]);
    }
  };
  const loadIEEEReport = async () => {
  if (!selectedProject) return;

  try {
    const res = await api.get(`/projects/${selectedProject.id}/ieee`);
    setIeeeReport(res.data);
  } catch (err) {
    alert("No IEEE report found. Generate it first.");
  }
};

  // ------------------------
  // Create project
  // ------------------------
  const createProject = async () => {
    if (!newTitle.trim()) return;

    await api.post("/projects/", {
      title: newTitle,
      description: "",
    });

    setNewTitle("");
    loadProjects();
  };

  // ------------------------
  // Generate report
  // ------------------------
  const generateReport = async (project) => {
  if (loading) return;

  setSelectedProject(project);
  setLoading(true);
  setLoadingText("⏳ Generating report (live)...");
  setReport(null);
  setIeeeReport(null);
  setSections([]);
  setShowSections(false);
  setAnswer("");
  setQuestion("");
  setSources([]);

  let poller = null;

  try {
    // 🔁 Start polling immediately
    poller = startPollingReport(project.id);

    // 🔥 This call will take LONG time (20–40 mins)
    await api.post(`/projects/${project.id}/generate_simple_report`);

    // Final fetch (just in case)
    const res = await api.get(`/projects/${project.id}/report`);
    setReport(res.data);

    await loadSources(project.id);
  } catch (err) {
    alert("Failed to generate report");
  }

  // 🛑 Stop polling
  if (poller) clearInterval(poller);

  setLoading(false);
  setLoadingText("");
};

  // ------------------------
  // Expand to IEEE
  // ------------------------
  const expandToIEEE = async () => {
    if (!selectedProject || loading) return;

    setLoading(true);
    setLoadingText("⏳ Converting to IEEE format...");

    try {
      await api.post(`/projects/${selectedProject.id}/expand_to_ieee`);
      const res = await api.get(`/projects/${selectedProject.id}/report`);
      setReport(res.data);
      setSections([]);
      setShowSections(false);
      await loadSources(selectedProject.id);
    } catch (err) {
      alert("Failed to expand to IEEE format");
    }

    setLoading(false);
    setLoadingText("");
  };

  // ------------------------
  // Split Report
  // ------------------------
  const splitReport = async () => {
    if (!selectedProject || loading) return;

    setLoading(true);
    setLoadingText("⏳ Splitting report into sections...");

    try {
      await api.post(`/projects/${selectedProject.id}/split_report`);
      alert("✅ Report split successfully. Now click 'View Sections'.");
    } catch (err) {
      alert("Failed to split report");
    }

    setLoading(false);
    setLoadingText("");
  };
  // new function 
  const startPollingReport = (projectId) => {
  const interval = setInterval(async () => {
    try {
      const r = await api.get(`/projects/${projectId}/report`);
      setReport(r.data);
    } catch {}

    try {
      const s = await api.get(`/projects/${projectId}/sources`);
      setSources(s.data);
    } catch {}
  }, 3000); // every 3 seconds

  return interval;
};


  // ------------------------
  // Load Sections
  // ------------------------
  const loadSections = async () => {
    if (!selectedProject || loading) return;

    setLoading(true);
    setLoadingText("⏳ Loading sections...");

    try {
      const res = await api.get(`/projects/${selectedProject.id}/sections`);
      setSections(res.data);
      setShowSections(true);
    } catch (err) {
      alert("No sections found. Split first.");
    }

    setLoading(false);
    setLoadingText("");
  };

  // ------------------------
  // Ask from report
  // ------------------------
  const askFromReport = async () => {
    if (!question.trim() || asking || loading) return;

    setAsking(true);
    setAnswer("");

    try {
      const res = await api.post(
        `/projects/${selectedProject.id}/ask_from_report?question=${encodeURIComponent(
          question
        )}`
      );
      setAnswer(res.data.answer);
    } catch (err) {
      alert("Failed to ask question");
    }

    setAsking(false);
  };

  // ------------------------
  // Download report
  // ------------------------
  const downloadReport = (type) => {
    if (!selectedProject) return;

    const url = `${api.defaults.baseURL}/projects/${selectedProject.id}/download/${type}`;
    window.open(url, "_blank");
  };

  return (
    <div style={{ padding: 20, fontFamily: "Arial", maxWidth: 1200, margin: "auto" }}>
      <h1>AutoResearch Pro</h1>

      <h2>Create Research Topic</h2>
      <input
        value={newTitle}
        onChange={(e) => setNewTitle(e.target.value)}
        style={{ width: 400 }}
        placeholder="Enter topic..."
      />
      <button onClick={createProject} style={{ marginLeft: 10 }}>
        Create
      </button>

      <hr />

      <h2>Projects</h2>
      <ul>
        {projects.map((p) => (
          <li key={p.id} style={{ marginBottom: 10 }}>
            <b>{p.title}</b>{" "}
            <button onClick={() => generateReport(p)} disabled={loading}>
              {loading && selectedProject?.id === p.id ? "⏳ Generating..." : "Generate Report"}
            </button>
          </li>
        ))}
      </ul>

      <hr />

      {loading && (
        <p style={{ color: "orange", fontWeight: "bold" }}>
          {loadingText || "⏳ Working..."}
        </p>
      )}

      {report && (
        <div>
          <h2>📄 {report.title}</h2>

          <div style={{ display: "grid", gridTemplateColumns: "3fr 1fr", gap: 20 }}>
            {/* REPORT */}
            <pre
              style={{
                background: "#1e1e1e",
                color: "#fff",
                padding: 15,
                maxHeight: "60vh",
                overflowY: "auto",
                whiteSpace: "pre-wrap",
                borderRadius: 8,
              }}
            >
              {report.full_content}
            </pre>

            {/* SOURCES */}
            <div
              style={{
                background: "#111",
                color: "#fff",
                padding: 15,
                borderRadius: 8,
                maxHeight: "60vh",
                overflowY: "auto",
              }}
            >
              <h3>🔗 Sources</h3>

              {sources.length === 0 && <p style={{ color: "#888" }}>No sources found.</p>}

              {sources.map((s, i) => (
                <div key={s.id} style={{ marginBottom: 12 }}>
                  <a
                    href={s.url}
                    target="_blank"
                    rel="noreferrer"
                    style={{ color: "#4da3ff", textDecoration: "none" }}
                  >
                    {i + 1}. {s.title || s.url}
                  </a>
                </div>
              ))}
            </div>
          </div>

          <br />

          <button onClick={expandToIEEE} disabled={loading}>
            {loading ? "⏳ Working..." : "🔥 Convert to IEEE"}
          </button>

          <button onClick={splitReport} style={{ marginLeft: 10 }} disabled={loading}>
            {loading ? "⏳ Working..." : "✂️ Split Report"}
          </button>

          <button onClick={loadSections} style={{ marginLeft: 10 }} disabled={loading}>
            {loading ? "⏳ Working..." : "📑 View Sections"}
          </button>

          <button onClick={() => downloadReport("word")} style={{ marginLeft: 10 }} disabled={loading}>
            ⬇️ Download Word
          </button>

          <button onClick={() => downloadReport("pdf")} style={{ marginLeft: 10 }} disabled={loading}>
            ⬇️ Download PDF
          </button>

          <hr />

          {showSections && sections.length > 0 && (
            <div>
              <h2>📚 Sections</h2>
              {sections.map((s) => (
                <div
                  key={s.id}
                  style={{
                    marginBottom: 20,
                    padding: 15,
                    background: "#222",
                    color: "#fff",
                    borderRadius: 8,
                  }}
                >
                  <h3>
                    {s.order}. {s.title}
                  </h3>
                  <pre style={{ whiteSpace: "pre-wrap" }}>{s.content}</pre>
                </div>
              ))}
            </div>
          )}

          <hr />
          <button onClick={loadIEEEReport} style={{ marginLeft: 10 }}>
            📄 View IEEE Report
          </button>

          <h2>❓ Ask from Report</h2>
          <input
            style={{ width: "80%" }}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask something from this report..."
          />
          <button onClick={askFromReport} style={{ marginLeft: 10 }} disabled={asking || loading}>
            {asking ? "🤔 Thinking..." : "Ask"}
          </button>

         {answer && (
  <div style={{ marginTop: 20, padding: 15, background: "#003300", color: "#00ff88", borderRadius: 8 }}>
    <b>Answer:</b>
    <p>{answer}</p>
  </div>
)}

/* 👇 ADD THIS EXACTLY HERE 👇 */

{ieeeReport && (
  <div style={{ marginTop: 30 }}>
    <h2>📘 IEEE Report</h2>
    <pre
      style={{
        background: "#0f172a",
        color: "#fff",
        padding: 15,
        maxHeight: "60vh",
        overflowY: "auto",
        whiteSpace: "pre-wrap",
        borderRadius: 8,
      }}
    >
      {ieeeReport.full_content}
    </pre>
  </div>
)}

        </div>
      )}
    </div>
  );
}

export default App;
