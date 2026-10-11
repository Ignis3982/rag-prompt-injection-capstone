"""Inspect required local components without publishing or storing evidence."""
import json
import platform
import importlib.metadata
from src.rag_guard.semantic import SemanticScorer
from src.rag_guard.generation import OllamaGenerator


def main():
    print("System:", platform.system(), platform.release(), platform.version())
    print("Python:", platform.python_version(), "| Machine:", platform.machine())
    for name in ("numpy", "scipy", "scikit-learn", "onnxruntime", "tokenizers", "huggingface-hub"):
        print(name, importlib.metadata.version(name))
    scorer = SemanticScorer.from_files("models/minilm", "config/semantic_head.json")
    print("Encoder assets match the fitted head:", json.dumps(scorer.encoder.fingerprint))
    print("Generator identity:", json.dumps(OllamaGenerator().identity(), indent=2))
    print("Setup inspection completed. This is not a performance evaluation.")


if __name__ == "__main__":
    main()
