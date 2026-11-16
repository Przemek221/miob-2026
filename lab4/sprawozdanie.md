**codex · GPT 5.6 Terra · Lekki**

# Odbiór klasyfikatora spamu — Lab 4

Oceniany projekt: [`lab3/project`](../lab3/project/)

## 1. Cel i oceniany rezultat

Oceniono klasyfikator `spam`/`ham` działający wyłącznie na `text`: trening na `train.csv`, ocena na `validation.csv`, zapis modeli i predykcja bez ponownego treningu. Przegląd był tylko do odczytu; nie uruchamiano ponownie `evaluate`.

## 2. Ustalenia code review

### Potwierdzone błędy

1. **Nie jest wymuszona jednorazowa ocena walidacji.** [`src/cli.py:339-434`](../lab3/project/src/cli.py#L339-L434) pozwala uruchamiać `evaluate` wielokrotnie, nadpisuje wyniki i zawsze zapisuje `evaluation_runs: 1`. Nie można zatem uznać deklaracji jednego przebiegu za wiarygodny dowód.
2. **Brak powiązania wersji modelu z E6.** Modele `.joblib` mają późniejszy czas modyfikacji niż metryki i predykcje E6; kod nie zapisuje hashów ani wersji modelu ([`src/cli.py:271-289`](../lab3/project/src/cli.py#L271-L289)). Obecna paczka może więc nie być paczką ocenioną.

### Ryzyka

- `evaluate` omija `load_split()`, więc przy przyszłej zmianie danych nie sprawdzi rozłączności zbiorów.
- Planowany dobór progu/hiperparametrów E5 pominięto; jest to opisane w artefaktach, lecz nie ma potwierdzenia uzgodnienia odstępstwa.

### Potwierdzone poprawne obszary

- Pipeline dopasowuje wektoryzację i klasyfikator wewnątrz foldów treningowych ([`src/model.py:339-370`](../lab3/project/src/model.py#L339-L370)).
- Wejściem modelu jest wyłącznie `text`; pola zakazane są odrzucane ([`src/data.py:145-168`](../lab3/project/src/data.py#L145-L168)).
- Tabela predykcji ma 60 zgodnych rekordów walidacyjnych; liczby błędów są zgodne z macierzami i `metrics.json`.

## 3. Zgodność z celem i dowody

| Wymaganie | Dowód | Wniosek i ograniczenie |
|---|---|---|
| CV i wybór na danych treningowych | [`cv_v2.json`](../lab3/project/artifacts/cv_v2.json), [`ablation.json`](../lab3/project/artifacts/ablation.json) | 5 foldów na `train.csv` (180 wierszy); same JSON-y nie są niezależnym logiem wykonania. |
| Brak metadanych jako cech | [`test_data.py`](../lab3/project/tests/test_data.py), [`test_model.py`](../lab3/project/tests/test_model.py) | Testy i code review potwierdzają wejście `text`; nie wyklucza to artefaktów obecnych w treści. |
| Predykcja z zapisanego modelu | [wynik Labu 4](wyniki/model_load_isolated.txt) | Wszystkie trzy obecne `.joblib` wczytały się i przewidują bez treningu ani odczytu CSV; nie dowodzi to ich zgodności z E6. |
| Poprawne parowanie predykcji z etykietą | [`predictions_validation.csv`](../lab3/project/artifacts/predictions_validation.csv), [`metrics.json`](../lab3/project/artifacts/metrics.json) | 60 rekordów, zgodne ID i etykiety; macierze oraz listy błędów są spójne. |
| Jednorazowa walidacja po zamrożeniu modelu | [`metrics.json`](../lab3/project/artifacts/metrics.json) | **Niezaliczone:** deklaracja `evaluation_runs: 1` jest niewiarygodna, a modele nie są wersjonowane. |

### Kluczowy dowód

Dowód `Model można użyć ponownie bez trenowania` jest kluczowy, ponieważ potwierdza, że modele zostały poprawnie wytrenowane i można ich użyć do predykcji. Dowodem na to są [`tests/test_persistence.py`](../lab3/project/tests/test_persistence.py) oraz [predykcja jednego przykładowego maila w lab4](wyniki/model_load_isolated.txt).

## 4. Decyzja

**Decyzja: Należy nanieść drobne poprawki.**

Sam klasyfikator działa poprawnie — kod nie ma wycieku danych przy wektoryzacji, odrzuca metadane na wejściu, a nowe sprawdzenie ([`wyniki/model_load_isolated.txt`](wyniki/model_load_isolated.txt)) potwierdziło, że zapisane pliki `.joblib` wykonują predykcję bez ponownego trenowania i bez dostępu do plików CSV.

Do poprawy:
1. Brak kontroli jednorazowej walidacji: komenda `evaluate` pozwala bez ograniczeń nadpisywać wyniki. Z zapisanych plików nie da się udowodnić, że zbiór walidacyjny nie był używany wielokrotnie.
2. Brak powiązania aktualnych modeli z metrykami E6: pliki `.joblib` mają późniejszy czas zapisu (20:51:34–35) niż `metrics.json` i `predictions_validation.csv` (20:51:02–03), a raporty nie zapisują ich sum kontrolnych. Nie ma pewności, czy oceniane pliki nie zostały później nadpisane.