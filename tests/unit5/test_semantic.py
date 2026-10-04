import copy
import json
from pathlib import Path
import numpy as np
import pytest
from src.rag_guard.semantic import SemanticScorer, fit_head, validate_partitions, sha256_file


class TinyEncoder:
    dimension = 2
    fingerprint = {'test_encoder': 'v1'}

    def encode(self, texts):
        return np.asarray([[1.,0.] if t.startswith('attack') else [0.,1.] for t in texts])


def records():
    return [{'id':str(i), 'group':str(i), 'label':label, 'split':split,
             'text':f'{"attack" if label else "benign"} case {i}'}
            for i,(split,label) in enumerate([
                ('train',0),('train',0),('train',1),('train',1),
                ('calibration',0),('calibration',1)])]


def test_disjoint_development_partition():
    split = validate_partitions(records())
    assert len(split['train']) == 4 and len(split['calibration']) == 2


@pytest.mark.parametrize('change', ['duplicate_id','duplicate_text','group_leak','invalid_split','invalid_label','empty_text','single_class'])
def test_partition_defects_rejected(change):
    rows = records()
    if change == 'duplicate_id': rows[-1]['id'] = rows[0]['id']
    if change == 'duplicate_text': rows[-1]['text'] = rows[0]['text'].upper()
    if change == 'group_leak': rows[-1]['group'] = rows[0]['group']
    if change == 'invalid_split': rows[-1]['split'] = 'test'
    if change == 'invalid_label': rows[-1]['label'] = True
    if change == 'empty_text': rows[-1]['text'] = ' '
    if change == 'single_class': rows[-1]['label'] = 0
    with pytest.raises(ValueError):
        validate_partitions(rows)


def test_fitted_head_orders_scores_and_roundtrips_json(tmp_path):
    encoder = TinyEncoder()
    artifact = fit_head(records(), encoder)
    path = tmp_path/'head.json'
    path.write_text(json.dumps(artifact))
    scorer = SemanticScorer(encoder, json.loads(path.read_text()))
    assert 0 <= scorer.score('benign item') < scorer.score('attack item') <= 1
    assert len(sha256_file(path)) == 64


@pytest.mark.parametrize('change',['schema','encoder','shape','nan_weights','negative_slope','nan_intercept'])
def test_invalid_artifact_is_rejected(change):
    artifact = fit_head(records(), TinyEncoder())
    if change == 'schema': artifact['schema'] = 'wrong'
    if change == 'encoder': artifact['encoder'] = {'other':1}
    if change == 'shape': artifact['weights'] = [1.]
    if change == 'nan_weights': artifact['weights'][0] = float('nan')
    if change == 'negative_slope': artifact['calibration_slope'] = -1
    if change == 'nan_intercept': artifact['intercept'] = float('nan')
    with pytest.raises(ValueError):
        SemanticScorer(TinyEncoder(), artifact)


def test_nonfinite_embedding_fails():
    encoder = TinyEncoder()
    scorer = SemanticScorer(encoder, fit_head(records(), encoder))
    encoder.encode = lambda texts: np.asarray([[float('nan'),0.]])
    with pytest.raises(ValueError):
        scorer.score('input')
