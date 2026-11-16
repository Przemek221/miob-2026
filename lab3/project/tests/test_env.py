"""Bramka E0: wymagane biblioteki muszą się importować w aktywnym venvie."""

from __future__ import annotations


def test_required_packages_import() -> None:
    import numpy  # noqa: F401
    import pandas  # noqa: F401
    import pytest  # noqa: F401
    import sklearn  # noqa: F401

    assert sklearn.__version__


def test_sklearn_pipeline_components_available() -> None:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline

    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer()),
            ("clf", MultinomialNB()),
        ]
    )
    assert [name for name, _ in pipeline.steps] == ["tfidf", "clf"]
    assert LogisticRegression() is not None
