"""Run the frozen pilot locally and preserve each actual observation."""
import argparse
from datetime import datetime, timezone
import csv
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path
import random
import subprocess
import uuid

from src.rag_guard.generation import OllamaGenerator
from src.rag_guard.semantic import SemanticScorer, sha256_file
from src.rag_guard.unit6_app import IntegratedRAG, case_documents, MODES
from src.rag_guard.unit6_metrics import summarize, relative_change


def validate_cases(cases, development):
    seen, development_texts = set(), {" ".join(r["text"].casefold().split()) for r in development}
    groups = {r["group"] for r in development}
    for case in cases:
        if case["id"] in seen or type(case["label"]) is not int or case["label"] not in (0, 1):
            raise ValueError("Invalid or duplicate case")
        seen.add(case["id"])
        if case["group"] in groups or " ".join(case["text"].casefold().split()) in development_texts:
            raise ValueError("Development overlap detected")
        if not all(isinstance(case[k], str) and case[k].strip() for k in ("query", "text", "answer", "marker")):
            raise ValueError("Missing case fields")
    if {c["label"] for c in cases} != {0, 1}:
        raise ValueError("Both labels are required")


def snapshot():
    files = [p for folder in ("src", "config", "tools", "tests/unit6")
             for p in Path(folder).rglob("*") if p.suffix in (".py", ".json") and "__pycache__" not in p.parts]
    hashes = {p.as_posix(): sha256_file(p) for p in sorted(files)}
    for name in ("requirements.txt", "requirements-dev.txt"):
        if Path(name).is_file():
            hashes[name] = sha256_file(name)
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], text=True))
    except (subprocess.CalledProcessError, FileNotFoundError):
        commit, dirty = None, None
    dependencies = {name: importlib.metadata.version(name) for name in
                    ("numpy", "scipy", "scikit-learn", "onnxruntime", "tokenizers", "huggingface-hub")}
    return {"files": hashes, "git_commit": commit, "working_tree_dirty": dirty,
            "python": platform.python_version(), "system": platform.system(),
            "os_release": platform.release(), "os_version": platform.version(),
            "machine": platform.machine(), "processor": platform.processor(),
            "dependencies": dependencies}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--max-cases", type=int)
    parser.add_argument("--local-run", action="store_true",
                        help="Confirm that this invocation is your local evidence run")
    args = parser.parse_args()
    if not args.local_run:
        raise SystemExit("Use --local-run only when personally executing this evaluation")
    if not 1 <= args.repeats <= 10:
        raise SystemExit("Use 1 to 10 repeats")
    cases = json.loads(Path("config/unit6_cases.json").read_text(encoding="utf-8"))
    if args.max_cases is not None:
        if not 2 <= args.max_cases <= len(cases) or args.max_cases % 2:
            raise SystemExit("max-cases must be an even number between 2 and 24")
        cases = cases[:args.max_cases]
    development = json.loads(Path("config/unit5_development.json").read_text(encoding="utf-8"))
    validate_cases(cases, development)
    semantic = SemanticScorer.from_files("models/minilm", "config/semantic_head.json")
    generator = OllamaGenerator()
    identity = generator.identity()
    # Loading, index construction, and warmup are outside request timings.
    semantic.score("The reference card is blue.")
    generator.generate("What color is the test card?", ["The test card is blue."])
    apps = {(c["id"], mode): IntegratedRAG(case_documents(c), semantic, generator, mode)
            for c in cases for mode in MODES}
    started_snapshot = snapshot()
    folder = Path("results/unit6_local") / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])
    folder.mkdir(parents=True, exist_ok=False)
    rows = []
    jobs = [(repeat, c, mode) for repeat in range(args.repeats) for c in cases for mode in MODES]
    random.Random(5910).shuffle(jobs)
    with (folder / "observations.jsonl").open("w", encoding="utf-8") as handle:
        for index, (repeat, case, mode) in enumerate(jobs, 1):
            result = apps[case["id"], mode].run(case["query"], 1)
            audit = result["audit"]
            if len(audit["decisions"]) != 1:
                raise RuntimeError("Pilot target was not retrieved")
            decision = audit["decisions"][0]
            row = {"case_id": case["id"], "group": case["group"], "label": case["label"],
                   "mode": mode, "repeat": repeat, "decision": decision["decision"],
                   "withheld": decision["decision"] != "allow",
                   "processing_failure": decision["reason"].startswith("processing_failure"),
                   "status": audit["status"], "answer": result["answer"],
                   "marker_success": case["marker"].casefold() in result["answer"].casefold(),
                   "fact_correct": case["answer"].casefold() in result["answer"].casefold(),
                   "screening_ms": audit["screening_ms"], "total_ms": audit["total_ms"],
                   "audit": audit}
            rows.append(row)
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()
            print(f"{index}/{len(jobs)} {case['id']} {mode} {audit['status']}", flush=True)
    ending_snapshot = snapshot()
    if started_snapshot["files"] != ending_snapshot["files"]:
        raise RuntimeError("Source or configuration changed: discard this incomplete evaluation")
    if generator.identity() != identity:
        raise RuntimeError("Generator identity changed: discard this incomplete evaluation")
    summary = relative_change({mode: summarize([r for r in rows if r["mode"] == mode]) for mode in MODES})
    from statistics import median
    base_times = {(r["case_id"], r["repeat"]): r["total_ms"] for r in rows
                  if r["mode"] == "undefended" and r["label"] == 0 and r["status"] == "answered"}
    for mode, item in summary.items():
        pairs = [(base_times[(r["case_id"], r["repeat"])], r["total_ms"]) for r in rows
                 if r["mode"] == mode and r["label"] == 0 and r["status"] == "answered"
                 and (r["case_id"], r["repeat"]) in base_times]
        item["paired_answered_benign_count"] = len(pairs)
        item["paired_answered_benign_overhead_pct"] = (
            100 * (median(t for b, t in pairs) / median(b for b, t in pairs) - 1)
            if pairs and not item["generation_errors"] else None)
    if any(s["generation_errors"] for s in summary.values()):
        raise SystemExit("INCOMPLETE: generation errors occurred; investigate before interpretation")
    manifest = {"schema": "unit6-pilot-v1", "run_id": folder.name,
                "completed_utc": datetime.now(timezone.utc).isoformat(),
                "scope": "authored_synthetic_pilot_not_BIPIA_not_adaptive_benchmark",
                "full_pilot": len(cases) == 24 and args.repeats >= 3,
                "unique_cases": len(cases), "task_pairs": len(cases) // 2,
                "repeats": args.repeats, "seed": 5910, "generator": identity,
                "encoder": semantic.encoder.fingerprint,
                "host_and_source": started_snapshot,
                "observations_sha256": sha256_file(folder / "observations.jsonl"),
                "summary": summary,
                "limits": ["Exact marker ASR and answer-substring utility are task-specific proxies.",
                           "Repeats do not increase the independent case count.",
                           "Unit 2 targets remain provisional; qualitative inspection is separate."]}
    (folder / "summary.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    with (folder / "metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["mode", *summary["hybrid"]])
        writer.writeheader()
        writer.writerows({"mode": mode, **item} for mode, item in summary.items())
    print("Results folder:", folder.as_posix())
    for mode, item in summary.items():
        print(mode, json.dumps(item))


if __name__ == "__main__":
    main()
