import { useEffect, useState } from "react";
import { api } from "./api";

function App() {
  const [projects, setProjects] = useState([]);
  const [newTitle, setNewTitle] = useState("");
  const [selectedProject, setSelectedProject] = useState(null);

  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [asking, setAsking] = useState(false);

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
  // Create project
  // ------------------------
  const createProject = async () => {
    if (!newTitle.trim()) return;
    await api.post("/projects/", { title: newTitle, description: "" });
    setNewTitle("");
    loadProjects();
  };

  // ------------------------
  // Generate report (OFFLINE OLLAMA)
  // ------------------------
  const generateReport = async (project) => {
    setSelectedProject(project);
    setLoading(true);
    setReport(null);
    setAnswer("");
    setQuestion("");

    try {
      console.log("🧠 Generating research using Ollama for:", project.title);

      // 1. Generate report
      await api.post(`/projects/${project.id}/generate_simple_report`);

      console.log("📝 Report generated");

      // 2. Load report
      const res = await api.get(`/projects/${project.id}/report`);

      setReport(res.data);

    } catch (err) {
      console.error("❌ Error generating report:", err);
      alert("Failed to generate report. Check backend logs.");
    }

    setLoading(false);
  };

  // ------------------------
  // Ask from report
  // ------------------------
  const askFromReport = async () => {
    if (!question.trim()) return;

    setAsking(true);
    setAnswer("");

    try {
      const res = await api.post(
        `/projects/${selectedProject.id}/ask_from_report?question=${encodeURIComponent(question)}`
      );

      setAnswer(res.data.answer);
    } catch (err) {
      console.error("❌ Error asking question:", err);
      alert("Failed to ask question.");
    }

    setAsking(false);
  };

  // ------------------------
  // UI
  // ------------------------
  return (
    <div style={{ padding: 20, fontFamily: "Arial", maxWidth: 1000, margin: "auto" }}>
      <h1>AutoResearch Pro (Offline Ollama)</h1>

      {/* ---------------- Create Project ---------------- */}
      <h2>Create Research Topic</h2>
      <input
        value={newTitle}
        onChange={(e) => setNewTitle(e.target.value)}
        placeholder="Enter research topic..."
        style={{ width: 400 }}
      />
      <button onClick={createProject} style={{ marginLeft: 10 }}>
        Create
      </button>

      <hr />

      {/* ---------------- Projects List ---------------- */}
      <h2>Projects</h2>
      <ul>
        {projects.map((p) => (
          <li key={p.id} style={{ marginBottom: 10 }}>
            <b>{p.title}</b>{" "}
            <button onClick={() => generateReport(p)}>
              Generate Research
            </button>
          </li>
        ))}
      </ul>

      <hr />

      {/* ---------------- Loading ---------------- */}
      {loading && <p>⏳ Generating research using local Ollama... Please wait.</p>}

      {/* ---------------- Report Viewer ---------------- */}
      {report && (
        <div>
          <h2>📄 Report: {report.title}</h2>

          <div
            style={{
              marginBottom: 20,
              padding: 15,
              background: "#1e1e1e",
              color: "#ffffff",
              borderRadius: 8,
              whiteSpace: "pre-wrap",
            }}
          >
            {report.content || report.full_content}
          </div>

          {/* ---------------- Q&A ---------------- */}
          <hr />
          <h2>❓ Ask from this Report</h2>

          <input
            style={{ width: "80%" }}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question from this report..."
          />
          <button onClick={askFromReport} disabled={asking} style={{ marginLeft: 10 }}>
            Ask
          </button>

          {asking && <p>Thinking...</p>}

          {answer && (
            <div
              style={{
                marginTop: 20,
                padding: 15,
                background: "#003300",
                color: "#00ff88",
                borderRadius: 8,
              }}
            >
              <b>Answer:</b>
              <p>{answer}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
