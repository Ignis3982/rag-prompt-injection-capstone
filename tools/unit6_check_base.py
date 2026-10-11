"""Stop on a changed dependency instead of replacing established project files."""
import hashlib
import json
from pathlib import Path


def main():
    expected = json.loads(Path("config/unit6_base_sha256.json").read_text())
    mismatch = []
    for name, digest in expected.items():
        path = Path(name)
        actual = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest() if path.is_file() else None
        print(name, "MATCH" if actual == digest else "REVIEW REQUIRED")
        if actual != digest:
            mismatch.append(name)
    if mismatch:
        raise SystemExit("STOP: review changed Unit 5 dependencies before integration")
    print("All expected Unit 5 source dependencies match. No Git history was imported.")


if __name__ == "__main__":
    main()
