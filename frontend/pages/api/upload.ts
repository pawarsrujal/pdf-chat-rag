import { useState } from "react";

export default function ChatPage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);

    try {
      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.detail || data.error || "Upload failed");
        return;
      }

      alert(`Successfully uploaded ${data.filename}`);
    } catch (err) {
      alert("Upload error");
    } finally {
      setUploading(false);
    }
  };

  const handleReset = async () => {
    try {
      await fetch("/api/reset", { method: "POST" });
      alert("Chat reset successfully");
      window.location.reload();
    } catch (err) {
      alert("Reset failed");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Upload Documents</h2>

      <input
        type="file"
        accept=".pdf"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />

      <br /><br />

      <button
        onClick={handleUpload}
        disabled={uploading}
        style={{
          padding: "8px 14px",
          backgroundColor: "#6b6bf5",
          color: "white",
          border: "none",
          borderRadius: "6px",
          cursor: "pointer",
        }}
      >
        {uploading ? "Uploading..." : "Upload"}
      </button>

      <br /><br />

      {/* 🔴 RESET BUTTON */}
      <button
        onClick={handleReset}
        style={{
          padding: "8px 14px",
          backgroundColor: "#ff4d4f",
          color: "white",
          border: "none",
          borderRadius: "6px",
          cursor: "pointer",
        }}
      >
        Reset Chat
      </button>
    </div>
  );
}
