"""Integrated local research application retaining the Unit 5 detector."""
from dataclasses import asdict
from time import perf_counter
import hashlib
import json
import uuid

from src.rag_guard.core import Document
from src.rag_guard.defense import Evidence, Policy, probability
from src.rag_guard.screening import ScreeningPipeline
from src.rag_guard.semantic import SemanticScorer
from src.rag_guard.generation import OllamaGenerator, GenerationError

MODES = ("undefended", "rules", "semantic", "hybrid")


class BaselineDetector:
    """Single-signal comparators with documented, fixed decision thresholds."""
    def __init__(self, hybrid, mode):
        self.hybrid, self.mode, self.policy = hybrid, mode, hybrid.policy

    def detect(self, text):
        if self.mode == "undefended":
            return Evidence(0.0, 0.0, 0.0, False, ("screening_disabled",), ())
        if self.mode == "rules":
            risk, matches = self.hybrid.rules.score(text)
            semantic, structural = 0.0, risk
            reasons = tuple(dict.fromkeys(m.code for m in matches))
        else:
            risk = semantic = probability(self.hybrid.semantic.score(text))
            structural, matches, reasons = 0.0, (), ("semantic_only",)
        margin = self.policy.allow_below <= risk < self.policy.block_at
        return Evidence(semantic, structural, risk, margin, reasons, matches)


class IntegratedRAG:
    def __init__(self, documents, semantic, generator, mode="hybrid", policy=None):
        if mode not in MODES:
            raise ValueError("Unknown experimental mode")
        self.mode, self.generator = mode, generator
        self.pipeline = ScreeningPipeline(documents, semantic, policy or Policy())
        if mode != "hybrid":
            self.pipeline.detector = BaselineDetector(self.pipeline.detector, mode)

    def run(self, query, top_k=3):
        started = perf_counter()
        result = self.pipeline.run(query, top_k)
        screening_ms = (perf_counter() - started) * 1000
        approved = result["approved_context"]
        answer = "Insufficient approved context. No answer produced."
        status, error, generation_ms = "abstained", None, 0.0
        if approved:
            generation_started = perf_counter()
            try:
                answer = self.generator.generate(query, approved)
                status = "answered"
            except GenerationError as exc:
                answer, status = "Generation unavailable. No answer produced.", "generation_error"
                error = str(exc)
            generation_ms = (perf_counter() - generation_started) * 1000
        audit = result["audit"]
        audit.update({"schema": "unit6-runtime-v1", "run_id": str(uuid.uuid4()),
                      "mode": self.mode, "status": status,
                      "screening_ms": screening_ms, "generation_ms": generation_ms,
                      "total_ms": (perf_counter() - started) * 1000,
                      "generation_error": error,
                      "scope": "local_research_prototype_not_production"})
        return {"answer": answer, "audit": audit}


def build_app(documents, mode="hybrid", generator=None):
    semantic = SemanticScorer.from_files("models/minilm", "config/semantic_head.json")
    app = IntegratedRAG(documents, semantic, generator or OllamaGenerator(), mode)
    return app


def case_documents(case):
    return [Document(case["id"], case["topic"], case["text"], "unit6-synthetic-pilot")]


def print_result(result):
    audit = result["audit"]
    print("Mode:", audit["mode"], "| Status:", audit["status"])
    for decision in audit["decisions"]:
        print("Passage:", decision["document_id"], decision["decision"].upper())
        for window in decision["windows"]:
            print("  semantic={:.4f} rules={:.4f} risk={:.4f}".format(
                window["semantic"], window["structural"], window["risk"]))
            print("  Reasons:", ", ".join(window["reasons"]) or "below review band")
            print("  Evidence offsets:", window["locations"])
    print("Answer:", result["answer"])
    print("Total milliseconds: {:.2f}".format(audit["total_ms"]))
    print("Rule offsets explain rule matches; they are not neural attributions.")
