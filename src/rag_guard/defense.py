"""Versioned hybrid evidence and deterministic policy for untrusted passages."""
from __future__ import annotations

import math
import re
from dataclasses import dataclass


def probability(value):
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or not 0 <= value <= 1):
        raise ValueError("A finite numeric score from zero to one is required")
    return float(value)


@dataclass(frozen=True)
class Match:
    code: str
    start: int
    end: int


@dataclass(frozen=True)
class Evidence:
    semantic: float
    structural: float
    risk: float
    uncertain: bool
    reasons: tuple[str, ...]
    matches: tuple[Match, ...]


@dataclass(frozen=True)
class Policy:
    version: str = "unit5-policy-v1"
    allow_below: float = 0.35
    block_at: float = 0.75
    disagreement_at: float = 0.60
    semantic_weight: float = 0.70

    def __post_init__(self):
        for v in (self.allow_below, self.block_at, self.disagreement_at, self.semantic_weight):
            probability(v)
        if not 0 < self.allow_below < self.block_at < 1:
            raise ValueError("Invalid threshold ordering")


class RuleScorer:
    # Rules record locations, never copies of the potentially sensitive text.
    rules = (
        ("instruction_override", r"\b(?:ignore|disregard)\s+(?:(?:all|the)\s+)?(?:previous\s+instructions|user(?:'s)?\s+(?:request|question))", 0.55),
        ("sensitive_disclosure", r"\b(?:reveal|print|disclose)\s+(?:(?:the|all)\s+)?(?:system\s+prompt|secret(?:s)?|credentials|private\s+records)", 0.55),
        ("role_spoofing", r"(?:\[SYSTEM\]|<\|system\|>|\bsystem\s+override\s*:)", 0.55),
        ("exfiltration", r"\b(?:send|upload|transmit)\b[^.!?\n]{0,120}\b(?:https?://|external\s+(?:address|endpoint)|email\s+address)", 0.70),
    )

    def score(self, text):
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Nonempty passage required")
        matches, weight = [], 0.0
        for code, pattern, increment in self.rules:
            found = list(re.finditer(pattern, text, re.IGNORECASE))
            if found:
                weight += increment
                matches.extend(Match(code, m.start(), m.end()) for m in found)
        return min(1.0, weight), tuple(matches)


class HybridDetector:
    def __init__(self, semantic, policy=None):
        self.semantic = semantic
        self.policy = policy or Policy()
        self.rules = RuleScorer()

    def detect(self, text):
        semantic = probability(self.semantic.score(text))
        structural, matches = self.rules.score(text)
        weight = self.policy.semantic_weight
        risk = weight * semantic + (1 - weight) * structural
        disagreement = abs(semantic - structural) >= self.policy.disagreement_at
        margin = self.policy.allow_below <= risk < self.policy.block_at
        reasons = tuple(dict.fromkeys(m.code for m in matches))
        if disagreement:
            reasons += ("signal_disagreement",)
        if margin:
            reasons += ("review_band",)
        return Evidence(semantic, structural, risk, disagreement or margin,
                        reasons, matches)


class SecurityGate:
    def __init__(self, policy=None):
        self.policy = policy or Policy()

    def decide(self, evidence):
        if not isinstance(evidence, Evidence) or type(evidence.uncertain) is not bool:
            raise ValueError("Invalid detector result")
        for score in (evidence.semantic, evidence.structural, evidence.risk):
            probability(score)
        if evidence.uncertain:
            return "quarantine"
        if evidence.risk >= self.policy.block_at:
            return "block"
        if evidence.risk >= self.policy.allow_below:
            return "quarantine"
        return "allow"
