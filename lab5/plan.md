# Plan implementacji

## Cel

Przygotować lokalny, odtwarzalny klasyfikator cyfr dla obrazów PNG 8 × 8. Kod aplikacji umieścić w `src/`.

## Zasady pracy

- Wszystkie polecenia uruchamiaj w WSL, z katalogu projektu dostępnego pod ścieżką `/mnt/d/.../lab5`.
- Po każdym kroku zatrzymaj się na wskazanym **human review** i przedstaw jego wynik człowiekowi.
- Jeśli pojawi się nieoczekiwany, duży błąd (np. brak dostępu do danych, niezgodny format danych, awaria zależności lub wyraźnie nieracjonalny wynik), nie obchodź go samodzielnie. Opisz problem, zebrane dowody i zapytaj człowieka o interakcję albo dalszy plan rozwiązania.

## Kroki

1. **Przygotuj środowisko**
   - Utwórz wirtualne środowisko: `python -m venv .venv`.
   - Aktywuj je i zainstaluj zależności z `requirements.txt`.
   - Użyj przede wszystkim: `scikit-learn`, `pandas`, `Pillow`, `joblib` i `pytest`.
   - **Human review:** pokaż wersję Pythona, listę zainstalowanych zależności i potwierdź, że polecenia wykonano w WSL.

2. **Zorganizuj kod**
   - Umieść moduły w `src/`, np. `data.py`, `train.py`, `predict.py` i `evaluate.py`.
   - Wczytuj ścieżki obrazów z CSV, przekształcaj PNG do wektora 64 wartości i normalizuj piksele do zakresu 0–1.
   - Nie używaj etykiety podczas pojedynczej predykcji.
   - **Human review:** pokaż strukturę katalogów oraz wynik kontrolnego wczytania danych: liczbę rekordów w każdym CSV, rozmiar cech `(64,)` i zakres znormalizowanych pikseli.

3. **Wytrenuj i wybierz model**
   - Naucz na `data/train.csv` proste modele: KNN oraz SVC.
   - Sprawdź kilka rozsądnych parametrów wyłącznie na `data/validation.csv` (np. `n_neighbors` dla KNN oraz `C` i `gamma` dla SVC).
   - Wybierz model na podstawie wyniku walidacyjnego i prostoty rozwiązania.
   - Zapisz wybrany, dopasowany model wraz z całym przetwarzaniem do `models/` przez `joblib`.
   - **Human review:** przedstaw tabelę wyników walidacyjnych wszystkich sprawdzonych konfiguracji, uzasadnij wybór i potwierdź, że `test.csv` nie był użyty.

4. **Dodaj predykcję i ocenę końcową**
   - Skrypt predykcji ma przyjmować ścieżkę PNG oraz zapisany model, a zwracać cyfrę bez uczenia.
   - Po ostatecznym wyborze modelu uruchom jedną ocenę na `data/test.csv`.
   - Zapisz `image_id` i predykcje dla 200 obrazów do `artifacts/test_predictions.csv` oraz metryki: accuracy, liczbę trafień/pomyłek, macierz pomyłek i najczęściej mylone klasy.
   - **Human review:** pokaż przykład predykcji pojedynczego PNG po wczytaniu zapisanego modelu oraz potwierdź, że plik predykcji ma 200 unikalnych `image_id`. Przed uruchomieniem oceny testowej uzyskaj akceptację człowieka; po ocenie pokaż metryki i omów najczęstsze pomyłki.

5. **Minimalne testy jednostkowe**
   - Dodaj tylko dwa testy w `tests/`:
     1. trening na małym fragmencie danych kończy się sukcesem i zapisuje model;
     2. wczytany model zwraca cyfrę od 0 do 9 dla prawidłowego pliku PNG.
   - Uruchom je poleceniem `pytest`.
   - **Human review:** pokaż pełny wynik `pytest` i potwierdź, że wykonano dokładnie te dwa testy.

6. **Odtwarzalność i dokumentacja**
   - Opisz w `README.md` wymagania i polecenia do utworzenia środowiska, uczenia, predykcji, testów oraz oceny.
   - Wynik testowy traktuj wyłącznie jako końcową ocenę: nie dostrajaj po nim parametrów.
   - **Human review:** człowiek może odtworzyć polecenia z README w WSL i odnaleźć zapisany model, predykcje oraz metryki w opisanych lokalizacjach.
