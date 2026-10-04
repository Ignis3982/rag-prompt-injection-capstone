# Unit 5 verification and validation plan

Verification asks whether module contracts hold. Broader validation asks
whether the defense protects the intended RAG task while preserving utility.
The present evidence supports the first and only bounded demonstrations of the
second. All expectations below were checked in actual runs.

| Requirement | Check and input | Expected behavior | Test location |
| --- | --- | --- | --- |
| FR-02 | Long passage and token overflow | Original offsets retained; overflow withheld | test_screening; test_model_integration |
| FR-03 | Low risk, rule matches, conflicting signals | Reproducible scores and uncertainty reasons | test_defense |
| FR-04 / NFR-04 | NaN, Boolean scores, raised timeout, no approved context | Reject malformed scores; quarantine failed passage; no answer | test_defense; test_screening |
| FR-06 | Known attack span and private exception marker | Correct offsets; no raw query/passage or exception text in audit | test_screening |
| NFR-07 | Duplicate rows, split leakage, changed encoder, JSON head | Reject contaminated partition or incompatible artifact | test_semantic |
| Utility safeguard | Ordinary citation URL | URL alone produces no structural alert; demonstrated case allowed | test_defense; test_model_integration |

The isolated suite contains 49 parametrized cases. The pipeline suite has 13
integration cases with a stub semantic scorer. Eight model/asset checks exercise
the actual encoder, normalization, token rejection, learned pipeline and committed
partition. Eleven older regression cases remain separate. A stub is an isolation
tool, not evidence that the real model is accurate.

Two defects identified during development concerned URL-only rule activation and
Boolean acceptance. The Unit 5 entry point uses corrected rules and strict finite
numeric validation. Legacy code is retained for historical comparison, not
presented as having acquired the new safeguards.

A coverage instrumentation issue was identified during development. Selecting the
source directory in `.coveragerc` resolved the problem. `tests.txt` records the
successful final Unit 5 run. No failed execution is presented as a successful
result.

Unit-only coverage over the three new modules: 146/206 statements (70.87%) and
46/60 branch destinations (76.67%). The security module alone reaches 100%.
Combined unit/integration/model coverage: 206/206 statements and 60/60 branches.
Coverage proves execution of those paths, not correctness of all inputs, model
robustness, or generalization. No coverage pragmas hide executable branches.

The retained verification evidence was regenerated on Windows 11 with Python
3.12.10. The complete Unit 5 suite collected 70 tests and passed successfully,
while the separate Unit 4 regression suite collected 11 tests and also passed.
To rerun only isolated cases use `python -m pytest tests/unit5/test_defense.py
tests/unit5/test_semantic.py -v`. Use `python -m tools.capture_evidence` for the
complete repeatable capture after downloading the model.

The 64 authored development records are explicitly split 48/16 and balanced
within each partition. Unique IDs/groups and normalized exact-text checks prevent
simple leakage; they do not establish independence of paraphrase families.
Representative calibration assessment and family-aware benchmark partitions are
required before interpreting scores as operational confidence. Thresholds
0.35/0.75 and disagreement 0.60 are versioned development policy settings.
