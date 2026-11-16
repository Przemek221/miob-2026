"""Wczytywanie i walidacja danych wejściowych.

Kontrakt (plan.md, sekcja 4):

    data.load_split() -> (train_df, val_df)

Zwracane ramki mają kolumny ``message_id``, ``text``, ``label`` — i tylko je.
Funkcje cech dostają **wyłącznie** ``text``; kolumny zakazane (etykieta,
identyfikatory, metadane pochodzenia) są twardo odrzucane.

Pliki w ``data/`` są tylko do odczytu — ten moduł nigdy nic tam nie zapisuje.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"

#: Kolumny wymagane w plikach CSV (kolejność nie ma znaczenia).
REQUIRED_COLUMNS: tuple[str, ...] = ("message_id", "text", "label")

#: Jedyne kolumny dopuszczone jako wejście modelu.
FEATURE_COLUMNS: tuple[str, ...] = ("text",)

#: Kolumny, których nie wolno użyć jako cech (przeciek etykiety / zapamiętywanie).
FORBIDDEN_FEATURE_COLUMNS: frozenset[str] = frozenset(
    {
        "label",
        "message_id",
        "source",
        "member",
        "path",
        "split",
        "raw_sha256",
        "body_sha256",
        "sha256",
        "source_csv_sha256",
        "file_sha256",
    }
)

#: Dopuszczone etykiety.
LABELS: tuple[str, ...] = ("ham", "spam")


class DataValidationError(ValueError):
    """Dane wejściowe nie spełniają kontraktu; komunikat zawiera listę problemów."""


def _read_csv(path: Path) -> pd.DataFrame:
    """Czyta CSV jako tekst (bez interpretacji ``NA``) — treść maili zostaje nietknięta."""
    if not path.is_file():
        raise FileNotFoundError(f"Brak pliku z danymi: {path}")
    return pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8",
        engine="python",
    )


def validate_frame(df: pd.DataFrame, name: str) -> None:
    """Sprawdza schemat i spójność pojedynczego zbioru.

    Zbiera wszystkie problemy i zgłasza je jednym wyjątkiem, żeby naprawiać
    dane hurtowo, a nie po jednym błędzie na raz.
    """
    problems: list[str] = []

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        problems.append(f"brak wymaganych kolumn: {missing}")
    unexpected = [col for col in df.columns if col not in REQUIRED_COLUMNS]
    if unexpected:
        problems.append(f"nieoczekiwane kolumny: {unexpected}")

    if problems:
        raise DataValidationError(f"{name}: " + "; ".join(problems))

    if len(df) == 0:
        problems.append("zbiór jest pusty")

    for col in REQUIRED_COLUMNS:
        blank = df[col].astype(str).str.strip() == ""
        if blank.any():
            problems.append(f"puste wartości w kolumnie {col!r}: {int(blank.sum())}")

    bad_labels = sorted(set(df["label"]) - set(LABELS))
    if bad_labels:
        problems.append(f"etykiety spoza {LABELS}: {bad_labels}")

    duplicate_ids = int(df["message_id"].duplicated().sum())
    if duplicate_ids:
        problems.append(f"duplikaty message_id: {duplicate_ids}")

    duplicate_texts = int(df["text"].duplicated().sum())
    if duplicate_texts:
        problems.append(f"duplikaty text: {duplicate_texts}")

    if problems:
        raise DataValidationError(f"{name}: " + "; ".join(problems))


def load_csv(path: str | Path, name: str | None = None) -> pd.DataFrame:
    """Wczytuje i waliduje jeden plik CSV (kolejność kolumn jak w wymaganiach)."""
    path = Path(path)
    df = _read_csv(path)
    validate_frame(df, name or path.name)
    return df.loc[:, list(REQUIRED_COLUMNS)].reset_index(drop=True)


def load_split(data_dir: str | Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Zwraca ``(train_df, val_df)`` po pełnej walidacji obu zbiorów i ich rozłączności.

    Sprawdzane jest też, że zbiory nie dzielą ``message_id`` ani identycznej treści —
    inaczej ocena na walidacji mierzyłaby zapamiętywanie, nie generalizację.
    """
    data_dir = Path(data_dir) if data_dir is not None else DEFAULT_DATA_DIR
    train = load_csv(data_dir / "train.csv", "train.csv")
    validation = load_csv(data_dir / "validation.csv", "validation.csv")

    problems: list[str] = []
    shared_ids = set(train["message_id"]) & set(validation["message_id"])
    if shared_ids:
        problems.append(
            f"wspólne message_id między train i validation: {len(shared_ids)} "
            f"(np. {sorted(shared_ids)[:3]})"
        )
    shared_texts = set(train["text"]) & set(validation["text"])
    if shared_texts:
        problems.append(
            f"identyczne wiadomości w train i validation: {len(shared_texts)}"
        )
    if problems:
        raise DataValidationError("train.csv/validation.csv: " + "; ".join(problems))

    return train, validation


def select_feature_columns(columns: list[str] | tuple[str, ...] | pd.Index) -> list[str]:
    """Przepuszcza wyłącznie dozwolone kolumny cech.

    Używane przez pipeline'ę i testy: próba podania ``label``, ``message_id``
    albo metadanych pochodzenia kończy się błędem, a nie cichym przeciekiem.
    """
    columns = list(columns)
    forbidden = [col for col in columns if str(col).lower() in FORBIDDEN_FEATURE_COLUMNS]
    if forbidden:
        raise DataValidationError(
            f"kolumny zakazane jako cechy: {forbidden}; dozwolone: {list(FEATURE_COLUMNS)}"
        )
    unexpected = [col for col in columns if col not in FEATURE_COLUMNS]
    if unexpected:
        raise DataValidationError(
            f"nieobsługiwane kolumny cech: {unexpected}; dozwolone: {list(FEATURE_COLUMNS)}"
        )
    return columns


def feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Zwraca ramkę z samą kolumną ``text`` — wejście dla ekstrakcji cech."""
    columns = select_feature_columns(list(df.columns))
    return df.loc[:, columns].reset_index(drop=True)


def label_counts(df: pd.DataFrame) -> dict[str, int]:
    """Liczebności klas w ustalonej kolejności (do raportów i testów)."""
    counts = df["label"].value_counts()
    return {label: int(counts.get(label, 0)) for label in LABELS}
