"""Wspólne stałe projektu (ścieżki, ziarno, parametry CV)."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"

#: Ziarno zgodne z opisem zbioru (data/README.md) — powtarzalność podziałów i modeli.
SEED = 2026

#: Liczba foldów walidacji krzyżowej na `train` (plan.md, sekcja 7).
N_SPLITS = 5

LABELS = ("ham", "spam")
POSITIVE_LABEL = "spam"
