"""Testy pipeline'u TF-IDF + MultinomialNB (bramka E3)."""

from __future__ import annotations

import pytest

from src import data, model


def test_v1_pipeline_trains_and_predicts() -> None:
    train, _ = data.load_split()
    pipeline = model.build_pipeline_v1()
    pipeline.fit(train["text"], train["label"])

    predictions = pipeline.predict(train["text"].head(5))
    assert len(predictions) == 5
    assert set(predictions) <= set(data.LABELS)
    proba = pipeline.predict_proba(train["text"].head(5))
    assert proba.shape == (5, 2)


def test_v1_uses_only_text_column() -> None:
    pipeline = model.build_pipeline_v1()
    assert list(pipeline.named_steps) == ["guard", "tfidf", "clf"]


def test_v1_cv_runs_and_beats_baseline_floor() -> None:
    """Bramka E3: CV działa; F1(spam) jest wyraźnie powyżej podłogi baseline (0.0)."""
    train, _ = data.load_split()
    cv = model.cross_validate_estimator(model.build_pipeline_v1, train)
    assert cv["n_splits"] == 5
    assert len(cv["folds"]) == 5
    assert cv["summary"]["f1_spam"]["mean"] > 0.5
    assert cv["summary"]["roc_auc"]["mean"] > 0.6


def test_v2_pipeline_uses_text_and_engineered_features() -> None:
    train, _ = data.load_split()
    pipeline = model.build_pipeline_v2()
    pipeline.fit(train["text"].head(40), train["label"].head(40))
    predictions = pipeline.predict(train["text"].head(10))
    assert set(predictions) <= set(data.LABELS)
    blocks = dict(pipeline.named_steps["features"].transformer_list)
    assert set(blocks) == {"text", "engineered"}


def test_v2_svc_has_no_predict_proba_but_has_decision_function() -> None:
    train, _ = data.load_split()
    pipeline = model.build_pipeline_v2_svc()
    pipeline.fit(train["text"].head(40), train["label"].head(40))
    assert not hasattr(pipeline, "predict_proba")
    assert hasattr(pipeline, "decision_function")


def test_v2_cv_clearly_beats_baseline() -> None:
    """Bramka E4: F1(spam) >> 0 (baseline) przy wszystkich wariantach v2."""
    train, _ = data.load_split()
    for key in ("v1_lr", "v2_char", "v2", "v2_svc"):
        cv = model.cross_validate_estimator(model.MODEL_FACTORIES[key], train)
        mean_f1 = cv["summary"]["f1_spam"]["mean"]
        assert mean_f1 > 0.85, f"{key}: f1_spam={mean_f1:.3f}"


def test_pipeline_never_receives_forbidden_columns() -> None:
    """Wejście pipeline'u to wyłącznie kolumna text (nie ramka z metadanymi)."""
    train, _ = data.load_split()
    features = data.feature_frame(train[["text"]])
    assert list(features.columns) == ["text"]
    with pytest.raises(data.DataValidationError):
        data.feature_frame(train)
    pipeline = model.build_pipeline_v2()
    pipeline.fit(features["text"].head(30), train["label"].head(30))
    with pytest.raises(ValueError, match="kolumnę 'text'"):
        pipeline.predict(train[["text", "message_id"]])
