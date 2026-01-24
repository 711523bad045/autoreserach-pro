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
  // Generate report (FAST)
  // ------------------------
  const generateReport = async (project) => {
    setSelectedProject(project);
    setLoading(true);
    setReport(null);
    setAnswer("");
    setQuestion("");

    try {
      await api.post(`/projects/${project.id}/generate_simple_report`);
      const res = await api.get(`/projects/${project.id}/report`);
      console.log("📄 Report length:", res.data?.full_content?.length);
      setReport(res.data);
    } catch (err) {
      console.error("❌ Error:", err);
      alert("Failed to generate report. Check backend logs.");
    }

    setLoading(false);
  };

  // ------------------------
  // Expand to IEEE
  // ------------------------
  const expandToIEEE = async () => {
    if (!selectedProject) return;

    setLoading(true);

    try {
      await api.post(`/projects/${selectedProject.id}/expand_to_ieee`);
      const res = await api.get(`/projects/${selectedProject.id}/report`);
      setReport(res.data);
    } catch (err) {
      alert("Failed to expand to IEEE format");
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
      alert("Failed to ask question");
    }

    setAsking(false);
  };

  // ------------------------
  // UI
  // ------------------------
  return (
    <div style={{ padding: 20, fontFamily: "Arial", maxWidth: 1100, margin: "auto" }}>
      <h1>AutoResearch Pro (Offline)</h1>

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

      <h2>Projects</h2>
      <ul>
        {projects.map((p) => (
          <li key={p.id} style={{ marginBottom: 10 }}>
            <b>{p.title}</b>{" "}
            <button onClick={() => generateReport(p)}>Generate Report</button>
          </li>
        ))}
      </ul>

      <hr />

      {loading && <p>⏳ Working... Please wait.</p>}

      {report && (
        <div>
          <h2>📄 {report.title}</h2>

          <div
            style={{
              marginBottom: 20,
              padding: 15,
              background: "#1e1e1e",
              color: "#ffffff",
              borderRadius: 8,
              whiteSpace: "pre-wrap",
              maxHeight: "70vh",
              overflowY: "auto",
            }}
          >
            {report.full_content && report.full_content.trim().length > 0
              ? report.full_content
              : "❌ Report is empty"}
          </div>

          <button onClick={expandToIEEE}>
            🔥 Convert to IEEE Research Paper
          </button>

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
