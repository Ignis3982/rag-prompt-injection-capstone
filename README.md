# Robust and Explainable Detection of Indirect Prompt Injection in Retrieval-Augmented Generation Systems

MSIT 5910 Capstone Project. Unit 6 integrates hybrid passage screening,
local Ollama generation, and a desktop interface. This is a research
prototype, not a validated production security defense.

## Current status (Unit 6)

The verified local pilot (20261010T151239Z-189082a4) evaluated 24
synthetic cases in four modes with three repetitions (288 executions).
Hybrid F1 was 0.632, benign FPR was 8.33%, factual utility loss was
8.33 percentage points, and paired answered-benign latency overhead
was 11.08%. Exact-marker attack success changed from 8.33% to 0%,
but only one attack succeeded in the undefended baseline.
These results do not demonstrate robustness against adaptive attacks.

See docs/unit6/README.md for execution instructions and limitations.
Raw observations, screenshots, and local models remain outside Git.

## Unit 5 baseline (historical)

The existing Unit 4 implementation remains in `core.py` and `demo.py` for
comparison. The Unit 5 entry point is `src.rag_guard.unit5_demo`. It uses a
frozen MiniLM encoder, a logistic head fitted on 48 authored synthetic examples,
and a sigmoid mapping fitted on 16 separate synthetic examples. It does not
train a foundation model. Rules produce original-document locations; they do
not explain the neural model's internal reasoning. Score calibration outside
this small development set has not been established.

At the end of Unit 5, downstream output was an extractive preview.
Unit 6 subsequently integrated local generation and completed the synthetic pilot.
BIPIA, held-out attack-family evaluation, adaptive attacks, and formal
ablation studies remain future work. Unit 2 targets remain provisional.

## Unit 5 reproduction (historical, Windows PowerShell)

From the repository folder, with Python 3.12 installed:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m tools.download_model
.\.venv\Scripts\python.exe -m pytest tests/unit5 -v
.\.venv\Scripts\python.exe -m src.rag_guard.unit5_demo "How do I reset a router safely?"
.\.venv\Scripts\python.exe -m src.rag_guard.unit5_demo "How do I reset a router safely?" --data config/attack_only.json
```

On Linux/macOS use `python3.12 -m venv .venv` and replace the executable with
`.venv/bin/python`. Installation requires internet. Inference uses the downloaded
model locally and makes no network requests. This is not an operating-system
network sandbox.

The approximately 91 MB model download is pinned to revision
`1110a243fdf4706b3f48f1d95db1a4f5529b4d41`. Model/tokenizer digests must match
the committed head. Model weights and virtual environments are not committed.
The official model card identifies an Apache 2.0 license for the pretrained model.

The head is already supplied as plain JSON. To refit it explicitly, run
`python -m tools.train_detector`. This replaces the head; review its diff and
rerun the checks before committing a new model version. Do not tune against a
future frozen benchmark test set.

## Evidence and limits

`python -m tools.capture_evidence` saves actual logs, JUnit XML, coverage JSON,
and a file/dependency manifest under `docs/evidence/unit5`. The recorded Windows 11
Python 3.12.10 run passed 70 Unit 5 cases and eleven inherited Unit 4 regression
cases.
The unit-only coverage run measured 146/206 statements (70.87%) and 46/60 branch destinations (76.67%) across the three new implementation modules. The combined Unit 5 suite reached 206/206 statements and 60/60 branch destinations (100%).
CLI scripts, dependencies, and inherited Unit 4 code are
outside this coverage denominator. Test runtime is not a latency benchmark.

Unit tests use deterministic stand-ins for model dependencies. Real-model
checks are separately marked `model`; missing assets fail rather than silently
skip. Test cases and development examples are not representative security data.
Token overflow, malformed scores, and processing exceptions withhold the whole
passage. Raised timeout exceptions are handled, but there is no hard wall-clock
supervisor for a hung inference process. Processing is bounded English text.
Quoted attacks and uncommon language can still be overblocked.

## Repository workflow

Unit 5 was integrated into `Development` and `main` through pull requests.
Unit 6 development uses `unit6-integration`, based on `Development`.
Integration should proceed through reviewed pull requests into `Development`
and then `main`, preserving the established commit history. Local tags and
prepared notes do not themselves create GitHub release pages. See `docs/releases`
for descriptions and publication status. Never force-push or move a published
tag to conceal changes.

Folders: `src/` code; `tests/` checks; `config/` synthetic fixtures and fitted head;
`design/` architecture; `docs/` requirements/evidence; `tools/` reproduction
commands; `results/` disposable output.
