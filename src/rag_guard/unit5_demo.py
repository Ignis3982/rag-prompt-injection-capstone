"""Reproducible CLI demonstrations using the real fitted semantic component."""
import argparse
import json
from pathlib import Path

from src.rag_guard.core import load_documents
from src.rag_guard.semantic import SemanticScorer, sha256_file
from src.rag_guard.screening import ScreeningPipeline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--data", default="config/fixtures.json")
    parser.add_argument("--output", default="results/unit5_demo.json")
    args = parser.parse_args()
    semantic = SemanticScorer.from_files("models/minilm", "config/semantic_head.json")
    result = ScreeningPipeline(load_documents(args.data), semantic).run(args.query)
    result["audit"]["head_sha256"] = sha256_file("config/semantic_head.json")
    result["audit"]["encoder"] = semantic.encoder.fingerprint
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    # Store evidence only; the preview is printed for the synthetic demo.
    target.write_text(json.dumps(result["audit"], indent=2) + "\n")
    print("UNIT 5 | frozen MiniLM + fitted head + structural rules")
    for decision in result["audit"]["decisions"]:
        print(decision["document_id"], decision["decision"].upper(), decision["reason"])
        for window in decision["windows"]:
            print(f"  semantic={window['semantic']:.4f} rules={window['structural']:.2f} "
                  f"risk={window['risk']:.4f} uncertain={window['uncertain']}")
            print("  reasons:", ", ".join(window["reasons"]) or "below review band")
            for location in window["locations"]:
                print("  evidence:", location["code"], "offsets", location["start"], location["end"])
    print(result["response"])
    print("Audit:", target)
    print("Functional demonstration only; no LLM attack-success measurement.")


if __name__ == "__main__":
    main()
