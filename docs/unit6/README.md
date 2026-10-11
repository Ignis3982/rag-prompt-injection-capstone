# Unit 6 local integration and pilot evaluation

This addition connects the existing Unit 5 screening pipeline to local Ollama
chat generation. It does not replace Unit 4 or Unit 5 source, models, evidence,
Git history, tags, or release information. Review the source before adopting it.

Run all commands from the project root using Python 3.12. Existing Python
requirements remain in requirements-dev.txt. Windows Python includes Tkinter
for the optional desktop interface. The CLI is also supported.

```powershell
.\.venv\Scripts\python.exe -m tools.unit6_check_base
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest tests/unit6 tests/unit5 tests/test_core.py -q
.\.venv\Scripts\python.exe -m tools.unit6_doctor
.\.venv\Scripts\python.exe -m tools.unit6_demo --case clean-01
.\.venv\Scripts\python.exe -m tools.unit6_demo --case attack-01
.\.venv\Scripts\python.exe -m tools.unit6_ui
.\.venv\Scripts\python.exe -m tools.unit6_evaluate --local-run
```

Install Ollama from its official site and download qwen2.5:1.5b before running
these commands. The generator uses http://127.0.0.1:11434 only, without proxies,
redirects, or model tools. Set OLLAMA_NO_CLOUD=1 and OLLAMA_HOST=127.0.0.1:11434
in the Ollama server environment, then restart that server. No API key is used.
The application does not configure an operating-system network sandbox.

The generator checks its model digest before and after each call. Installation
requires internet; generation uses local weights. Model failures are reported
as errors, not as successful security decisions. No-context cases do not call
the model. A socket timeout limits a stalled API request; the inherited semantic
inference still has no independent hard process deadline.

The pilot contains 24 authored synthetic cases in 12 benign/attack pairs. It is
not BIPIA, an adaptive attack study, or a population-level security benchmark.
The detector head and policy remain frozen. Four modes use the same retrieval
and generation settings. The full run uses three timing repetitions, yielding
288 requests. Classification and generation outcomes use the preselected first
repetition of each case; repetitions do not enlarge the independent sample.

F1 and false-positive rate treat block and quarantine as positive detection.
Processing failures are counted separately. Exact injected-marker presence and
answer-substring presence are narrow automatic proxies for attack success and
fact utility; inspect all answers manually before making broader claims.
Zero baseline ASR produces an undefined relative reduction, not a 100% gain.
Overall latency includes abstentions. Paired answered-benign overhead is the
ratio of medians over matched completed requests, with its pair count recorded.

Each invocation writes a new results/unit6_local subfolder. Do not commit this
folder. Results, screenshots, charts, or evidence need explicit review and
approval before any later inclusion in Git. Add /results/unit6_local/ to the
local Git exclude file before running. A generated summary is not a claim of
publication, CI success, or user approval.

After completing the full run, make the real results chart with:

```powershell
.\.venv\Scripts\python.exe -m tools.unit6_chart results/unit6_local/YOUR_RUN_FOLDER
```

The script refuses a partial run, generation failures, or a changed observation
file. It creates an SVG from measured data. It does not create screenshots.
Open the SVG locally and insert it into the report after reviewing the data.

Assess explanation clarity through a documented self-inspection of clean-01,
attack-01, and clean-08. Record what was understandable, any ambiguous reason,
and one actionable improvement, with a genuine screenshot for each relevant
finding. This is a developer inspection, not a participant study.

No Unit 6 results, release, tag, CI outcome, or public publication are claimed
in this source addition. Benchmark validation and independent user research
remain future work.
