"""Modele: baseline (E2) oraz pipeline'y TF-IDF (E3+).

Zasada: wszystko, co wymaga dopasowania (wektoryzator, wagi, próg), jest
dopasowywane **wewnątrz** ``fit`` na danych treningowych. Ten moduł nie czyta
`validation.csv` — dostaje wyłącznie ramkę treningową.
"""

from __future__ import annotations

import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import MaxAbsScaler
from sklearn.svm import LinearSVC

from . import evaluate
from .config import N_SPLITS, SEED
from .features import FEATURE_NAMES, MessageFeatures


def build_baseline() -> DummyClassifier:
    """Model odniesienia: zawsze przewiduje klasę większościową (``ham``)."""
    return DummyClassifier(strategy="most_frequent")


class TextOnlyInput(BaseEstimator, TransformerMixin):
    """Strażnik wejścia: do modelu wolno podać tylko kolumnę ``text``.

    Bez tego strażnika ``TfidfVectorizer`` przyjąłby ramkę z kilkoma kolumnami
    i po cichu potraktował każdą kolumnę jako osobny dokument — czyli
    ``message_id``/``label`` trafiłyby do modelu bez żadnego błędu.
    """

    def _check(self, X) -> None:
        if isinstance(X, pd.DataFrame):
            if X.shape[1] != 1:
                raise ValueError(
                    "model przyjmuje wyłącznie kolumnę 'text'; "
                    f"otrzymano kolumny: {list(X.columns)}"
                )
            if list(X.columns) != ["text"]:
                raise ValueError(
                    f"dozwolona kolumna to 'text', otrzymano: {list(X.columns)}"
                )
        elif getattr(X, "ndim", 1) == 2:
            raise ValueError("model przyjmuje jednowymiarowy wektor tekstów, nie macierz 2D")

    def fit(self, X, y=None) -> "TextOnlyInput":
        self._check(X)
        return self

    def transform(self, X):
        self._check(X)
        if isinstance(X, pd.DataFrame):
            return X.iloc[:, 0]
        return X


def build_tfidf() -> TfidfVectorizer:
    """Wspólna konfiguracja TF-IDF dla tekstu (plan.md, sekcja 6.5).

    ``min_df=1`` przy 180 wiadomościach, bo rzadsze słowa bywają najmocniejszym
    sygnałem; ``sublinear_tf`` tłumi powtarzanie słów w długich mailach.
    """
    return TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
        lowercase=True,
        strip_accents="unicode",
    )


def build_pipeline_v1() -> Pipeline:
    """Model A z planu: TF-IDF (word 1–2) + MultinomialNB."""
    return Pipeline(
        [
            ("guard", TextOnlyInput()),
            ("tfidf", build_tfidf()),
            ("clf", MultinomialNB(alpha=1.0)),
        ]
    )


def build_char_tfidf() -> TfidfVectorizer:
    """TF-IDF na znakach 3–5 — odporny na obfuskację (``B!g``, ``V1AGRA``)."""
    return TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=2,
        sublinear_tf=True,
        lowercase=True,
    )


def build_text_block(use_char: bool = True) -> FeatureUnion:
    """Blok reprezentacji tekstu: word 1–2 (+ opcjonalnie char 3–5)."""
    transformers = [("word", build_tfidf())]
    if use_char:
        transformers.append(("char", build_char_tfidf()))
    return FeatureUnion(transformers)


def build_engineered_block() -> Pipeline:
    """Cechy inżynieryjne z ``features.extract`` + skalowanie (fit tylko na train)."""
    return Pipeline(
        [
            ("features", MessageFeatures()),
            ("scale", MaxAbsScaler()),
        ]
    )


def _build_logreg(use_char: bool = True, use_engineered: bool = True) -> Pipeline:
    blocks = [("text", build_text_block(use_char=use_char))]
    if use_engineered:
        blocks.append(("engineered", build_engineered_block()))
    return Pipeline(
        [
            ("guard", TextOnlyInput()),
            ("features", FeatureUnion(blocks)),
            (
                "clf",
                LogisticRegression(
                    class_weight="balanced",
                    C=1.0,
                    max_iter=2000,
                    solver="liblinear",
                    random_state=SEED,
                ),
            ),
        ]
    )


def _build_svc(use_char: bool = True, use_engineered: bool = True) -> Pipeline:
    blocks = [("text", build_text_block(use_char=use_char))]
    if use_engineered:
        blocks.append(("engineered", build_engineered_block()))
    return Pipeline(
        [
            ("guard", TextOnlyInput()),
            ("features", FeatureUnion(blocks)),
            ("clf", LinearSVC(class_weight="balanced", C=0.1, max_iter=5000, random_state=SEED)),
        ]
    )


def build_pipeline_v1_lr() -> Pipeline:
    """Ablacja: sam TF-IDF(word) + LogisticRegression."""
    return _build_logreg(use_char=False, use_engineered=False)


def build_pipeline_v2_char() -> Pipeline:
    """Ablacja: TF-IDF(word+char) + LogisticRegression, bez cech inżynieryjnych."""
    return _build_logreg(use_char=True, use_engineered=False)


def build_pipeline_v2() -> Pipeline:
    """Model B z planu: TF-IDF(word+char) + cechy inżynieryjne + LogisticRegression."""
    return _build_logreg(use_char=True, use_engineered=True)


def build_pipeline_v2_svc() -> Pipeline:
    """Model C (bez kalibracji): TF-IDF(word+char) + cechy + LinearSVC."""
    return _build_svc(use_char=True, use_engineered=True)


#: Rejestr modeli dostępnych z CLI (nazwa -> fabryka świeżego estimatora).
MODEL_FACTORIES = {
    "v1": build_pipeline_v1,
    "v1_lr": build_pipeline_v1_lr,
    "v2_char": build_pipeline_v2_char,
    "v2": build_pipeline_v2,
    "v2_svc": build_pipeline_v2_svc,
}

#: Warianty do ablacji (E4): co dodajemy i czego to dotyczy.
ABLATION_VARIANTS: tuple[str, ...] = ("v1", "v1_lr", "v2_char", "v2", "v2_svc")

#: Trzy modele zapisywane do ponownego użycia (A/B/C z planu, sekcja 7).
SAVED_MODELS: tuple[str, ...] = ("v1", "v2", "v2_svc")

#: Próg decyzyjny dla score'a z ``predict_proba`` (E5 pominięty: wartość domyślna).
#: Dla ``decision_function`` próg 0.0 odpowiada domyślnemu ``predict`` LinearSVC.
DEFAULT_THRESHOLDS: dict[str, float] = {
    "v1": 0.5,
    "v1_lr": 0.5,
    "v2_char": 0.5,
    "v2": 0.5,
    "v2_svc": 0.0,
}


def score_kind(pipeline) -> str:
    """Czy model daje prawdopodobieństwa, czy wartości decyzyjne."""
    return "predict_proba" if hasattr(pipeline, "predict_proba") else "decision_function"


def save_model(
    path: str | Path,
    model_key: str,
    pipeline,
    threshold: float,
    training_rows: int,
    config: dict | None = None,
) -> Path:
    """Zapisuje model **razem z progiem i metadanymi** do jednego pliku ``.joblib``.

    Jeden plik = brak rozjazdu między modelem a progiem przy ponownym użyciu.
    """
    bundle = {
        "bundle_format": 1,
        "model_key": model_key,
        "model_name": MODEL_DESCRIPTIONS[model_key]["name"],
        "pipeline": pipeline,
        "threshold": float(threshold),
        "score": score_kind(pipeline),
        "positive_label": "spam",
        "random_state": SEED,
        "trained_on": {"file": "train.csv", "rows": int(training_rows)},
        "config": config if config is not None else MODEL_DESCRIPTIONS[model_key],
        # Wersje potrzebne do wykrycia niezgodności przy wczytaniu starego modelu.
        "versions": {
            "python": ".".join(map(str, sys.version_info[:3])),
            "scikit_learn": sklearn.__version__,
            "joblib": joblib.__version__,
        },
    }
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, path, compress=3)
    return path


def load_model(path: str | Path) -> dict:
    """Wczytuje paczkę modelu i sprawdza jej minimalną strukturę."""
    bundle = joblib.load(Path(path))
    if not isinstance(bundle, dict):
        raise ValueError(f"Nieoczekiwany format modelu w {path}")
    missing = {"pipeline", "threshold", "model_key"} - set(bundle)
    if missing:
        raise ValueError(f"Model {path} nie ma pól: {sorted(missing)}")
    return bundle


def predict_bundle(bundle: dict, texts) -> tuple[np.ndarray, np.ndarray]:
    """Predykcja z wczytanego modelu: ``(etykiety, score klasy spam)``.

    Etykieta wynika z porównania score'a z progiem zapisanym w paczce —
    ten sam próg dla treningu, oceny i ponownego użycia.
    """
    pipeline = bundle["pipeline"]
    threshold = float(bundle["threshold"])
    if score_kind(pipeline) == "predict_proba":
        classes = list(pipeline.classes_)
        scores = np.asarray(pipeline.predict_proba(texts), dtype=float)[:, classes.index("spam")]
    else:
        scores = np.asarray(pipeline.decision_function(texts), dtype=float).ravel()
    labels = np.where(scores >= threshold, "spam", "ham")
    return labels, scores

#: Opis konfiguracji do zapisu w artefaktach (JSON-friendly, bez obiektów sklearn).
_WORD = {
    "type": "TfidfVectorizer",
    "ngram_range": [1, 2],
    "min_df": 1,
    "sublinear_tf": True,
    "lowercase": True,
    "strip_accents": "unicode",
}
_CHAR = {
    "type": "TfidfVectorizer",
    "analyzer": "char_wb",
    "ngram_range": [3, 5],
    "min_df": 2,
    "sublinear_tf": True,
    "lowercase": True,
}
_ENGINEERED = {
    "type": "MessageFeatures",
    "source": "src.features.extract",
    "n_features": len(FEATURE_NAMES),
    "scaling": "MaxAbsScaler (fit na train)",
}

MODEL_DESCRIPTIONS = {
    "v1": {
        "name": "tfidf_word_1_2__multinomial_nb",
        "vectorizer": _WORD,
        "classifier": {"type": "MultinomialNB", "alpha": 1.0},
        "input": ["text"],
    },
    "v1_lr": {
        "name": "ablation_tfidf_word__logreg",
        "vectorizer": _WORD,
        "classifier": {"type": "LogisticRegression", "C": 1.0, "class_weight": "balanced"},
        "input": ["text"],
    },
    "v2_char": {
        "name": "ablation_tfidf_word_char__logreg",
        "vectorizer": [_WORD, _CHAR],
        "classifier": {"type": "LogisticRegression", "C": 1.0, "class_weight": "balanced"},
        "input": ["text"],
    },
    "v2": {
        "name": "tfidf_word_char__engineered__logreg",
        "vectorizer": [_WORD, _CHAR],
        "engineered_features": _ENGINEERED,
        "classifier": {"type": "LogisticRegression", "C": 1.0, "class_weight": "balanced"},
        "input": ["text"],
    },
    "v2_svc": {
        "name": "tfidf_word_char__engineered__linear_svc",
        "vectorizer": [_WORD, _CHAR],
        "engineered_features": _ENGINEERED,
        "classifier": {"type": "LinearSVC", "C": 0.1, "class_weight": "balanced"},
        "input": ["text"],
    },
}


def _text_and_labels(df: pd.DataFrame) -> tuple[pd.Series, np.ndarray]:
    """Oddziela jedyne dozwolone wejście (``text``) od celu (``label``)."""
    return df["text"], df["label"].to_numpy()


def cross_validate_estimator(
    factory,
    df: pd.DataFrame,
    n_splits: int = N_SPLITS,
    seed: int = SEED,
) -> dict:
    """5-fold stratified CV na `train`; każdy fold trenuje od zera.

    Args:
        factory: funkcja zwracająca świeży estimator (pipeline) dla każdego foldu.
        df: ramka treningowa z kolumnami ``text`` i ``label``.
        n_splits: liczba foldów.
        seed: ziarno podziału (shuffle w StratifiedKFold).

    Returns:
        dict z listą raportów per fold, agregatem mean/std i informacją o podziale.
    """
    X, y = _text_and_labels(df)
    splitter = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)

    folds: list[dict] = []
    for fold_idx, (train_idx, test_idx) in enumerate(splitter.split(X, y), start=1):
        estimator = factory()
        estimator.fit(X.iloc[train_idx], y[train_idx])
        y_pred = estimator.predict(X.iloc[test_idx])
        y_proba, score_kind = _positive_class_scores(estimator, X.iloc[test_idx])
        fold_report = evaluate.report(y[test_idx], y_pred, y_proba)
        fold_report["fold"] = fold_idx
        fold_report["score"] = score_kind
        fold_report["n_train"] = int(len(train_idx))
        fold_report["n_test"] = int(len(test_idx))
        folds.append(fold_report)

    return {
        "n_splits": n_splits,
        "seed": seed,
        "folds": folds,
        "summary": evaluate.mean_and_std(folds),
    }


def _positive_class_scores(estimator, X) -> tuple[np.ndarray | None, str]:
    """Score klasy ``spam``: prawdopodobieństwo, a gdy brak — wartość decyzyjna.

    ``LinearSVC`` nie ma ``predict_proba``; ``decision_function`` daje ten sam
    porządek (a ROC-AUC/PR-AUC zależą tylko od porządku), więc jest użyty jako
    score rankingowy. Informacja o rodzaju score'a trafia do raportu.
    """
    classes = list(getattr(estimator, "classes_", []))
    if hasattr(estimator, "predict_proba"):
        proba = estimator.predict_proba(X)
        if "spam" in classes:
            return proba[:, classes.index("spam")], "predict_proba"
        return None, "none"
    if hasattr(estimator, "decision_function"):
        decision = np.asarray(estimator.decision_function(X), dtype=float).ravel()
        if classes == ["ham", "spam"] or classes == ["spam"]:
            return decision, "decision_function"
        return -decision, "decision_function(negated)"
    return None, "none"
