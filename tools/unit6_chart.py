"""Create an SVG chart from a completed local pilot, never from sample numbers."""
import argparse
from html import escape
import json
from pathlib import Path
from src.rag_guard.semantic import sha256_file


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder")
    args = parser.parse_args()
    folder = Path(args.folder)
    data = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
    if data.get("schema") != "unit6-pilot-v1" or not data.get("full_pilot"):
        raise SystemExit("A complete 24-case pilot with at least three repeats is required")
    if sha256_file(folder / "observations.jsonl") != data["observations_sha256"]:
        raise SystemExit("Observation digest mismatch")
    if any(row["generation_errors"] for row in data["summary"].values()):
        raise SystemExit("Resolve generation errors before creating the results figure")
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="650" viewBox="0 0 1100 650">',
           '<rect width="1100" height="650" fill="white"/>',
           '<g font-family="Arial" fill="#162b40">',
           '<text x="60" y="45" font-size="26">Synthetic pilot detection and benign withholding</text>',
           '<text x="60" y="76" font-size="17">24 cases in 12 task pairs; first repetition per case for classification</text>']
    for step in range(6):
        y = 495 - step * 70
        svg.extend([f'<path d="M95 {y} H1040" stroke="#dddddd"/>',
                    f'<text x="42" y="{y + 6}" font-size="19">{step / 5:.1f}</text>'])
    for i, (mode, row) in enumerate(data["summary"].items()):
        x = 145 + 225 * i
        for delta, metric, color in ((0, "f1", "#214e74"), (72, "benign_fpr", "#a34a24")):
            value = row[metric]
            if not isinstance(value, (int, float)) or not 0 <= value <= 1:
                raise SystemExit("Invalid metric range")
            height = value * 350
            svg.extend([f'<rect x="{x+delta}" y="{495-height}" width="58" height="{height}" fill="{color}"/>',
                        f'<text x="{x+delta+29}" y="{483-height}" font-size="18" text-anchor="middle">{value:.3f}</text>'])
        svg.append(f'<text x="{x+64}" y="531" font-size="20" text-anchor="middle">{escape(mode)}</text>')
    svg.extend(['<rect x="300" y="570" width="20" height="20" fill="#214e74"/>',
                '<text x="330" y="587" font-size="20">F1 (higher is better)</text>',
                '<rect x="610" y="570" width="20" height="20" fill="#a34a24"/>',
                '<text x="640" y="587" font-size="20">Benign FPR (lower is better)</text>',
                '<text x="60" y="627" font-size="16">Quarantine counts as withholding. This is not a BIPIA or population-level robustness result.</text>',
                '</g></svg>'])
    target = folder / "pilot_chart.svg"
    target.write_text("\n".join(svg), encoding="utf-8")
    print("Chart:", target.as_posix())


if __name__ == "__main__":
    main()
