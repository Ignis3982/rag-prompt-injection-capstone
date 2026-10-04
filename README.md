# Robust and Explainable Detection of Indirect Prompt Injection in Retrieval-Augmented Generation Systems

MSIT 5910 Capstone Project. Unit 5 adds a working local semantic classifier,
structural evidence, fusion, and a deterministic security gate. These are
research development components, not an experimentally validated defense.

## Current status

The existing Unit 4 implementation remains in `core.py` and `demo.py` for
comparison. The Unit 5 entry point is `src.rag_guard.unit5_demo`. It uses a
frozen MiniLM encoder, a logistic head fitted on 48 authored synthetic examples,
and a sigmoid mapping fitted on 16 separate synthetic examples. It does not
train a foundation model. Rules produce original-document locations; they do
not explain the neural model's internal reasoning. Score calibration outside
this small development set has not been established.

The downstream output is still an extractive preview. A genuine LLM baseline,
BIPIA integration, held-out family evaluation, adaptive attacks, utility/latency
measurement, and ablations remain outstanding. Unit 2 targets are unchanged
proposed evaluation criteria. No F1 or attack-success result is claimed here.

## Run on Windows PowerShell

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

The remote's existing branches are `main` and `Development` (capital D).
`unit5-core-logic` is the isolated Unit 5 working branch based on reviewed main.
Integrate it into Development, run CI, then merge through a pull request into
main. Preserve existing Unit 1–4 documents and commit history. Local tags and
prepared notes do not themselves create GitHub release pages. See `docs/releases`
for descriptions and publication status. Never force-push or move a published
tag to conceal changes.

Folders: `src/` code; `tests/` checks; `config/` synthetic fixtures and fitted head;
`design/` architecture; `docs/` requirements/evidence; `tools/` reproduction
commands; `results/` disposable output.
