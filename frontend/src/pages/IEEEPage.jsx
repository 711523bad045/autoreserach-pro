import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api";
import "../styles/IEEEPage.css";

function IEEEPage() {
    const { projectId } = useParams();
    const navigate = useNavigate();

    const [report, setReport] = useState(null);

    useEffect(() => {
        loadIEEE();
    }, []);

    async function loadIEEE() {
        try {
            const res = await api.get(`/projects/${projectId}/ieee`);
            setReport(res.data);
        } catch (err) {
            alert("Unable to load IEEE Report");
            navigate(`/report/${projectId}`);
        }
    }

    if (!report) {
        return <div className="loading">Generating IEEE preview…</div>;
    }

    return (
        <div className="paper-background">

            <div className="toolbar">
                <div className="toolbar-brand">
                    <span className="dot" />
                    Research Agent · IEEE Preview
                </div>

                <div className="toolbar-actions">
                    <button onClick={() => navigate(`/report/${projectId}`)}>
                        ← Back
                    </button>

                    <button className="primary" onClick={() => window.print()}>
                        Print / Export
                    </button>
                </div>
            </div>

            <div className="paper-frame">
                <div className="paper">

                    <h1 className="paper-title">
                        {report.title}
                    </h1>

                    <div className="authors">
                        Rajesh N | AI Research Assistant
                    </div>

                    <div className="abstract">
                        {report.abstract}
                    </div>

                    <div className="keywords">
                        Blockchain, Artificial Intelligence,
                        Deep Learning, Federated Learning, Research
                    </div>

                    <div className="columns">

                        <div className="column">

                            {report.full_content.split("\n").map((line, index) => {

                                if (!line.trim()) {
                                    return <br key={index} />;
                                }

                                // ---------------- Architecture ----------------

                                if (line.includes("[[IMAGE:architecture]]")) {
                                    return (
                                        <div className="figure" key={index}>
                                            <img
                                                src={`http://127.0.0.1:8000/generated_diagrams/${projectId}_architecture.png`}
                                                className="report-image"
                                                alt="Architecture"
                                            />
                                            <div className="figure-caption">
                                                Figure 1. Overall System Architecture
                                            </div>
                                        </div>
                                    );
                                }

                                // ---------------- Workflow ----------------

                                if (line.includes("[[IMAGE:workflow]]")) {
                                    return (
                                        <div className="figure" key={index}>
                                            <img
                                                src={`http://127.0.0.1:8000/generated_diagrams/${projectId}_workflow.png`}
                                                className="report-image"
                                                alt="Workflow"
                                            />
                                            <div className="figure-caption">
                                                Figure 2. Proposed Workflow
                                            </div>
                                        </div>
                                    );
                                }

                                // ---------------- Accuracy ----------------

                                if (line.includes("[[IMAGE:accuracy]]")) {
                                    return (
                                        <div className="figure" key={index}>
                                            <img
                                                src={`http://127.0.0.1:8000/generated_diagrams/${projectId}_accuracy.png`}
                                                className="report-image"
                                                alt="Accuracy"
                                            />
                                            <div className="figure-caption">
                                                Figure 3. Accuracy Comparison
                                            </div>
                                        </div>
                                    );
                                }

                                // ---------------- Comparison ----------------

                                if (line.includes("[[IMAGE:comparison]]")) {
                                    return (
                                        <div className="figure" key={index}>
                                            <img
                                                src={`http://127.0.0.1:8000/generated_diagrams/${projectId}_comparison.png`}
                                                className="report-image"
                                                alt="Comparison"
                                            />
                                            <div className="figure-caption">
                                                Figure 4. Performance Comparison
                                            </div>
                                        </div>
                                    );
                                }

                                // ---------------- H1 ----------------

                                if (line.startsWith("# ")) {
                                    return (
                                        <h1 key={index}>
                                            {line.replace("# ", "")}
                                        </h1>
                                    );
                                }

                                // ---------------- H2 ----------------

                                if (line.startsWith("## ")) {
                                    return (
                                        <h2 key={index}>
                                            {line.replace("## ", "")}
                                        </h2>
                                    );
                                }

                                // ---------------- H3 ----------------

                                if (line.startsWith("### ")) {
                                    return (
                                        <h3 key={index}>
                                            {line.replace("### ", "")}
                                        </h3>
                                    );
                                }

                                // ---------------- Paragraph ----------------

                                return (
                                    <p key={index}>
                                        {line}
                                    </p>
                                );

                            })}

                        </div>

                    </div>

                    <div className="page-number">
                        Page 1
                    </div>

                </div>
            </div>

        </div>
    );
}

export default IEEEPage;