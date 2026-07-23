import "./Dashboard.css";

function DashboardHeader({ report, onBack }) {
  return (
    <div className="dashboard-header">

      <div>
        <h1>{report?.title || "AutoResearch Pro"}</h1>

        <p>
          AI Powered Autonomous Research Assistant
        </p>
      </div>

      <div className="header-buttons">

        <button
          className="btn-secondary"
          onClick={onBack}
        >
          ← Projects
        </button>

      </div>

    </div>
  );
}

export default DashboardHeader;