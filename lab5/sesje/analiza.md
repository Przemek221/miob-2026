# Wyjaśnij wymagania zadania

> Przeczytaj pliki .md w tym projekcie. README.md dotyczy tylko danych, lab-5-assignment dotyczy zadania. Powiedz mi co muszę zrobić i w jaki sposób mogę to zrobić.

<details><summary>2 previous messages</summary>

> Przejrzę instrukcje projektu i streszczę zadanie wraz z praktyczną ścieżką realizacji.
>
> <details><summary>Ran 4 commands</summary>
>
> - Ran `rg --files -g "*.md"`
> - Ran `Get-ChildItem -Force | Select-Object Name,Mode,Length; Get-ChildItem -Path .. -Filter *.md -Force | Select-Object FullName,Length`
> - Ran `Get-ChildItem -Path .. -Filter *.md -Force | ForEach-Object { $_.FullName }; Get-ChildItem -Path .. -Force | Select-Object -ExpandProperty Name`
> - Ran `Get-Content -Raw -Path ..\README.md; Get-Content -Raw -Path ..\lab-5-assignment.md`
>
> </details>
</details>

Musisz zbudować lokalny prototyp rozpoznający pojedyncze cyfry z obrazów PNG 8×8, a potem rzetelnie udokumentować, czy jego wynik można uznać za wystarczający w tym zakresie.

Dane masz już w `data/`:

- `train.csv` — 600 obrazów do uczenia,
- `validation.csv` — 200 do porównania modeli i wyboru ustawień,
- `test.csv` — 200 wyłącznie do końcowej, jednorazowej oceny,
- `images/` — obrazy,
- `manifest.json` — metadane źródłowe.

Najprostsza sensowna droga:

1. Utwórz w repozytorium folder `lab5/`.
2. Napisz skrypt uczący, który:
   - czyta CSV,
   - ładuje PNG wskazane przez `image_path`,
   - zamienia każdy obraz 8×8 na wektor 64 cech,
   - uczy klasyfikator wyłącznie na `train.csv`,
   - sprawdza kandydatów na `validation.csv`.
3. Porównaj co najmniej dwa podejścia, np.:
   - `KNeighborsClassifier` jako prosty punkt odniesienia,
   - `SVC` albo `LogisticRegression` jako model docelowy.

   Dla tak małych danych i obrazów dobrym wyborem będzie zwykle SVM (`SVC`) oraz skalowanie wartości pikseli do zakresu 0–1. Ustawienia, np. `C` i `gamma`, dobierasz na walidacji — nie na teście.
4. Gdy wybierzesz model, zapisz go na dysku (np. `joblib`) razem z ewentualnym przekształceniem danych.
5. Napisz osobny skrypt predykcji, np.:
   ```powershell
   python predict.py --model models/model.joblib --image data/images/digit-....png
   ```
   Ma zwracać cyfrę bez korzystania z etykiety i bez ponownego uczenia.
6. Dopiero wtedy uruchom końcową ocenę na `test.csv`. Zapisz:
   - plik z 200 predykcjami, np. `artifacts/test_predictions.csv`, zawierający `image_id`, ścieżkę i przewidzianą cyfrę;
   - liczbę trafień i pomyłek oraz accuracy;
   - macierz pomyłek;
   - najczęściej mylone pary cyfr;
   - przykłady błędnie rozpoznanych obrazów — najlepiej tabela lub wygenerowany obraz z kilkoma przykładami.
7. Zadbaj o odtwarzalność: `requirements.txt` oraz jasne polecenia w README.

Do oddania w `lab5/` potrzebujesz co najmniej:

```text
lab5/
  README.md
  sprawozdanie.md
  requirements.txt
  train.py
  evaluate.py
  predict.py
  models/
    model.joblib
  artifacts/
    test_predictions.csv
    metrics.json lub metrics.md
    confusion_matrix.png
    misclassified_examples.png
  sesje/
    ...pełne zapisy sesji z agentem...
```

`README.md` powinno wyjaśniać instalację, gdzie znajdują się dane oraz dokładne polecenia do uczenia, predykcji i oceny.

`sprawozdanie.md` ma zawierać:

- link do repozytorium, użytego agenta, model językowy i poziom rozumowania;
- wybrane rozwiązanie i uzasadnienie względem przynajmniej jednej alternatywy;
- opis współpracy z agentem: rzeczywiste zlecenie, dlaczego miało taki zakres, oraz przykład, gdy wynik sprawdzenia zmienił dalszą decyzję;
- wyniki, błędy i odniesienia do konkretnych plików;
- końcowy werdykt: czy model można przyjąć jako prototyp do przygotowanych, wyciętych znaków 8×8 — z ograniczeniami.

Najważniejsza zasada metodologiczna: testu nie używasz do wyboru modelu. Jeśli po zobaczeniu wyniku testowego zmienisz ustawienia, przestaje on być uczciwą końcową oceną. Model ma działać tylko dla przygotowanych pojedynczych cyfr — nie jest dowodem działania na zdjęciach telefonem czy całych formularzach.

> Czy takie proste modele wystarczą do klasyfikacji?

Tak — dla tych danych proste modele są całkowicie adekwatne.

Obrazy mają tylko 8×8 pikseli, czyli 64 cechy, a zbiór uczący ma 600 przykładów. Sieć neuronowa byłaby tu raczej niepotrzebnym utrudnieniem: łatwo ją przeuczyć, wymagałaby więcej ustawień, a prawdopodobnie nie dałaby istotnej przewagi.

Dobry zestaw do porównania:

- `KNeighborsClassifier` — bardzo prosty punkt odniesienia; często działa zaskakująco dobrze dla małych obrazów cyfr.
- `SVC` z jądrem RBF — mocniejszy, ale nadal lekki model CPU; ma sens, jeśli poprawia walidację względem KNN.
- opcjonalnie `LogisticRegression` — prosty model liniowy jako dodatkowa alternatywa.

Moja praktyczna rekomendacja: porównaj KNN i SVC na `validation.csv`, wybierz lepszy wynik i uzasadnij wybór prostotą oraz wynikiem. Potem zapisz zwycięski model i wykonaj pojedynczą ocenę na `test.csv`.

W sprawozdaniu możesz napisać wprost: „Ze względu na mały, niskowymiarowy zbiór wybrano klasyczne modele uczenia maszynowego zamiast sieci neuronowej. Pozwoliło to szybko odtworzyć uczenie lokalnie na CPU i łatwo przeanalizować błędy.”

> Okej, przygotuj prosty plik plan.md w którym napiszesz plan implementacji dla innego agenta. plan ma zakładać przygotowanie venva, instalację zależności, trening modeli, dostosowanie parametrów i finalne sprawdzenie. Chce aby ten plik był zwięzły oraz chcę aby kod był w folderze src/. W kwestii testów jednostkowych to ogranicz je jedynie do minimum - zrób testy tylko dla poprawnego nauczenia modelu i poprawnej predykcji.

<details><summary>2 previous messages</summary>

> Przygotuję zwięzły plan dla kolejnego agenta w katalogu laboratorium, z kodem w `src/` i minimalnymi testami.
>
> <details><summary>Created a file, explored a file, ran a command</summary>
>
> - Ran `Get-ChildItem -Force .. | Select-Object Name,Mode; Test-Path ..\plan.md`
>
> - Wrote `D:/--------------SZKOLA/magisterka-semestr3/miob/lab/miob-2026/lab5/plan.md` (+38 -0)
>
> <details><summary>Explored a file</summary>
>
> - Read `D:/--------------SZKOLA/magisterka-semestr3/miob/lab/miob-2026/lab5/plan.md`
>
> </details>
>
> </details>
</details>

Utworzyłem zwięzły plan: [plan.md](D:/--------------SZKOLA/magisterka-semestr3/miob/lab/miob-2026/lab5/plan.md).

Uwzględnia venv, zależności, kod w `src/`, strojenie wyłącznie na walidacji, końcową ocenę testową oraz dwa minimalne testy: trening i predykcję.

> Ok, dodaj informację żeby odpalać to w WSLu. Dodatkowo dodaj kryteria walidacji dla każdego kroku, które będzie jako human review. Dopisz że w przypadku nieoczekiwanych dużych błędów należy zapytać czlowieka o interakcje/plan na rozwiazanie.

<details><summary>2 previous messages</summary>

> Uzupełnię plan o pracę w WSL, ręczne punkty akceptacji i zasadę eskalacji nietypowych błędów.
>
> <details><summary>Edited a file, explored a file</summary>
>
> - Wrote `D:/--------------SZKOLA/magisterka-semestr3/miob/lab/miob-2026/lab5/plan.md` (+12 -0)
>
> <details><summary>Explored a file</summary>
>
> - Read `D:/--------------SZKOLA/magisterka-semestr3/miob/lab/miob-2026/lab5/plan.md`
>
> </details>
>
> </details>
</details>

Zaktualizowałem [plan.md](D:/--------------SZKOLA/magisterka-semestr3/miob/lab/miob-2026/lab5/plan.md).

Plan wymaga teraz pracy w WSL, zawiera kryterium „human review” po każdym kroku oraz nakazuje zatrzymanie i konsultację z człowiekiem przy dużych, nieoczekiwanych błędach.
