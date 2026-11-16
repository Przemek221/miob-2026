#!/usr/bin/env bash
# Uruchomienie z katalogu project/: bash scripts/run_tests.sh
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .venv/bin/activate ]; then
  echo "Brak .venv — patrz README (sekcja 'Uruchomienie od zera')." >&2
  exit 1
fi
# shellcheck disable=SC1091
source .venv/bin/activate
exec python -m pytest "$@"
