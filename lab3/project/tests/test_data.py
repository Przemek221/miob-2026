"""Testy kontraktu danych (bramka E1).

Fakty z sekcji 3 plan.md zakodowane jako testy regresyjne: jeśli dane albo loader
się zmienią, testy mają to złapać, zamiast po cichu psuć kolejne etapy.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src import data


@pytest.fixture(scope="module")
def split() -> tuple[pd.DataFrame, pd.DataFrame]:
    return data.load_split()


def test_shape_and_columns(split: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    train, validation = split
    assert train.shape == (180, 3)
    assert validation.shape == (60, 3)
    assert list(train.columns) == list(data.REQUIRED_COLUMNS)
    assert list(validation.columns) == list(data.REQUIRED_COLUMNS)


def test_label_distribution(split: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    train, validation = split
    assert data.label_counts(train) == {"ham": 120, "spam": 60}
    assert data.label_counts(validation) == {"ham": 40, "spam": 20}


def test_labels_are_known(split: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    train, validation = split
    assert set(train["label"]) == set(data.LABELS)
    assert set(validation["label"]) == set(data.LABELS)


def test_no_missing_values(split: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    for df in split:
        for col in data.REQUIRED_COLUMNS:
            assert (df[col].astype(str).str.strip() != "").all()
            assert df[col].notna().all()


def test_no_duplicates(split: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    train, validation = split
    assert not train["message_id"].duplicated().any()
    assert not validation["message_id"].duplicated().any()
    assert not train["text"].duplicated().any()
    assert not validation["text"].duplicated().any()


def test_no_leak_between_splits(split: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    train, validation = split
    assert set(train["message_id"]).isdisjoint(validation["message_id"])
    assert set(train["text"]).isdisjoint(validation["text"])


def test_every_message_has_subject(split: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    for df in split:
        assert df["text"].str.startswith("Subject:").all()


def test_validation_is_never_loaded_as_training_data() -> None:
    """``load_split`` zwraca dwie różne ramki; walidacja nie jest doklejana do treningu."""
    train, validation = data.load_split()
    assert len(train) + len(validation) == 240
    assert set(train["message_id"]).isdisjoint(validation["message_id"])


def test_feature_frame_keeps_only_text(split: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    train, _ = split
    features = data.feature_frame(train.drop(columns=["label", "message_id"]))
    assert list(features.columns) == ["text"]


@pytest.mark.parametrize("column", sorted(data.FORBIDDEN_FEATURE_COLUMNS))
def test_forbidden_columns_are_rejected(column: str) -> None:
    with pytest.raises(data.DataValidationError):
        data.select_feature_columns(["text", column])


def test_unknown_columns_are_rejected() -> None:
    with pytest.raises(data.DataValidationError):
        data.select_feature_columns(["text", "subject"])


def test_validation_rejects_wrong_columns() -> None:
    df = pd.DataFrame({"message_id": ["a"], "text": ["Subject: x"], "source": ["spam"]})
    with pytest.raises(data.DataValidationError, match="brak wymaganych kolumn"):
        data.validate_frame(df, "synthetic.csv")


def test_validation_rejects_unknown_label() -> None:
    df = pd.DataFrame({"message_id": ["a"], "text": ["Subject: x"], "label": ["maybe"]})
    with pytest.raises(data.DataValidationError, match="etykiety"):
        data.validate_frame(df, "synthetic.csv")


def test_validation_rejects_duplicates_and_blanks() -> None:
    df = pd.DataFrame(
        {
            "message_id": ["a", "a"],
            "text": ["Subject: x", "   "],
            "label": ["ham", "spam"],
        }
    )
    with pytest.raises(data.DataValidationError) as excinfo:
        data.validate_frame(df, "synthetic.csv")
    message = str(excinfo.value)
    assert "duplikaty message_id" in message
    assert "puste wartości" in message


def test_load_split_rejects_overlapping_ids(tmp_path) -> None:
    header = "message_id,text,label\n"
    (tmp_path / "train.csv").write_text(
        header + 'a,"Subject: one",ham\n', encoding="utf-8"
    )
    (tmp_path / "validation.csv").write_text(
        header + 'a,"Subject: two",spam\n', encoding="utf-8"
    )
    with pytest.raises(data.DataValidationError, match="wspólne message_id"):
        data.load_split(tmp_path)


def test_load_split_rejects_missing_file(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        data.load_split(tmp_path)
