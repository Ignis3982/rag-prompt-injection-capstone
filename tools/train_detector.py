"""Fit the Unit 5 synthetic development head; no benchmark test data loaded."""
import json
from pathlib import Path
from src.rag_guard.semantic import MiniLMEncoder, fit_head, sha256_file

path = Path("config/unit5_development.json")
records = json.loads(path.read_text())
artifact = fit_head(records, MiniLMEncoder("models/minilm"))
artifact["development_sha256"] = sha256_file(path)
target = Path("config/semantic_head.json")
target.write_text(json.dumps(artifact, indent=2) + "\n")
print("Fitted frozen MiniLM + logistic head + independent sigmoid mapping")
print("Training records:", artifact["train_count"])
print("Calibration records:", artifact["calibration_count"])
print("Artifact:", target)
print("Artifact SHA256:", sha256_file(target))
print("Scope:", artifact["scope"])
