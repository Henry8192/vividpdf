import express from "express";
import cors from "cors";
import multer from "multer";
import { spawn } from "child_process";
import path from "path";
import fs from "fs";

const app = express();
app.use(cors());

const upload = multer({ dest: "uploads/" });

app.post("/upload", upload.single("file"), (req, res) => {
  if (!req.file) return res.status(400).json({ error: "No file uploaded" });

  const pdfPath = path.resolve(req.file.path);
  const outputPath = pdfPath + ".out";

  const p = spawn(path.resolve("venv/bin/mineru"), [
    "-p",
    pdfPath,
    "-o",
    outputPath
  ]);

  let buffer = "";
  p.stdout.on("data", d => buffer += d);
  p.stderr.on("data", d => buffer += d);

  p.on("close", code => {
    res.json({ code, output: buffer });
    fs.unlink(pdfPath, () => {});
  });
});

app.listen(3000, () => console.log("Node backend on 3000"));
