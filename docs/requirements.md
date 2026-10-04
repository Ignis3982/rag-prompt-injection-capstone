Proposed requirements. No acceptance tests or experimental targets have yet been demonstrated.

Functional Requirements

FR-01: M1 shall return the configured number of available passages with document identifiers, ranks, and the corpus version, while preserving the original query separately.

FR-02: M2 shall preserve original offsets, create bounded overlapping windows, and flag incomplete or invalid processing without silently treating it as safe.

FR-03: M3–M5 shall emit semantic scores, rule matches, a fused risk score, and a versioned uncertainty decision for every inspected passage.

FR-04: M6 shall allow low-risk passages, quarantine uncertain passages, and block high-risk passages. Processing failures shall withhold affected content; absence of approved context shall prevent substantive generation.

FR-05: M7 shall generate from the user task and approved context only, without executing retrieved instructions as tools or network actions.

FR-06: M8 shall record decision reasons, redacted evidence locations, run identifiers, and processing errors without storing credentials or unrestricted raw prompts.

FR-07: M9 shall execute matched baseline, hybrid, and ablation runs and export metrics with configurations, seeds, split identifiers, model revisions, and the code revision.

Non-Functional Requirements

NFR-01, detection quality: proposed targets are F1 ≥ 0.90 and benign false-positive rate ≤ 5%. A withheld benign passage counts as a false positive, including quarantine. Verification uses the frozen test partition; coverage and failure counts accompany the scores.

NFR-02, security and utility: proposed targets are at least 50% relative attack-success reduction against the undefended pipeline and at most five percentage points of benign task-utility loss. Matched queries and identical generator settings establish the comparison; a zero baseline attack-success rate makes relative reduction undefined.

NFR-03, performance: proposed median latency overhead is ≤ 25%, measured as the relative increase in median end-to-end time against the matched baseline. Warm-up, hardware, sample size, and tail latency will also be reported.

NFR-04, reliability and security: injected timeout, malformed-input, and detector-error tests shall show no unsafe fallback. Local account permissions protect artifacts; generation receives no secrets, tools, or outbound network capability.

NFR-05, usability: every withheld query shall return a readable status and trace identifier. A fixture review shall confirm that explanations distinguish risk evidence from certainty about attacker intent.

NFR-06, maintainability and scale: detector modules shall share versioned input/output schemas and process bounded batches. Swapping a baseline shall require configuration changes rather than changes to retrieval or generation. Batch memory and throughput will be characterized; production scalability is outside scope.

NFR-07, reproducibility: a clean environment shall reconstruct one documented run from pinned dependencies, accessible data manifests, seeds, and a code revision. Numeric tolerances and nondeterministic components shall be disclosed. Calibration and decision thresholds will be fixed before test evaluation.