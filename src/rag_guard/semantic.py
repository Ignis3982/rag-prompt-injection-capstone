"""Local frozen MiniLM embeddings and a fitted linear classification head.

No pickle loading, model download, or network use occurs during inference.
The small synthetic development set establishes operability, not robustness.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.special import expit
from sklearn.linear_model import LogisticRegression

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class MiniLMEncoder:
    """Attention-mask mean pooling followed by L2 normalization on CPU."""

    dimension = 384
    max_tokens = 256

    def __init__(self, model_dir):
        import onnxruntime as ort
        from tokenizers import Tokenizer

        folder = Path(model_dir)
        self.tokenizer = Tokenizer.from_file(str(folder / "tokenizer.json"))
        self.tokenizer.no_truncation()
        self.tokenizer.enable_padding(pad_id=0, pad_token="[PAD]")
        options = ort.SessionOptions()
        options.intra_op_num_threads = 2
        self.session = ort.InferenceSession(
            str(folder / "onnx/model.onnx"), options,
            providers=["CPUExecutionProvider"],
        )
        self.fingerprint = {
            "model_id": MODEL_ID, "revision": MODEL_REVISION,
            "onnx_sha256": sha256_file(folder / "onnx/model.onnx"),
            "tokenizer_sha256": sha256_file(folder / "tokenizer.json"),
        }

    def encode(self, texts):
        if not texts or any(not isinstance(t, str) or not t.strip() for t in texts):
            raise ValueError("Nonempty texts required")
        encoded = self.tokenizer.encode_batch(texts)
        if any(sum(e.attention_mask) > self.max_tokens for e in encoded):
            raise ValueError("Token budget exceeded; content was not truncated")
        feeds = {
            "input_ids": np.asarray([e.ids for e in encoded], dtype=np.int64),
            "attention_mask": np.asarray([e.attention_mask for e in encoded], dtype=np.int64),
            "token_type_ids": np.asarray([e.type_ids for e in encoded], dtype=np.int64),
        }
        feeds = {i.name: feeds[i.name] for i in self.session.get_inputs()}
        output = self.session.run(None, feeds)[0]
        mask = feeds["attention_mask"][..., None]
        pooled = (output * mask).sum(axis=1) / mask.sum(axis=1)
        return pooled / np.maximum(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-12)


def validate_partitions(records):
    """Reject exact duplicate content, IDs, group leakage, and invalid labels."""
    ids, texts, groups = set(), set(), {}
    splits = {"train": [], "calibration": []}
    for row in records:
        if (row["split"] not in splits or type(row["label"]) is not int
                or row["label"] not in (0, 1) or not row["text"].strip()):
            raise ValueError("Invalid development record")
        normalized = " ".join(row["text"].casefold().split())
        if row["id"] in ids or normalized in texts:
            raise ValueError("Duplicate development record")
        ids.add(row["id"])
        texts.add(normalized)
        group = row["group"]
        if group in groups and groups[group] != row["split"]:
            raise ValueError("Group leakage between training and calibration")
        groups[group] = row["split"]
        splits[row["split"]].append(row)
    if any({r["label"] for r in rows} != {0, 1} for rows in splits.values()):
        raise ValueError("Both classes required in each split")
    return splits


def fit_head(records, encoder):
    splits = validate_partitions(records)
    train, calibration = splits["train"], splits["calibration"]
    x_train = encoder.encode([r["text"] for r in train])
    x_cal = encoder.encode([r["text"] for r in calibration])
    classifier = LogisticRegression(C=2.0, random_state=5910, max_iter=1000)
    classifier.fit(x_train, [r["label"] for r in train])
    # Independent records fit a sigmoid mapping; quality still requires evaluation.
    calibrator = LogisticRegression(C=1.0, random_state=5910)
    calibrator.fit(classifier.decision_function(x_cal).reshape(-1, 1),
                   [r["label"] for r in calibration])
    return {
        "schema": "semantic-head-v1", "seed": 5910,
        "weights": classifier.coef_[0].tolist(),
        "intercept": float(classifier.intercept_[0]),
        "calibration_slope": float(calibrator.coef_[0, 0]),
        "calibration_intercept": float(calibrator.intercept_[0]),
        "encoder": encoder.fingerprint,
        "train_count": len(train), "calibration_count": len(calibration),
        "scope": "synthetic_development_only_not_benchmark",
    }


class SemanticScorer:
    def __init__(self, encoder, artifact):
        self.encoder = encoder
        self.artifact = artifact
        if artifact.get("schema") != "semantic-head-v1":
            raise ValueError("Unknown head schema")
        if artifact["encoder"] != encoder.fingerprint:
            raise ValueError("Encoder artifact mismatch")
        self.weights = np.asarray(artifact["weights"], dtype=float)
        self.parameters = np.asarray([
            artifact["intercept"], artifact["calibration_slope"],
            artifact["calibration_intercept"],
        ], dtype=float)
        if self.weights.shape != (encoder.dimension,) or not np.isfinite(self.weights).all():
            raise ValueError("Invalid classifier coefficients")
        if not np.isfinite(self.parameters).all() or self.parameters[1] <= 0:
            raise ValueError("Invalid sigmoid calibration")

    def score(self, text):
        embedding = self.encoder.encode([text])[0]
        logit = float(embedding @ self.weights + self.parameters[0])
        score = float(expit(self.parameters[1] * logit + self.parameters[2]))
        if not np.isfinite(score):
            raise ValueError("Nonfinite model output")
        return score

    @classmethod
    def from_files(cls, model_dir, artifact_path):
        return cls(MiniLMEncoder(model_dir), json.loads(Path(artifact_path).read_text()))
