import React, { useState } from "react";
import "./App.css";

import Button from "@mui/material/Button";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";

const App = () => {
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState("");

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setMsg("");
    setLoading(true);

    const form = new FormData();
    form.append("file", file);

    try {
      const resp = await fetch("http://localhost:3000/upload", {
        method: "POST",
        body: form,
      });

      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || "Upload failed");
      setMsg(data.output || "MinerU completed.");
    } catch (err) {
      setMsg(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box className="app-root">
      <Button
        component="label"
        variant="contained"
        startIcon={<CloudUploadIcon />}
        disabled={loading}
        className="upload-btn"
      >
        {loading ? "Processing..." : "Upload PDF"}
        <input type="file"
          accept="application/pdf"
          onChange={handleUpload}
          style={{ display: "none" }}
        />
      </Button>

      {loading && <CircularProgress />}

      {msg && <Box className="msg-box">{msg}</Box>}
    </Box>
  );
};

export default App;
