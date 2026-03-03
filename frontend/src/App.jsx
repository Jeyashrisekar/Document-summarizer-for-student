import React, { useState } from "react";
import "./App.css";

function App() {
  const [textInput, setTextInput] = useState("");
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [summaryType, setSummaryType] = useState("short");

  const handleSummarize = async (e) => {
    e.preventDefault();
    setSummary("");

    const formData = new FormData();
    if (file) formData.append("file", file);
    else formData.append("text_input", textInput);
    formData.append("summary_type", summaryType);

    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/summarize", {
        method: "POST",
        body: formData,
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        setSummary(prev => prev + decoder.decode(value));
      }
    } catch {
      alert("Backend not running.");
    }

    setLoading(false);
  };

  return (
    <div className="app">
      <div className="card">
        <h1> Hushh Document Summarizer</h1>

        <textarea
          placeholder="Paste your text..."
          value={textInput}
          onChange={(e) => {
            setTextInput(e.target.value);
            setFile(null);
          }}
        />

        <div className="upload">
          <input
            type="file"
            onChange={(e) => {
              setFile(e.target.files[0]);
              setTextInput("");
            }}
          />
        </div>

        <select
          value={summaryType}
          onChange={(e) => setSummaryType(e.target.value)}
        >
          <option value="short">Short</option>
          <option value="medium">Medium</option>
          <option value="detailed">Detailed</option>
        </select>

        <button onClick={handleSummarize} disabled={loading}>
          {loading ? "Generating..." : "Generate Summary"}
        </button>

        {summary && (
          <div className="result">
            <h3>Summary</h3>
            <div className="summary-text">
              {summary}
              {loading && <span className="blink">|</span>}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;