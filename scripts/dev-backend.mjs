/**
 * Starts the FastAPI backend for local development.
 *
 * Exists so that `npm run dev` works from the repository root on Windows, macOS
 * and Linux without the developer having to activate a virtual environment
 * first. The interpreter lives in a different place per platform, so we look
 * for it rather than assuming.
 */

import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const backendDir = join(repoRoot, "backend");

const candidates = [
  join(backendDir, ".venv", "Scripts", "python.exe"), // Windows
  join(backendDir, ".venv", "bin", "python"), // macOS, Linux
];

const python = candidates.find((candidate) => existsSync(candidate));

if (!python) {
  console.error(
    [
      "",
      "No backend virtual environment found.",
      "",
      "Expected one of:",
      ...candidates.map((candidate) => `  ${candidate}`),
      "",
      "Run the first-time setup from the repository root:",
      "",
      "  python -m venv backend/.venv",
      "  backend\\.venv\\Scripts\\python.exe -m pip install -r backend/requirements.txt   (Windows)",
      "  backend/.venv/bin/python -m pip install -r backend/requirements.txt             (macOS, Linux)",
      "",
      "See the README for the full setup instructions.",
      "",
    ].join("\n"),
  );
  process.exit(1);
}

const args = [
  "-m",
  "uvicorn",
  "app.main:app",
  "--reload",
  "--host",
  "127.0.0.1",
  "--port",
  "8000",
];

const child = spawn(python, args, {
  cwd: backendDir,
  stdio: "inherit",
  env: process.env,
});

child.on("error", (error) => {
  console.error(`Failed to start the backend: ${error.message}`);
  process.exit(1);
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.exit(0);
  }
  process.exit(code ?? 1);
});
