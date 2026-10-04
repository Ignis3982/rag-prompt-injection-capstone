"""Unit 5 integration boundary; generation is still an extractive preview."""
from dataclasses import asdict
import hashlib
import json
import uuid

from src.rag_guard.core import Preprocessor, RetrievalIndex
from src.rag_guard.defense import HybridDetector, SecurityGate


class ScreeningPipeline:
    def __init__(self, documents, semantic, policy=None):
        self.index = RetrievalIndex(documents)
        self.preprocessor = Preprocessor()
        self.detector = HybridDetector(semantic, policy)
        self.gate = SecurityGate(self.detector.policy)
        self.corpus_sha256 = hashlib.sha256(json.dumps(
            [asdict(d) for d in self.index.documents], sort_keys=True
        ).encode()).hexdigest()

    def run(self, query, top_k=3):
        if not isinstance(query, str) or not query.strip() or len(query) > 2000:
            raise ValueError("A query of 1 to 2000 characters is required")
        if type(top_k) is not int or not 1 <= top_k <= 20:
            raise ValueError("top_k must be an integer from 1 to 20")
        approved, decisions = [], []
        for document in self.index.search(query, top_k):
            windows = []
            try:
                for window in self.preprocessor.split(document.text):
                    evidence = self.detector.detect(window.text)
                    decision = self.gate.decide(evidence)
                    # Window-relative matches become original-document offsets.
                    locations = [{"code": m.code, "start": m.start + window.start,
                                  "end": m.end + window.start} for m in evidence.matches]
                    windows.append({"start": window.start, "end": window.end,
                                    "decision": decision, "semantic": evidence.semantic,
                                    "structural": evidence.structural, "risk": evidence.risk,
                                    "uncertain": evidence.uncertain,
                                    "reasons": evidence.reasons, "locations": locations})
                severity = {"allow": 0, "quarantine": 1, "block": 2}
                decision = max((w["decision"] for w in windows), key=severity.get)
                reason = "completed_screening"
            except Exception as exc:
                decision, reason = "quarantine", "processing_failure:" + type(exc).__name__
            decisions.append({"document_id": document.document_id, "decision": decision,
                              "reason": reason, "windows": windows})
            if decision == "allow":
                approved.append(document.text)
        audit = {"schema": "screening-audit-v1", "run_id": str(uuid.uuid4()),
                 "query_length": len(query), "policy": asdict(self.detector.policy),
                 "corpus_sha256": self.corpus_sha256, "decisions": decisions,
                 "approved_count": len(approved),
                 "scope": "synthetic_functional_validation_not_security_benchmark"}
        response = ("Approved context preview (no LLM): " + " ".join(approved[:2])
                    if approved else "Insufficient approved context. No answer produced.")
        return {"approved_context": approved, "response": response, "audit": audit}
