"""Metryki, macierz pomyłek i zapis raportów.

Kontrakt (plan.md, sekcja 4):

    evaluate.report(y_true, y_pred, y_proba) -> dict

Format JSON jest wspólny dla baseline (E2), CV (E3–E5) i oceny końcowej (E6),
dzięki czemu wyniki można porównywać bez tłumaczenia kluczy.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn import metrics

from .data import LABELS

POSITIVE_LABEL = "spam"
NEGATIVE_LABEL = "ham"

#: Klucze metryk liczbowych w `report()` (bez progu i macierzy pomyłek).
METRIC_KEYS: tuple[str, ...] = (
    "accuracy",
    "precision_spam",
    "recall_spam",
    "f1_spam",
    "f1_macro",
    "roc_auc",
    "pr_auc",
)


def _score_for_positive_class(y_proba: np.ndarray | None) -> np.ndarray | None:
    """Zamienia ``predict_proba`` na wektor score'ów klasy ``spam``.

    Obsługuje zarówno dwukolumnową macierz ``[P(ham), P(spam)]``, jak i wektor
    prawdopodobieństw klasy pozytywnej.
    """
    if y_proba is None:
        return None
    array = np.asarray(y_proba, dtype=float)
    if array.ndim == 2:
        return array[:, 1]
    return array.ravel()


def report(y_true, y_pred, y_proba=None, threshold: float | None = None) -> dict:
    """Liczy metryki w ustalonym formacie.

    Args:
        y_true: etykiety prawdziwe (``ham``/``spam``).
        y_pred: etykiety przewidziane (po zastosowaniu progu, jeśli dotyczy).
        y_proba: opcjonalne prawdopodobieństwa/score'y klasy ``spam``.
        threshold: próg decyzyjny użyty do wygenerowania ``y_pred`` (do zapisu).

    Returns:
        dict z kluczami ``METRIC_KEYS`` + ``confusion_matrix``, ``threshold``,
        ``labels``, ``n_samples`` i liczebnościami klas.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if y_true.shape != y_pred.shape:
        raise ValueError(f"y_true i y_pred różnią się kształtem: {y_true.shape} vs {y_pred.shape}")

    scores = _score_for_positive_class(y_proba)

    result: dict = {
        "accuracy": float(metrics.accuracy_score(y_true, y_pred)),
        "precision_spam": float(
            metrics.precision_score(y_true, y_pred, pos_label=POSITIVE_LABEL, zero_division=0)
        ),
        "recall_spam": float(
            metrics.recall_score(y_true, y_pred, pos_label=POSITIVE_LABEL, zero_division=0)
        ),
        "f1_spam": float(
            metrics.f1_score(y_true, y_pred, pos_label=POSITIVE_LABEL, zero_division=0)
        ),
        "f1_macro": float(metrics.f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "roc_auc": None,
        "pr_auc": None,
        "confusion_matrix": metrics.confusion_matrix(y_true, y_pred, labels=list(LABELS)).tolist(),
        "labels": list(LABELS),
        "threshold": None if threshold is None else float(threshold),
        "n_samples": int(len(y_true)),
        "n_true": {label: int((y_true == label).sum()) for label in LABELS},
        "n_pred": {label: int((y_pred == label).sum()) for label in LABELS},
    }

    if scores is not None:
        has_both_classes = len(set(y_true.tolist())) == 2
        if has_both_classes:
            result["roc_auc"] = float(metrics.roc_auc_score(y_true == POSITIVE_LABEL, scores))
            result["pr_auc"] = float(
                metrics.average_precision_score(y_true == POSITIVE_LABEL, scores)
            )

    return result


def mean_and_std(folds: list[dict]) -> dict:
    """Agreguje listę raportów z foldów: średnia i odchylenie standardowe metryk."""
    summary: dict = {}
    for key in METRIC_KEYS:
        values = [fold[key] for fold in folds if fold.get(key) is not None]
        if values:
            summary[key] = {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "n_folds": len(values),
            }
        else:
            summary[key] = {"mean": None, "std": None, "n_folds": 0}
    return summary


def save_json(payload: dict, path: str | Path) -> Path:
    """Zapisuje JSON (UTF-8, wcięty, klucze sortowane) i zwraca ścieżkę."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def save_confusion_matrix_csv(matrix: list[list[int]], path: str | Path) -> Path:
    """Zapisuje macierz pomyłek jako CSV z etykietami w nagłówku i kolumnie."""
    import csv

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["true\\pred", *LABELS])
        for label, row in zip(LABELS, matrix):
            writer.writerow([label, *row])
    return path
