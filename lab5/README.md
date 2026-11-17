# Lab 5 — rozpoznawanie odręcznie zapisanych cyfr 8 × 8

Lokalny prototyp klasyfikatora pojedynczych cyfr zapisanych jako obrazy PNG 8 × 8 pikseli. Kod aplikacji znajduje się w `src/`, model w `models/`, a wyniki oceny w `artifacts/`.

## Wymagania i środowisko

- Windows z WSL (Ubuntu) albo Linux.
- Python 3.10+ (sprawdzone na Pythonie 3.14.4 w WSL).
- Zależności z `requirements.txt`: pandas, Pillow, scikit-learn, joblib, pytest.

Wszystkie polecenia wykonuj w WSL z katalogu `lab5`:

```bash
cd /mnt/<ścieżka-do-repozytorium>/lab5
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python --version
.venv/bin/python -m pip list
```

## Dane

Katalog `data/` zawiera 1000 obrazów PNG i odpowiadające im etykiety od `0` do `9`:

| Plik | Liczba obrazów | Przeznaczenie |
|---|---:|---|
| `data/train.csv` | 600 | Uczenie. |
| `data/validation.csv` | 200 | Porównanie modeli i wybór ustawień. |
| `data/test.csv` | 200 | Jednorazowa końcowa ocena. |

Każdy CSV ma kolumny `image_id`, `image_path` (ścieżka względem `data/`) i `label`. Obrazy są w `data/images/`, a metadane źródłowe w `data/manifest.json`.

### Format

Każdy obraz ma 8 × 8 pikseli i jeden 8-bitowy kanał szarości. Ciemne tło ma wartość bliską 0, a jasny znak wartości bliższe 255. Pliki PNG zachowują układ 64 wartości źródłowego obrazu. Wartości od 0 do 16 przeliczono wzorem `round(wartość * 255 / 16)`.

### Pochodzenie i zakres danych

Źródło: E. Alpaydin i C. Kaynak, *Optical Recognition of Handwritten Digits* (1998), [UCI Machine Learning Repository](https://doi.org/10.24432/C50P49). Dane są udostępnione na licencji [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

To przygotowany podzbiór dydaktyczny. Obrazy do uczenia i walidacji wybrano z oryginalnego `optdigits.tra`, a do końcowej oceny z `optdigits.tes`. Oryginalny zbiór rozdziela te dwa pliki według autorów pisma. Podział na uczenie i walidację w tym zadaniu nie rozdziela dodatkowo autorów.

Dokonane zmiany: wybór 100 obrazów każdej cyfry, przygotowanie podziałów i identyfikatorów oraz zapis macierzy 8 × 8 jako PNG. Losowanie wykonano z ziarnem `20261114`. `data/manifest.json` zawiera źródło, sumy kontrolne, pozycje wybranych rekordów w plikach źródłowych i przypisanie do zbiorów.

Obrazy są już wyodrębnionymi, przygotowanymi znakami. Wynik na tych danych nie potwierdza rozpoznawania całych formularzy, zdjęć z telefonu ani skuteczności na każdym stylu pisma.

## Struktura projektu

```text
lab5/
  data/                 # dostarczone dane, bez zmian
  src/
    data.py             # wczytanie CSV i PNG -> wektor 64 cech 0–1
    train.py            # trening KNN/SVC, wybór na walidacji, zapis modelu
    predict.py          # predykcja jednego PNG z zapisanego modelu
    evaluate.py         # jednorazowa ocena testowa, metryki i wizualizacje
  tests/test_classifier.py
  models/digit_classifier.joblib
  artifacts/            # wyniki walidacji i oceny testowej
  README.md
  sprawozdanie.md
  requirements.txt
```

## Uczenie i wybór modelu

```bash
.venv/bin/python -m src.train --model-name svc_c10.0_gammascale
```

Skrypt uczy kandydatów wyłącznie na `data/train.csv` i porównuje ich na `data/validation.csv`:

- KNN dla `n_neighbors` = 1, 3, 5, 7,
- SVC RBF dla `C` = 1, 10 i `gamma` = `scale`, 0.01.

Argument `--model-name` wskazuje jawnie model wybrany przez człowieka na podstawie tabeli walidacyjnej. Wybrany model jest zapisywany w `models/digit_classifier.joblib`, a tabela wyników w `artifacts/validation_results.csv`. Zbiór testowy nie jest używany na tym etapie.

## Predykcja pojedynczego obrazu

```bash
.venv/bin/python -m src.predict data/images/digit-17a28342e8c0.png \
  --model models/digit_classifier.joblib
```

Skrypt wczytuje PNG, normalizuje piksele do zakresu 0–1 i zwraca cyfrę wyłącznie na podstawie obrazu — bez etykiety i bez ponownego uczenia.

## Testy

```bash
.venv/bin/python -m pytest
```

Testy sprawdzają dwa przypadki: trening na małym fragmencie danych zapisuje model oraz wczytany model zwraca cyfrę 0–9 dla prawidłowego PNG.

## Końcowa ocena

Ocenę testową uruchamia się **tylko raz**, po zaakceptowaniu wybranego modelu:

```bash
.venv/bin/python -m src.evaluate
```

Wyniki:

- `artifacts/test_predictions.csv` — 200 predykcji z `image_id`, ścieżką, etykietą prawdziwą i informacją o trafieniu,
- `artifacts/test_metrics.json` — accuracy, trafienia, pomyłki, macierz pomyłek i najczęstsze pary błędów,
- `artifacts/test_metrics.md` — czytelne podsumowanie metryk,
- `artifacts/confusion_matrix.png` — macierz pomyłek,
- `artifacts/misclassified_examples.png` — przykłady błędnie rozpoznanych obrazów.

Po zobaczeniu wyniku testowego nie zmieniaj parametrów ani nie wybieraj ponownie modelu — inaczej przestaje to być uczciwa końcowa ocena.

## Wynik końcowy

Jednorazowa ocena zapisanego modelu `svc_c10.0_gammascale` na `data/test.csv` dała **198/200 trafień (accuracy 0,99)**. Pomyłki: `7 → 9` i `3 → 2`. Szczegóły, macierz pomyłek i przykłady błędów znajdują się w `artifacts/` oraz w `sprawozdanie.md`.

