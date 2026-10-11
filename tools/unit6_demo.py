"""Display one real local run; persist only the minimized audit record."""
import argparse
import json
from pathlib import Path
from src.rag_guard.unit6_app import build_app, case_documents, print_result, MODES


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", default="clean-01")
    parser.add_argument("--mode", choices=MODES, default="hybrid")
    args = parser.parse_args()
    cases = json.loads(Path("config/unit6_cases.json").read_text(encoding="utf-8"))
    case = next((c for c in cases if c["id"] == args.case), None)
    if case is None:
        raise SystemExit("Unknown case identifier")
    print("Case:", case["id"], "| Synthetic pilot input")
    print("Question:", case["query"])
    print("Retrieved source:", case["text"])
    result = build_app(case_documents(case), args.mode).run(case["query"], 1)
    print_result(result)
    target = Path("results/unit6_local") / ("demo-" + result["audit"]["run_id"] + ".json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result["audit"], indent=2) + "\n", encoding="utf-8")
    print("Audit:", target.as_posix())
    if result["audit"]["status"] == "generation_error":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
