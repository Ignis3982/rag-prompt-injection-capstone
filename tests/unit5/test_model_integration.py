import json
from pathlib import Path
import numpy as np
import pytest
from src.rag_guard.core import load_documents
from src.rag_guard.semantic import MiniLMEncoder, SemanticScorer, validate_partitions
from src.rag_guard.screening import ScreeningPipeline

pytestmark = pytest.mark.model


@pytest.fixture(scope='module')
def scorer():
    # Missing assets are an error for this explicit model suite, never a silent skip.
    return SemanticScorer.from_files('models/minilm','config/semantic_head.json')


def test_real_encoder_normalized_repeatable_and_batch_invariant(scorer):
    encoder = scorer.encoder
    text = 'Restart the router.'
    one = encoder.encode([text])[0]
    batch = encoder.encode([text,'The longer article discusses several documentation changes.'])[0]
    assert one.shape == (384,) and np.linalg.norm(one) == pytest.approx(1,abs=1e-6)
    np.testing.assert_allclose(one,batch,atol=1e-6)


@pytest.mark.parametrize('texts',[[],[''],['router '*300]])
def test_encoder_rejects_empty_or_overbudget_input_without_truncation(scorer,texts):
    with pytest.raises(ValueError):
        scorer.encoder.encode(texts)


def test_real_model_mixed_corpus_screening(scorer):
    result = ScreeningPipeline(load_documents('config/fixtures.json'),scorer).run('How do I reset a router safely?')
    decisions = {d['document_id']:d['decision'] for d in result['audit']['decisions']}
    assert decisions['benign-router-01'] == 'allow'
    assert decisions['injection-router-01'] in ('quarantine','block')
    assert all('https://example.invalid' not in p for p in result['approved_context'])


def test_real_model_attack_only_fallback(scorer):
    result = ScreeningPipeline(load_documents('config/attack_only.json'),scorer).run('router')
    assert result['approved_context'] == [] and 'No answer produced' in result['response']


def test_real_model_reference_url_regression(scorer):
    from src.rag_guard.defense import HybridDetector, SecurityGate
    e = HybridDetector(scorer).detect('Router manual: see https://example.invalid/manual for restart instructions.')
    assert e.structural == 0 and SecurityGate().decide(e) == 'allow'


def test_committed_partition_is_disjoint():
    split = validate_partitions(json.loads(Path('config/unit5_development.json').read_text()))
    assert len(split['train']) == 48 and len(split['calibration']) == 16
