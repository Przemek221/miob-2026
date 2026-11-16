# Klasyfikator spamu — laboratorium 3

## Wynik końcowej oceny (E6)

Ocena została wykonana **raz** na `data/validation.csv` (60 wiadomości: 40 `ham`, 20 `spam`) po zamrożeniu modeli wytrenowanych wyłącznie na `data/train.csv`. Pełny raport: [artifacts/metrics.json](artifacts/metrics.json).

| Model | F1 (spam) | Precision (spam) | Recall (spam) | Accuracy | PR-AUC | Błędy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `v1` — TF-IDF słów + MultinomialNB | 0,710 | 1,000 | 0,550 | 0,850 | 0,998 | 9 |
| `v2` — TF-IDF słów i znaków + cechy inżynieryjne + regresja logistyczna | 0,909 | 0,833 | 1,000 | 0,933 | 0,845 | 4 |
| `v2_svc` — TF-IDF słów i znaków + cechy inżynieryjne + LinearSVC | **0,930** | **0,870** | **1,000** | **0,950** | **0,850** | **3** |

**Najlepszy wynik na walidacji uzyskał `v2_svc`**: nie przeoczył żadnego spamu i popełnił trzy fałszywe alarmy. Końcowym, uprzednio wybranym modelem pozostaje `v2`, bo został wybrany na 5-fold CV na `train` (F1(spam) = 0,951). Nie zmieniano wyboru po obejrzeniu walidacji, bo byłoby to dostrajanie do zbioru końcowej oceny. `v2` udostępnia prawdopodobieństwo `predict_proba`; `v2_svc` zwraca score z `decision_function`.

Wynik dotyczy małego, historycznego korpusu z 2003 r.; nie jest miarą gotowości filtra dla współczesnej produkcyjnej poczty.

## Cel i zasady

Projekt klasyfikuje wiadomość jako `spam` albo `ham`, używając **wyłącznie kolumny `text`**.

- `train.csv` służy do trenowania i CV, zaś `validation.csv` wyłącznie do jednorazowej oceny E6;
- pliki w `data/` są tylko do odczytu;
- model nie używa `label`, `message_id` ani metadanych pochodzenia (`source`, `member`, `split`, sum SHA) jako cech;
- pipeline działa offline: nie otwiera linków ani załączników, nie wykonuje instrukcji z treści wiadomości i nie wykonuje żądań sieciowych.

## Środowisko: WSL Ubuntu, nie natywny Windows

Projekt należy uruchamiać w **Ubuntu w WSL**. Środowisko `.venv` jest linuksowe, więc nie uruchamiaj jego interpretera bezpośrednio z PowerShella ani `cmd.exe` w Windows 11.

Katalog Windows `D:\--------------SZKOLA\magisterka-semestr3\miob\lab\miob-2026\lab3\project` w WSL ma ścieżkę:

```bash
/mnt/d/--------------SZKOLA/magisterka-semestr3/miob/lab/miob-2026/lab3/project
```

W każdej nowej sesji WSL aktywuj środowisko:

```bash
cd '/mnt/d/--------------SZKOLA/magisterka-semestr3/miob/lab/miob-2026/lab3/project'
source .venv/bin/activate
```

Użyte środowisko: Python 3.14.4, Ubuntu 26.04 w WSL; wersje bibliotek są przypięte w `requirements.txt`.

### Znany problem Windows 11 / PowerShell → WSL

Przekazanie wielowyrazowej lub wieloliniowej wiadomości przez `--text` z PowerShella do `wsl ... bash -lc ...` może błędnie obsłużyć cudzysłowy i przekazać tylko fragment tekstu, np. samo `Subject:`. To problem cytowania na granicy PowerShell–WSL, nie błąd predykcji modelu.

W Windows 11 dla rzeczywistej, szczególnie wieloliniowej wiadomości zalecany jest plik UTF-8 z opcją `--file`. W TXT wiele wiadomości rozdziel linią `---`.

## Uruchomienie od zera

Kroki wykonuj w terminalu Ubuntu WSL. Pierwsza instalacja pakietów wymaga dostępu do repozytorium pakietów; sam pipeline podczas trenowania i predykcji nie używa sieci.

```bash
cd '/mnt/d/--------------SZKOLA/magisterka-semestr3/miob/lab/miob-2026/lab3/project'
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Jeżeli `python3 -m venv` zgłosi brak modułu `venv`, doinstaluj w Ubuntu odpowiedni pakiet, np.:

```bash
sudo apt install python3.14-venv python3-pip
```

Potem ponownie utwórz i aktywuj `.venv`.

## Komendy

Po aktywowaniu `.venv` uruchamiaj komendy z katalogu głównego projektu.

```bash
# testy kontraktowe i regresyjne
bash scripts/run_tests.sh -q

# wyłącznie train.csv
python -m src.cli baseline
python -m src.cli cv --model v1
python -m src.cli cv --model v2
python -m src.cli ablate
python -m src.cli train
```

### Ważne: ocena końcowa

```bash
python -m src.cli evaluate
```

Ta komenda czyta `data/validation.csv` i zapisuje końcowe raporty. Dla rzetelności eksperymentu uruchom ją **dokładnie raz**, po zamrożeniu wyboru modelu i progu. W aktualnym repozytorium E6 już wykonano — nie uruchamiaj jej ponownie wyłącznie po to, aby odtworzyć obecne wyniki.

### Predykcja nowej wiadomości

```bash
# krótka wiadomość
python -m src.cli predict --model v2 --text 'Subject: przykładowa wiadomość'

# preferowane na Windows 11, również dla treści wieloliniowej
python -m src.cli predict --model v2 --file /sciezka/do/wiadomosc.txt
```

Do wyboru są `v1`, `v2` i `v2_svc`. Predykcja korzysta z zapisanych modeli i nie trenuje ich ponownie.

## Struktura

```text
src/
  data.py       # bezpieczne wczytywanie i kontrakt danych
  features.py   # 45 cech wyliczanych z text
  model.py      # pipeline'y, CV, zapis i odczyt modeli
  evaluate.py   # metryki i macierze pomyłek
  cli.py        # interfejs poleceń
tests/          # testy danych, cech, modeli, artefaktów i CLI
data/           # niezmieniane dane wejściowe
artifacts/      # modele oraz raporty eksperymentu
scripts/run_tests.sh
```

## Artefakty E6

- `artifacts/models/*.joblib` — trzy wytrenowane, skompresowane modele;
- `artifacts/metrics.json` — metryki i informacja o jednym przebiegu walidacji;
- `artifacts/confusion_matrix_<model>.csv` — macierze pomyłek;
- `artifacts/errors_<model>.csv` — błędne predykcje: ID, prawda, predykcja, score i temat;
- `artifacts/predictions_validation.csv` — komplet predykcji walidacyjnych;
- `artifacts/baseline.json`, `cv_v1.json`, `cv_v2.json`, `ablation.json` — wyniki z treningu/CV;
- `artifacts/training.json` — konfiguracje zapisanych modeli.

Macierze mają wiersze jako klasę prawdziwą i kolumny jako predykcję (`ham`, potem `spam`).

## Ograniczenia

Korpus jest mały i historyczny, dlatego wyniki mogą odzwierciedlać jego specyfikę. Przed praktycznym użyciem konieczna byłaby ocena na nowszych, reprezentatywnych danych oraz osobny przegląd bezpieczeństwa i prywatności.

