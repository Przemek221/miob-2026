"""Testy metryk i modelu odniesienia (bramka E2)."""

from __future__ import annotations

import numpy as np
import pytest

from src import data, evaluate, model


def test_report_format_and_perfect_scores() -> None:
    y_true = ["ham", "ham", "spam", "spam"]
    y_pred = ["ham", "ham", "spam", "spam"]
    y_proba = np.array([0.1, 0.2, 0.8, 0.9])
    result = evaluate.report(y_true, y_pred, y_proba, threshold=0.5)

    for key in evaluate.METRIC_KEYS:
        assert key in result
    assert result["accuracy"] == 1.0
    assert result["precision_spam"] == 1.0
    assert result["recall_spam"] == 1.0
    assert result["f1_spam"] == 1.0
    assert result["f1_macro"] == 1.0
    assert result["roc_auc"] == 1.0
    assert result["pr_auc"] == 1.0
    assert result["threshold"] == 0.5
    assert result["n_samples"] == 4
    assert result["labels"] == ["ham", "spam"]


def test_confusion_matrix_orientation() -> None:
    # 2 ham poprawnie, 1 spam jako ham (FN), 1 ham jako spam (FP)
    result = evaluate.report(
        ["ham", "ham", "spam", "ham"], ["ham", "ham", "ham", "spam"]
    )
    assert result["confusion_matrix"] == [[2, 1], [1, 0]]


def test_report_accepts_probability_matrix() -> None:
    y_true = ["ham", "spam"]
    y_pred = ["ham", "spam"]
    result = evaluate.report(y_true, y_pred, np.array([[0.9, 0.1], [0.2, 0.8]]))
    assert result["roc_auc"] == 1.0


def test_constant_scores_give_uninformative_auc_not_double_class_issue() -> None:
    """Stały score (baseline) daje AUC 0.5 — brak informacji, nie błąd."""
    result = evaluate.report(
        ["ham", "ham", "spam", "spam"], ["ham"] * 4, np.array([0.3, 0.3, 0.3, 0.3])
    )
    assert result["roc_auc"] == pytest.approx(0.5)
    assert result["f1_spam"] == 0.0


def test_single_class_truth_leaves_auc_empty() -> None:
    result = evaluate.report(["ham", "ham"], ["ham", "ham"], np.array([0.1, 0.2]))
    assert result["roc_auc"] is None
    assert result["pr_auc"] is None


def test_mean_and_std_of_folds() -> None:
    folds = [
        {"f1_spam": 1.0, "roc_auc": None},
        {"f1_spam": 0.5, "roc_auc": None},
    ]
    summary = evaluate.mean_and_std(folds)
    assert summary["f1_spam"] == {"mean": 0.75, "std": 0.25, "n_folds": 2}
    assert summary["roc_auc"]["mean"] is None
    assert summary["roc_auc"]["n_folds"] == 0


def test_baseline_predicts_majority_class_only() -> None:
    train, _ = data.load_split()
    baseline = model.build_baseline()
    baseline.fit(train["text"], train["label"])
    predictions = set(baseline.predict(train["text"]))
    assert predictions == {"ham"}


def test_baseline_cv_on_train_has_zero_spam_f1() -> None:
    """Podłoga: baseline nie wykrywa spamu, więc F1(spam) = 0 w każdym foldzie."""
    train, _ = data.load_split()
    cv = model.cross_validate_estimator(model.build_baseline, train)
    assert cv["n_splits"] == 5
    assert len(cv["folds"]) == 5
    assert cv["summary"]["f1_spam"]["mean"] == 0.0
    # Baseline zgaduje wszystkie wiadomości jako 'ham' -> accuracy = udział ham w foldach testowych.
    assert 0.6 < cv["summary"]["accuracy"]["mean"] < 0.8
