import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import "../styles/HomePage.css";

function HomePage() {
  const [projects, setProjects] = useState([]);
  const [newTitle, setNewTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [generatingId, setGeneratingId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);
  
  const navigate = useNavigate();

  const loadProjects = async () => {
    const res = await api.get("/projects/");
    setProjects(res.data);
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const createProject = async () => {
    if (!newTitle.trim()) return;

    await api.post("/projects/", {
      title: newTitle,
      description: "",
    });

    setNewTitle("");
    loadProjects();
  };

  const generateReport = async (project) => {
    if (loading) return;

    setLoading(true);
    setGeneratingId(project.id);

    try {
      await api.post(`/projects/${project.id}/generate_simple_report`);
      navigate(`/report/${project.id}`);
    } catch (err) {
      alert("Failed to generate report");
    }

    setLoading(false);
    setGeneratingId(null);
  };

  const viewReport = (projectId) => {
    navigate(`/report/${projectId}`);
  };

  const deleteProject = async (projectId, projectTitle) => {
    const confirmDelete = window.confirm(
      `⚠️ Are you sure you want to delete "${projectTitle}"?\n\nThis action cannot be undone and will remove all associated reports.`
    );
    
    if (!confirmDelete) return;

    setDeletingId(projectId);

    try {
      await api.delete(`/projects/${projectId}`);
      loadProjects();
    } catch (err) {
      alert("Failed to delete project. Please try again.");
    }

    setDeletingId(null);
  };

  return (
    <div className="home-container">
      {/* Animated Background */}
      <div className="animated-bg">
        <div className="sphere sphere-1"></div>
        <div className="sphere sphere-2"></div>
        <div className="sphere sphere-3"></div>
      </div>

      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo-section">
            <span className="logo-icon">📚</span>
            <div>
              <h1>AutoResearch Pro</h1>
              <p className="subtitle">AI-Powered Research Report Generator</p>
            </div>
          </div>
        </div>
      </header>

      {/* Create New Project */}
      <section className="create-section">
        <div className="section-card">
          <h2>🚀 Create New Research Topic</h2>
          <div className="input-group">
            <input
              type="text"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="Enter your research topic (e.g., Artificial Intelligence, Quantum Computing...)"
              className="topic-input"
              onKeyPress={(e) => e.key === "Enter" && createProject()}
            />
            <button onClick={createProject} className="btn-create">
              <span className="btn-icon">➕</span>
              Create Project
            </button>
          </div>
        </div>
      </section>

      {/* Projects Grid */}
      <section className="projects-section">
        <h2 className="section-title">📂 Your Research Projects</h2>
        
        {projects.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <h3>No Projects Yet</h3>
            <p>Create your first research topic above to get started!</p>
            <div className="empty-decoration">
              <span>🚀</span>
              <span>✨</span>
              <span>🎯</span>
            </div>
          </div>
        ) : (
          <div className="projects-grid">
            {projects.map((project, index) => (
              <div 
                key={project.id} 
                className="project-card"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="card-glow"></div>
                
                <div className="card-header">
                  <div className="title-section">
                    <h3>{project.title}</h3>
                    <span className="project-id">
                      <span className="id-label">ID:</span> {project.id}
                    </span>
                  </div>
                  <button
                    onClick={() => deleteProject(project.id, project.title)}
                    disabled={deletingId === project.id}
                    className="btn-delete"
                    title="Delete Project"
                  >
                    {deletingId === project.id ? (
                      <span className="spinner-small"></span>
                    ) : (
                      "🗑️"
                    )}
                  </button>
                </div>
                
                <div className="card-footer">
                  <button
                    onClick={() => generateReport(project)}
                    disabled={loading && generatingId === project.id}
                    className="btn-generate"
                  >
                    {generatingId === project.id ? (
                      <>
                        <span className="spinner-small"></span>
                        Generating...
                      </>
                    ) : (
                      <>
                        <span className="btn-icon">🔥</span>
                        Generate Report
                      </>
                    )}
                  </button>
                  
                  <button
                    onClick={() => viewReport(project.id)}
                    className="btn-view"
                  >
                    <span className="btn-icon">👁️</span>
                    View Report
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Floating Particles */}
      <div className="particles">
        {[...Array(20)].map((_, i) => (
          <div key={i} className="particle" style={{
            left: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 5}s`,
            animationDuration: `${5 + Math.random() * 10}s`
          }}></div>
        ))}
      </div>
    </div>
  );
}

export default HomePage;