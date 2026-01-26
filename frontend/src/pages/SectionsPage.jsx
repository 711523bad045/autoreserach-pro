import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api";
import "../styles/SectionsPage.css";

function SectionsPage() {
  const { projectId } = useParams();
  const navigate = useNavigate();

  const [sections, setSections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSection, setSelectedSection] = useState(null);

  useEffect(() => {
    loadSections();
  }, [projectId]);

  const loadSections = async () => {
    try {
      const res = await api.get(`/projects/${projectId}/sections`);
      setSections(res.data);
      if (res.data.length > 0) {
        setSelectedSection(res.data[0]);
      }
    } catch (err) {
      alert("No sections found. Please split the report first.");
      navigate(`/report/${projectId}`);
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="sections-container">
        <div className="loading-screen">
          <div className="spinner"></div>
          <h2>Loading Sections...</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="sections-container">
      {/* Top Navigation */}
      <nav className="top-nav">
        <button onClick={() => navigate(`/report/${projectId}`)} className="btn-back">
          ← Back to Report
        </button>
        <h1>Report Sections ({sections.length})</h1>
      </nav>

      {/* Split View */}
      <div className="split-view">
        {/* Left Sidebar - Section List */}
        <div className="sections-sidebar">
          <h3>📑 Table of Contents</h3>
          <div className="sections-list">
            {sections.map((section) => (
              <div
                key={section.id}
                className={`section-item ${
                  selectedSection?.id === section.id ? "active" : ""
                }`}
                onClick={() => setSelectedSection(section)}
              >
                <span className="section-number">{section.order}</span>
                <span className="section-title">{section.title}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Right Panel - Section Content */}
        <div className="section-content-panel">
          {selectedSection ? (
            <>
              <div className="section-header">
                <h2>
                  {selectedSection.order}. {selectedSection.title}
                </h2>
              </div>
              <div className="section-body">
                <pre>{selectedSection.content}</pre>
              </div>
            </>
          ) : (
            <div className="empty-state">
              <p>Select a section from the left to view its content</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SectionsPage;