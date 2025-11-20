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
  const outputPath = "./output/";

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
    const resultPath = path.resolve(
      outputPath,
      req.file.filename,
      "auto",
      `${req.file.filename}_content_list.json`
    );
    fs.readFile(resultPath, "utf8", (err, data) => {
      if (err) {
        res.status(500).json({ code, error: "Failed to read mineru output", details: err.message });
      } else {
        try {
          const json = JSON.parse(data);
          res.json({ code, output: json });
        } catch (parseErr) {
          res.status(500).json({ code, error: "Failed to parse JSON output", details: parseErr.message });
        }
      }
      fs.unlink(pdfPath, () => {});
    });
  });
});

app.listen(3000, () => console.log("Node backend on 3000"));
