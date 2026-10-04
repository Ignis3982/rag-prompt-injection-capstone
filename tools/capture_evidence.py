"""Run real checks and save unedited stdout plus a reproduction manifest."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime, timezone

out = Path('docs/evidence/unit5')
out.mkdir(parents=True, exist_ok=True)
commands = [
    ('unit_tests.txt', ['-m','pytest','tests/unit5/test_defense.py','tests/unit5/test_semantic.py','-v','--no-header','--no-summary',
     '--cov=src/rag_guard','--cov-branch','--cov-report=term-missing',
     '--cov-report=json:docs/evidence/unit5/unit_coverage.json']),
    ('tests.txt', ['-m','pytest','tests/unit5','-v','--no-header','--no-summary','--cov=src/rag_guard','--cov-branch',
     '--cov-report=term-missing','--cov-report=json:docs/evidence/unit5/coverage.json',
     '--junitxml=docs/evidence/unit5/junit.xml']),
    ('unit4_regression.txt', ['-m','pytest','tests/test_core.py','-v','--no-header','--no-summary']),
    ('mixed_demo.txt', ['-m','src.rag_guard.unit5_demo','How do I reset a router safely?',
     '--output','docs/evidence/unit5/mixed_audit.json']),
    ('attack_only_demo.txt', ['-m','src.rag_guard.unit5_demo','How do I reset a router safely?',
     '--data','config/attack_only.json','--output','docs/evidence/unit5/attack_only_audit.json']),
]
executions = []
for filename, args in commands:
    proc = subprocess.run([sys.executable,*args],text=True,capture_output=True)
    (out/filename).write_text(proc.stdout + proc.stderr,encoding='utf-8')
    executions.append({'command':['python',*args],'log':filename,'exit_code':proc.returncode})
    print(filename, 'PASS' if proc.returncode == 0 else 'FAIL')
    if proc.returncode:
        print(proc.stdout[-2000:],proc.stderr[-1000:])
        raise SystemExit(proc.returncode)
paths = [Path(p) for p in ['src/rag_guard/defense.py','src/rag_guard/semantic.py',
    'src/rag_guard/screening.py','src/rag_guard/unit5_demo.py','config/unit5_development.json',
    'config/semantic_head.json','config/fixtures.json','config/attack_only.json',
    'requirements.txt','requirements-dev.txt','.coveragerc']]
manifest = {
    'captured_utc':datetime.now(timezone.utc).isoformat(),
    'platform':platform.platform(),'python':platform.python_version(),
    'packages':{p:importlib.metadata.version(p) for p in [
        'scikit-learn','numpy','scipy','onnxruntime','tokenizers','huggingface-hub',
        'pytest','pytest-cov','coverage']},
    'files_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
    'executions':executions,
    'scope':'functional checks, not benchmark effectiveness or security certification',
}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Manifest saved. No remote GitHub Actions run is asserted.')
