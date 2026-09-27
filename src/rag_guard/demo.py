"""Command-line demonstration used in the Unit 4 presentation."""

from __future__ import annotations

import argparse
import json
from .core import GuardedRAG, load_documents


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local RAG security-gate prototype")
    parser.add_argument("query", nargs="?", default="How do I reset a router safely?")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--data", default="config/fixtures.json")
    parser.add_argument("--audit", default="results/latest_audit.jsonl")
    args = parser.parse_args()

    system = GuardedRAG(load_documents(args.data), audit_path=args.audit)
    result = system.run(args.query, top_k=args.top_k)
    if args.as_json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
        return

    print(f"Query: {result.query}")
    print("Retrieved passage decisions:")
    for item in result.retrieved:
        d = item.detection
        if d is None:
            print(f"  {item.document_id}: {item.decision.upper()} | {item.reason}")
        else:
            print(f"  {item.document_id}: {item.decision.upper()} | fused={d.fused_score:.3f} | uncertain={d.uncertain}")
            print(f"    evidence: {item.reason}")
    print("\nResponse:")
    print(result.response)


if __name__ == "__main__":
    main()
