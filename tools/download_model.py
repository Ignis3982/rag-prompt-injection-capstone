"""One-time public model download. Inference itself is local and offline."""
import json
from pathlib import Path
from huggingface_hub import hf_hub_download
from src.rag_guard.semantic import MODEL_ID, MODEL_REVISION

folder = Path("models/minilm")
for filename in ["onnx/model.onnx", "tokenizer.json", "config.json", "modules.json",
                 "sentence_bert_config.json", "1_Pooling/config.json", "README.md"]:
    path = hf_hub_download(MODEL_ID, filename, revision=MODEL_REVISION, local_dir=folder)
    print(filename, Path(path).stat().st_size, "bytes")
(folder / "revision.json").write_text(json.dumps(
    {"model_id": MODEL_ID, "revision": MODEL_REVISION}, indent=2) + "\n")
print("Model revision:", MODEL_REVISION)
