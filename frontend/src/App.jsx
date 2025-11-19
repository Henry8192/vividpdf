import React, { useState } from "react";
import "./App.css";

import { styled } from "@mui/material/styles";
import Button from "@mui/material/Button";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";

const VisuallyHiddenInput = styled("input")({
  clip: "rect(0 0 0 0)",
  clipPath: "inset(50%)",
  height: 1,
  overflow: "auto",
  position: "absolute",
  bottom: 0,
  left: 0,
  whiteSpace: "nowrap",
  width: 1,
});

export default function App() {
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
    <Box
      sx={{
        width: "100vw",
        height: "100vh",
        overflow: "auto",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        bgcolor: "#f5f5f5",
        flexDirection: "column",
        gap: 2,
      }}
    >
      <Button
        component="label"
        variant="contained"
        startIcon={<CloudUploadIcon />}
        disabled={loading}
        sx={{ fontSize: "1.1rem", padding: "10px 20px" }}
      >
        {loading ? "Processing..." : "Upload PDF"}
        <VisuallyHiddenInput type="file" accept="application/pdf" onChange={handleUpload} />
      </Button>

      {loading && <CircularProgress />}

      {msg && (
        <Box
          sx={{
            mt: 2,
            padding: 2,
            bgcolor: "white",
            borderRadius: 2,
            boxShadow: 1,
            width: "60vw",
            maxWidth: "600px",
            textAlign: "left",
            fontFamily: "monospace",
            fontSize: "0.85rem",
            whiteSpace: "pre-wrap",
          }}
        >
          {msg}
        </Box>
      )}
    </Box>
  );
}