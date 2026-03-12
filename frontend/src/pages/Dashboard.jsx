import React, { useState } from "react";
import { analyzeDocuments } from "../services/api";

const Dashboard = () => {
  const [driveLink, setDriveLink] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!driveLink) {
      alert("Please paste Google Drive folder link");
      return;
    }

    try {
      setLoading(true);
      setResult(null);

      const data = await analyzeDocuments(driveLink);
      setResult(data);
      setLoading(false);

    } catch (err) {
      console.error(err);
      alert("Upload failed. Check backend terminal.");
      setLoading(false);
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: 40 }}>
      <h1>AI Document Checker</h1>

      <h3>Paste Google Drive Folder Link</h3>

      <input
        type="text"
        placeholder="https://drive.google.com/drive/folders/xxxxx"
        value={driveLink}
        onChange={(e) => setDriveLink(e.target.value)}
        style={{ width: "400px", padding: "8px" }}
      />

      <br /><br />

      <button
        onClick={handleUpload}
        style={{
          padding: "12px 25px",
          fontSize: 16,
          backgroundColor: "#4CAF50",
          color: "white",
          border: "none",
          borderRadius: "8px",
          cursor: "pointer"
        }}
      >
        Analyze Documents
      </button>

      {loading && <h3>Analyzing documents...</h3>}

      {/* KEEP RESULT UI SAME */}
      {result && (
        <div style={{ marginTop: 30 }}>
          <h2>Score: {result.score}</h2>
          <h3>Status: {result.status}</h3>
          <h2 style={{color:"red"}}>
            AI Result: {result.same_person_result}
          </h2>

          <h3>Detected Person Info</h3>
          <ul>
            {result?.person_data?.map((p, i) => (
              <li key={i}>
                {p.file} → {p.name || "Name not found"} | {p.dob || "DOB not found"}
              </li>
            ))}
          </ul>

          <h3>Missing Documents</h3>
          <ul>
            {result.missing_documents.length === 0 && <li>None</li>}
            {result.missing_documents.map((m, i) => (
              <li key={i}>{m}</li>
            ))}
          </ul>

          <h3>Rejected / Weak Documents</h3>
          <ul>
            {result.weak_documents.length === 0 && <li>None</li>}
            {result.weak_documents.map((w, i) => (
              <li key={i}>
                <b>{w.file}</b> → {w.reason}
              </li>
            ))}
          </ul>

          <h3>AI Insights</h3>
          <ul>
            {result.insights.consistency_issues.length === 0 && <li>No issues</li>}
            {result.insights.consistency_issues.map((m, i) => (
              <li key={i}>{m}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Dashboard;