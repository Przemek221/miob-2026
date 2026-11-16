# Kontynuuj etap E6 w WSL Ubuntu

> Tu masz plik z poprzednią sesją agenta deepseek. Przeanalizuj ją i zobacz główne polecenie. Kontynuuj etap E6. Pamiętaj żeby odpalać projekt w wslu Ubuntu.
>
> User context
>
> Attachments:
> - session-99e85c59-a7d8-4563-b49b-4cde09d991c8.md: `C:/Users/przem/AppData/Local/Temp/session-99e85c59-a7d8-4563-b49b-4cde09d991c8.md`

<details><summary>4 previous messages</summary>

> Najpierw odczytam przekazanie z poprzedniej sesji, wyłapię dokładne wymagania etapu E6 i sprawdzę bieżący stan projektu. Następnie będę uruchamiał oraz weryfikował projekt przez Ubuntu w WSL, zgodnie z Twoją wskazówką.
>
> <details><summary>Explored a file, ran a command</summary>
>
> <details><summary>Explored a file</summary>
>
> - Read `C:/Users/przem/AppData/Local/Temp/session-99e85c59-a7d8-4563-b49b-4cde09d991c8.md`
>
> </details>
>
> - Ran `wsl -d Ubuntu -- bash -lc 'cd "/mnt/d/--------------SZKOLA/magisterka-semestr3/miob/lab/miob-2026/lab3/project" && . .venv/bin/activate && pytest -q'`
>
> </details>
>
> Odtworzyłem kontekst E6: modele zostały wytrenowane, a pojedyncza końcowa ocena walidacyjna już zapisana w artefaktach. Teraz domykam bramkę jakości bez ponownego uruchamiania oceny na `validation.csv`; pierwsza próba uruchomienia WSL została zablokowana przez sandbox, więc ponawiam ją z wymaganym uprawnieniem.
>
> <details><summary>Ran 5 commands</summary>
>
> - Ran `wsl -d Ubuntu -- bash -lc 'cd "/mnt/d/--------------SZKOLA/magisterka-semestr3/miob/lab/miob-2026/lab3/project" && . .venv/bin/activate && pytest -q'`
> - Ran `Get-ChildItem -Force | Select-Object Mode,Name; git status --short; rg --files -g 'pyproject.toml' -g 'pytest.ini' -g 'setup.cfg' -g 'conftest.py' -g 'run_tests.sh' -g 'src/**' -g 'tests/**'`
> - Ran `Get-Content -Raw scripts\run_tests.sh; Get-Content -Raw src\__init__.py; Get-Content -Raw artifacts\metrics.json`
> - Ran `wsl -d Ubuntu -- bash -lc 'cd "/mnt/d/--------------SZKOLA/magisterka-semestr3/miob/lab/miob-2026/lab3/project" && . .venv/bin/activate && pwd && python -c "import os,sys; print(os.getcwd()); print(sys.path[0]); import src; print(src.__file__)" && bash scripts/run_tests.sh -q'`
> - Ran `Get-Content -Raw tests\test_evaluate.py; Get-Content -Raw src\evaluate.py; Get-ChildItem artifacts | Select-Object Name,Length`
>
> </details>
</details>

E6 jest domknięty — bez ponownego uruchamiania oceny na `validation.csv`.

- Testy w WSL Ubuntu po aktywacji `.venv`: **79 passed**
- Końcowy, z góry wybrany model: `v2`
- Wynik `v2`: F1(spam) **0,909**, precision **0,833**, recall **1,000**, accuracy **0,933**
- Macierz: TN=36, FP=4, FN=0, TP=20

Artefakty są zapisane w [artifacts](./artifacts):
[metrics.json](./artifacts/metrics.json), [macierz v2](./artifacts/confusion_matrix_v2.csv) oraz [lista 4 błędów v2](./artifacts/errors_v2.csv).

Zatrzymuję się na bramce E6 do human review, zgodnie z głównym poleceniem.

> Okej, teraz przygotuj readme projektu zgodnie z założeniami. Nie testuj czy instrukcja działa. Przekaż informacje o WSLu i błędzie z windows 11.  Dodatkowo na początku readme załącz aktualne wyniki ewaluacji modelu wraz z interpretacją który jest najlepszy.

<details><summary>2 previous messages</summary>

> Przygotuję README bez wykonywania opisanych w nim poleceń. Uwzględnię wymagane środowisko WSL Ubuntu z aktywacją `.venv`, udokumentuję zaobserwowany problem uruchamiania bezpośrednio z Windows 11 oraz rozpocznę plik od wyników E6 i uczciwej interpretacji wyboru modelu.
>
> <details><summary>Created a file, deleted a file, ran 4 commands</summary>
>
> - Ran `Get-Content -Raw README.md; Get-Content -Raw requirements.txt; Get-Content -Raw artifacts\training.json; Get-Content -Raw artifacts\cv_v2.json`
> - Ran `Get-Content -Raw src\cli.py; Get-Content -Raw src\data.py; Get-Content -Raw .gitignore`
> - Ran `rg -n -i -C 3 "windows 11|e_accessdenied|windows|wsl" 'C:\Users\przem\AppData\Local\Temp\session-99e85c59-a7d8-4563-b49b-4cde09d991c8.md'`
> - Ran `rg -a -n -i -C 3 "windows 11|e_accessdenied|windows|wsl" 'C:\Users\przem\AppData\Local\Temp\session-99e85c59-a7d8-4563-b49b-4cde09d991c8.md'`
> - Deleted `./README.md` (+0 -18)
> - Wrote `./README.md` (+136 -0)
>
> </details>
</details>

README został przygotowany: [README.md](./README.md).

Zawiera na początku aktualne wyniki E6, interpretację (`v2_svc` najlepszy na walidacji, ale `v2` pozostaje zamrożonym wyborem z CV), instrukcje dla WSL Ubuntu z aktywacją `.venv` oraz opis problemu cytowania PowerShell → WSL w Windows 11 i zalecenie użycia `--file`.

Nie uruchamiałem testów ani komend z instrukcji, zgodnie z prośbą.

> a v2_svc to jaki model?

`v2_svc` to wariant modelu `v2`, w którym klasyfikatorem jest `LinearSVC` — liniowa maszyna wektorów nośnych (SVM).

Wspólna część z `v2`:

- TF-IDF słów (1–2 gramy),
- TF-IDF znaków (3–5 gramy),
- 45 ręcznie wyliczanych cech z `text`,
- balansowanie klas (`class_weight="balanced"`).

Różnica:

- `v2` używa regresji logistycznej i zwraca prawdopodobieństwo spamu (`predict_proba`);
- `v2_svc` używa `LinearSVC`, zwraca score decyzyjny, nie skalibrowane prawdopodobieństwo.

Na końcowej walidacji `v2_svc` wypadł najlepiej: F1(spam) 0,930 i 3 błędy.

> czym jest tf-idf?

TF‑IDF to sposób zamiany tekstu na liczby dla modelu.

- **TF** (*term frequency*) — jak często słowo lub fragment występuje w jednej wiadomości.
- **IDF** (*inverse document frequency*) — obniża wagę fragmentów, które występują prawie wszędzie w zbiorze, a podnosi wagę tych rzadszych i bardziej rozróżniających.

Przykład: słowo „the” pojawia się w większości e-maili, więc ma niską wartość. Natomiast słowo „viagra” albo fragment znakowy `fr33` mogą mieć większą wartość, jeśli występują rzadko i pomagają oddzielić spam od zwykłej poczty.

W tym projekcie model używa dwóch reprezentacji TF‑IDF:

- słów i par słów, np. `limited offer`;
- fragmentów znaków o długości 3–5, co pomaga rozpoznać obfuskację typu `V1AGRA` lub `fr33`.

Każda wiadomość staje się bardzo długim wektorem liczb, a `v2` / `v2_svc` uczą się, które elementy tego wektora wskazują na spam.

> 4\. Rezultat i ograniczenia — linki do projektu, README i wyników, najważniejsze odstępstwa od planu oraz informacje o tym, czego nie ukończono lub nie sprawdzono.
>
> **\*\*W trakcie wykonywania został wyczerpany limit darmowych tokenów. Zmiana na Codex GPT5.6-Terra Lekki\*\***
>
> Rezultat:
>
> Napisz mi rezultat całego laba.

## 4. Rezultat i ograniczenia

**W trakcie wykonywania został wyczerpany limit darmowych tokenów, dlatego dalsza praca była kontynuowana przez Codex GPT‑5.6‑Terra Lekki.**

### Rezultat

Zrealizowano powtarzalny, działający klasyfikator wiadomości `spam` / `ham`, wykorzystujący wyłącznie kolumnę `text`. Projekt, instrukcja uruchomienia oraz komplet wyników znajdują się w:

- [katalogu projektu](.)
- [README.md](./README.md)
- [raporcie metryk E6](./artifacts/metrics.json)
- [macierzy pomyłek modelu v2](./artifacts/confusion_matrix_v2.csv)
- [liście błędnych predykcji modelu v2](./artifacts/errors_v2.csv)

Zaimplementowano moduły w `src/`, testy w `tests/`, interfejs CLI, zapis modeli oraz artefakty eksperymentu. Pipeline wykorzystuje reprezentację TF‑IDF słów i fragmentów znakowych, a także 45 cech wyliczanych wyłącznie z tekstu wiadomości. Nie użyto etykiet, identyfikatorów wiadomości ani metadanych pochodzenia jako cech, dzięki czemu ograniczono ryzyko przecieku danych.

Końcowa ocena została wykonana jednokrotnie na `validation.csv` (60 wiadomości: 40 ham i 20 spam). Wyniki:

| Model | F1(spam) | Precision | Recall | Accuracy | Błędy |
| --- | ---: | ---: | ---: | ---: | ---: |
| v1 — TF-IDF słów + MultinomialNB | 0,710 | 1,000 | 0,550 | 0,850 | 9 |
| v2 — TF-IDF słów i znaków + cechy + regresja logistyczna | 0,909 | 0,833 | 1,000 | 0,933 | 4 |
| v2_svc — TF-IDF słów i znaków + cechy + LinearSVC | **0,930** | **0,870** | **1,000** | **0,950** | **3** |

Najlepszy wynik na walidacji uzyskał `v2_svc`: poprawnie rozpoznał wszystkie wiadomości spam i popełnił trzy fałszywe alarmy. Jako model końcowy przed oceną wybrano jednak `v2`, zgodnie z wynikiem walidacji krzyżowej na zbiorze treningowym. Nie zmieniano tego wyboru po poznaniu wyników walidacyjnych, aby nie dostrajać modelu do zbioru końcowego.

### Odstępstwa od planu i ograniczenia

- Etap E5, czyli ograniczony dobór hiperparametrów i progu, został pominięty. Użyto parametrów wybranych na wcześniejszym etapie oraz domyślnych progów: `0,5` dla modeli probabilistycznych i `0,0` dla `LinearSVC`.
- Plan zakładał zatrzymanie po każdym etapie do review; etapy były realizowane sekwencyjnie, a E6 zakończono przed przygotowaniem dokumentacji.
- Testy projektu zostały uruchomione wcześniej w WSL Ubuntu i zakończyły się wynikiem **79 passed**. Po ostatniej edycji README nie wykonywano ponownego testu instrukcji uruchomieniowej.
- Projekt należy uruchamiać w Ubuntu w WSL z aktywnym `.venv`. W Windows 11 występuje problem cytowania tekstów przy przekazywaniu wielowyrazowego `--text` przez PowerShell do WSL; dla pełnych i wieloliniowych wiadomości zalecane jest użycie pliku przez `--file`.
- Zbiór jest mały i historyczny (wiadomości z 2003 r.), więc uzyskane wyniki nie gwarantują podobnej skuteczności dla współczesnej poczty produkcyjnej.
- Nie przeprowadzono niezależnej oceny na dodatkowym, nowszym zbiorze danych, kalibracji score’ów modelu `v2_svc` ani wdrożenia produkcyjnego.

> Skróć to znacznie. Po prostu napisz jakie modele wytrenowane, który najlepszy i jakie wyniki.

## 4. Rezultat i ograniczenia

Wytrenowano trzy modele klasyfikacji spamu, wykorzystujące wyłącznie tekst wiadomości:

- `v1`: TF-IDF słów + MultinomialNB,
- `v2`: TF-IDF słów i znaków + cechy inżynieryjne + regresja logistyczna,
- `v2_svc`: TF-IDF słów i znaków + cechy inżynieryjne + LinearSVC.

Najlepszy wynik na zbiorze walidacyjnym uzyskał model `v2_svc`: accuracy **0,950**, precision(spam) **0,870**, recall(spam) **1,000**, F1(spam) **0,930**. Popełnił 3 błędy i nie przeoczył żadnej wiadomości spam.

Wyniki pozostałych modeli:

| Model | Accuracy | F1(spam) | Błędy |
| --- | ---: | ---: | ---: |
| v1 | 0,850 | 0,710 | 9 |
| v2 | 0,933 | 0,909 | 4 |
| v2_svc | **0,950** | **0,930** | **3** |

> Wyeksportuj zapis tej sesji do folderu D:\\--------------SZKOLA\magisterka-semestr3\miob\lab\miob-2026\lab3\sesje
>
> Nie wiem jaki format obsługujesz ale może być md lub json?

<details><summary>2 previous messages</summary>

> Sprawdzę dostępne narzędzie do eksportu lub odczytu bieżącej rozmowy i zapiszę jej kopię w wskazanym folderze, preferując Markdown.
>
> <details><summary>Created a file, ran a command</summary>
>
> Tool call
>
> Tool: list_threads
> Status: completed
>
> Tool call
>
> Tool: read_thread
> Status: completed
>
> Tool call
>
> Tool: read_thread
> Status: completed
>
> - Ran `New-Item -ItemType Directory -Force 'D:\--------------SZKOLA\magisterka-semestr3\miob\lab\miob-2026\lab3\sesje' | Out-Null`
>
> - Wrote `D:/--------------SZKOLA/magisterka-semestr3/miob/lab/miob-2026/lab3/sesje/sesja_codex_2026-11-16.md` (+96 -0)
>
> </details>
</details>

Zapisałem eksport tej sesji w Markdown:

[sesja_codex_2026-11-16.md](D:/--------------SZKOLA/magisterka-semestr3/miob/lab/miob-2026/lab3/sesje/sesja_codex_2026-11-16.md)

Zawiera rozmowę użytkownika i odpowiedzi asystenta, bez wewnętrznego rozumowania oraz obszernych logów narzędzi.
