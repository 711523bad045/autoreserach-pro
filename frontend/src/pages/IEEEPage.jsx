import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api";
import "../styles/IEEEPage.css";

function IEEEPage() {
  const { projectId } = useParams();
  const navigate = useNavigate();

  const [ieeeReport, setIeeeReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadIEEEReport();
  }, [projectId]);

  const loadIEEEReport = async () => {
    try {
      const res = await api.get(`/projects/${projectId}/ieee`);
      setIeeeReport(res.data);
    } catch (err) {
      alert("No IEEE report found. Please generate it first.");
      navigate(`/report/${projectId}`);
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="ieee-container">
        <div className="loading-screen">
          <div className="spinner"></div>
          <h2>Loading IEEE Report...</h2>
        </div>
      </div>
    );
  }

  if (!ieeeReport) {
    return null;
  }

  return (
    <div className="ieee-container">
      {/* Top Navigation */}
      <nav className="top-nav">
        <button onClick={() => navigate(`/report/${projectId}`)} className="btn-back">
          ← Back to Report
        </button>
        <h1>IEEE Format - {ieeeReport.title}</h1>
      </nav>

      {/* IEEE Content */}
      <div className="ieee-content">
        <div className="ieee-paper">
          <pre>{ieeeReport.full_content}</pre>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="action-footer">
        <button
          onClick={() => window.print()}
          className="btn-action"
        >
          🖨️ Print
        </button>
        <button
          onClick={() => {
            const url = `${api.defaults.baseURL}/projects/${projectId}/download/pdf`;
            window.open(url, "_blank");
          }}
          className="btn-action"
        >
          ⬇️ Download PDF
        </button>
      </div>
    </div>
  );
}

export default IEEEPage;