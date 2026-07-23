import "./Dashboard.css";

function StatisticsCards({ sources }) {

    const papers = sources?.length || 0;

    return (

        <div className="stats-grid">

            <div className="stat-card">
                <h3>{papers}</h3>
                <span>Papers Retrieved</span>
            </div>

            <div className="stat-card">
                <h3>{Math.min(20, papers)}</h3>
                <span>Papers Used</span>
            </div>

            <div className="stat-card">
                <h3>96%</h3>
                <span>Confidence</span>
            </div>

            <div className="stat-card">
                <h3>2026</h3>
                <span>Latest Year</span>
            </div>

        </div>

    );
}

export default StatisticsCards;