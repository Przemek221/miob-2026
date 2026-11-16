"""Smoke-test etapu E0: CLI odpowiada na --help, pakiety są importowalne."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_cli_help_exits_zero() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "src.cli", "--help"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "spam" in result.stdout.lower()
