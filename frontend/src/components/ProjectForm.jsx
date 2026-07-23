import { useState } from "react";

function ProjectForm({ onCreate }) {
  const [form, setForm] = useState({
    title: "",
    description: "",
    objective: "",
    requirements: "",
    domain: "Artificial Intelligence",
    year_from: 2022,
    year_to: 2026,
    preferred_sources: ["IEEE", "Springer"],
  });

  const domains = [
    "Artificial Intelligence",
    "Machine Learning",
    "Deep Learning",
    "Computer Vision",
    "Natural Language Processing",
    "Cyber Security",
    "Cloud Computing",
    "Blockchain",
    "Internet of Things",
    "Data Science",
    "Healthcare",
    "Robotics",
  ];

  const sources = [
    "IEEE",
    "Springer",
    "ACM",
    "Elsevier",
    "Nature",
    "ScienceDirect",
    "arXiv",
  ];

  const update = (key, value) => {
    setForm((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const toggleSource = (source) => {
    if (form.preferred_sources.includes(source)) {
      update(
        "preferred_sources",
        form.preferred_sources.filter((s) => s !== source)
      );
    } else {
      update("preferred_sources", [
        ...form.preferred_sources,
        source,
      ]);
    }
  };

  const submit = () => {
    if (!form.title.trim()) {
      alert("Project title is required.");
      return;
    }

    onCreate(form);

    setForm({
      title: "",
      description: "",
      objective: "",
      requirements: "",
      domain: "Artificial Intelligence",
      year_from: 2022,
      year_to: 2026,
      preferred_sources: ["IEEE", "Springer"],
    });
  };

  return (
    <div className="section-card">

      <h2>Create New Research Project</h2>

      <input
        className="topic-input"
        placeholder="Project Title"
        value={form.title}
        onChange={(e) => update("title", e.target.value)}
      />

      <br /><br />

      <textarea
        rows="6"
        className="topic-input"
        placeholder="Describe your project..."
        value={form.description}
        onChange={(e) => update("description", e.target.value)}
      />

      <br /><br />

      <textarea
        rows="3"
        className="topic-input"
        placeholder="Research Objective"
        value={form.objective}
        onChange={(e) => update("objective", e.target.value)}
      />

      <br /><br />

      <textarea
        rows="4"
        className="topic-input"
        placeholder="Report Requirements"
        value={form.requirements}
        onChange={(e) => update("requirements", e.target.value)}
      />

      <br /><br />

      <select
        className="topic-input"
        value={form.domain}
        onChange={(e) => update("domain", e.target.value)}
      >
        {domains.map((d) => (
          <option key={d}>{d}</option>
        ))}
      </select>

      <br /><br />

      <div
        style={{
          display: "flex",
          gap: "20px",
        }}
      >
        <input
          type="number"
          className="topic-input"
          value={form.year_from}
          onChange={(e) =>
            update("year_from", Number(e.target.value))
          }
        />

        <input
          type="number"
          className="topic-input"
          value={form.year_to}
          onChange={(e) =>
            update("year_to", Number(e.target.value))
          }
        />
      </div>

      <br />

      <h4>Preferred Sources</h4>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3,1fr)",
          gap: "10px",
        }}
      >
        {sources.map((src) => (
          <label key={src}>
            <input
              type="checkbox"
              checked={form.preferred_sources.includes(src)}
              onChange={() => toggleSource(src)}
            />
            {" "}
            {src}
          </label>
        ))}
      </div>

      <br />

      <button
        className="btn-create"
        onClick={submit}
      >
        Generate Research
      </button>

    </div>
  );
}

export default ProjectForm;