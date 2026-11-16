# Przeprowadź code review klasyfikatora…

> Przeprowadzamy odbiór projektu klasyfikatora spamu. Na tym etapie NIE modyfikuj żadnych plików z kodu projektu (z Labu 3) – pracujemy wyłącznie w trybie tylko do odczytu.\
> \
> 1\. Zapoznaj się z dokumentacją i kodem w repozytorium:\
> &#x20;  \- Planem z Labu 3 D:\\--------------SZKOLA\magisterka-semestr3\miob\lab\miob-2026\lab3\project masz plik plan.md\
> &#x20;  \- Delegacją i gotowym projektem z Labu 3 (kod, zapisany model, README, pliki z predykcjami i logami sprawdzeń w folderze lab3/).\
> \
> 2\. Przeprowadź dokładne code review pod kątem spełnienia założeń z planu. Zwróć szczególną uwagę na:\
> &#x20;  \- poprawne rozdzielenie etapu uczenia od oceny/predykcji (brak wycieku danych / data leakage przy podziale zbioru i wektoryzacji tekstu),\
> &#x20;  \- możliwość wczytania i użycia zapisanego modelu bez ponownego trenowania,\
> &#x20;  \- poprawne zestawienie predykcji z prawdziwymi etykietami tych samych wiadomości,\
> &#x20;  \- zgodność zachowania skryptów z opisem w README.\
> \
> 3\. Wypisz ustalenia, dzieląc je wyraźnie na:\
> &#x20;  \- POTWIERDZONE BŁĘDY / REGRESJE (wskaż konkretny plik, numer linii/fragment kodu jako podstawę oraz opisz techniczny skutek błędu),\
> &#x20;  \- PODEJRZENIA / RYZYKA (rzeczy niejednoznaczne lub wymagające dodatkowego sprawdzenia),\
> &#x20;  \- BRAK BŁĘDÓW (jeśli dany obszar działa w pełni poprawnie).\
> \
> 4\. Utwórz plik \`lab4/sprawozdanie.md\` i wpisz do niego wstępne wersje sekcji:\
> &#x20;  \- Metryczka (miejsce na link do repo, nazwę aplikacji agenta, model i poziom rozumowania),\
> &#x20;  \- Sekcja 1: Cel i oceniany rezultat (krótkie podsumowanie),\
> &#x20;  \- Sekcja 2: Ustalenia code review (na podstawie powyższej analizy).

<details><summary>6 previous messages</summary>

> Najpierw porównam plan, implementację, README oraz artefakty z Labu 3 w trybie tylko do odczytu. Jedynym utworzonym plikiem będzie raport `lab4/sprawozdanie.md`.
>
> <details><summary>Ran 5 commands</summary>
>
> - Ran `Get-ChildItem -Force; Get-ChildItem -Force ..; Get-ChildItem -Force ..\lab3; Get-ChildItem -Force ..\lab3\project`
> - Ran `rg --files ..\lab3\project -g '!*.pyc' -g '!*.joblib' -g '!*.pkl' -g '!*.zip' -g '!*.csv' -g '!*.json' -g '!*.log' -g '!*.venv*' ; Get-Content -Raw ..\lab3\project\plan.md; Get-Content -Raw ..\lab3\project\README.md; Get-Content -Raw ..\lab3\sprawozdanie.md; Get-Content -Raw .\lab-4-assignment.md`
> - Ran ``$files = @('..\lab3\project\src\config.py','..\lab3\project\src\data.py','..\lab3\project\src\features.py','..\lab3\project\src\model.py','..\lab3\project\src\evaluate.py','..\lab3\project\src\cli.py','..\lab3\project\tests\test_data.py','..\lab3\project\tests\test_features.py','..\lab3\project\tests\test_model.py','..\lab3\project\tests\test_persistence.py','..\lab3\project\tests\test_evaluate.py','..\lab3\project\tests\test_smoke.py','..\lab3\project\tests\test_env.py'); foreach ($f in $files) { "`n===== $f ====="; $i=0; Get-Content $f | ForEach-Object { $i++; '{0,4}: {1}' -f $i,$_ } }; "`n===== ARTIFACTS ====="; Get-ChildItem -Recurse -File ..\lab3\project\artifacts | Select-Object FullName,Length,LastWriteTime; "`n===== JSON ====="; Get-ChildItem -Recurse -File ..\lab3\project\artifacts -Filter *.json | ForEach-Object { "`n--- $($_.Name) ---"; Get-Content -Raw $_.FullName }``
> - Ran ``$files = @('..\lab3\project\src\model.py','..\lab3\project\src\evaluate.py','..\lab3\project\src\cli.py','..\lab3\project\tests\test_model.py','..\lab3\project\tests\test_persistence.py','..\lab3\project\tests\test_evaluate.py','..\lab3\project\tests\test_smoke.py','..\lab3\project\tests\test_env.py'); foreach ($f in $files) { "`n===== $f ====="; $i=0; Get-Content $f | ForEach-Object { $i++; '{0,4}: {1}' -f $i,$_ } }``
> - Ran ``$files = @('..\lab3\project\src\model.py','..\lab3\project\src\evaluate.py','..\lab3\project\src\cli.py'); foreach ($f in $files) { "`n===== $f ====="; $i=0; Get-Content $f | ForEach-Object { $i++; if (($f -like '*model.py' -and $i -ge 334) -or ($f -like '*evaluate.py') -or ($f -like '*cli.py')) { '{0,4}: {1}' -f $i,$_ } } }``
>
> </details>
>
> Znalazłem już jeden istotny problem odbiorowy: skrypt oceny deklaruje „jednorazową” walidację, ale nie ma blokady kolejnego uruchomienia i zawsze zapisuje `evaluation_runs: 1`. Sprawdzam teraz spójność zapisanych tabel predykcji z walidacją oraz faktyczne wczytanie modelu — bez ponawiania oceny.
>
> <details><summary>Ran 4 commands</summary>
>
> - Ran `$a='..\lab3\project\artifacts'; Get-ChildItem -File $a | Select-Object Name,Length,LastWriteTime; Get-ChildItem -File "$a\models" | Select-Object Name,Length,LastWriteTime; '--- predictions headers/rows ---'; Import-Csv "$a\predictions_validation.csv" | Select-Object -First 5 | Format-Table -AutoSize | Out-String; '--- errors v2 ---'; Get-Content "$a\errors_v2.csv"; '--- matrices ---'; Get-Content "$a\confusion_matrix_v2.csv"; '--- reconcile ---'; $v=Import-Csv '..\lab3\project\data\validation.csv'; $p=Import-Csv "$a\predictions_validation.csv"; "validation=$($v.Count); predictions=$($p.Count); same_ids=$(@(Compare-Object $v.message_id $p.message_id -SyncWindow 0).Count -eq 0); same_labels=$((0..($v.Count-1) | Where-Object {$v[$_].label -ne $p[$_].true_label}).Count -eq 0)"; $counts=@{}; foreach($m in 'v1','v2','v2_svc'){ $wrong=(0..($v.Count-1) | Where-Object {$p[$_]."${m}_pred" -ne $p[$_].true_label}).Count; "$m wrong=$wrong" }; '--- git status/history ---'; git -C ..\lab3\project status --short; git -C ..\lab3\project log --oneline --all -5`
> - Ran `wsl.exe bash -lc "cd '/mnt/d/--------------SZKOLA/magisterka-semestr3/miob/lab/miob-2026/lab3/project' && PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -c \"from src import model; b=model.load_model('artifacts/models/v2.joblib'); labels,scores=model.predict_bundle(b,['Subject: meeting\\n\\nAgenda for tomorrow']); print(b['model_key'], b['trained_on']['file'], len(labels), labels[0], b['threshold'])\""`
> - Ran `& wsl.exe bash -lc "cd '/mnt/d/--------------SZKOLA/magisterka-semestr3/miob/lab/miob-2026/lab3/project'; env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m src.cli predict --model v2 --text 'Subject: meeting'"`
> - Ran ``$files=@('..\lab3\project\scripts\run_tests.sh','..\lab3\project\tests\test_data.py','..\lab3\project\requirements.txt','..\lab3\project\data\README.md'); foreach($f in $files){"`n===== $f ====="; $i=0; Get-Content $f | % {$i++; '{0,4}: {1}' -f $i,$_}}; '--- source references to validation ---'; rg -n "validation|evaluation_runs|joblib.dump|load_split|predict_consistent" ..\lab3\project\src ..\lab3\project\tests``
>
> </details>
>
> Potwierdziłem też, że tabela `predictions_validation.csv` ma 60 wierszy, zachowuje kolejność i `message_id` walidacji, a `true_label` jest zgodne z `validation.csv`; liczby błędów zgadzają się z macierzami. Nie ponawiałem `evaluate`, aby nie naruszać deklaracji jednorazowej oceny. Tworzę raport z rozdzieleniem faktów od ryzyk.
>
> <details><summary>Created a file, ran a command</summary>
>
> - Wrote `./sprawozdanie.md` (+56 -0)
> - Ran `Get-Content -Raw .\sprawozdanie.md; git diff --no-index -- NUL .\sprawozdanie.md`
>
> </details>
</details>

Przegląd zakończony. Utworzyłem [sprawozdanie.md](./sprawozdanie.md).

Najważniejsze ustalenia:

- Potwierdzony błąd: `evaluate` można uruchamiać wielokrotnie, a `metrics.json` zawsze zapisuje `evaluation_runs: 1`.
- Potwierdzona niespójność dowodowa: obecne pliki modeli mają późniejszy czas modyfikacji niż metryki i predykcje E6, bez hashów lub wersjonowania wiążących je ze sobą.
- Potwierdzono poprawne użycie tylko `text`, rozdzielenie fitowania w CV, możliwość predykcji z zapisanego modelu oraz zgodność tabeli predykcji z 60 wiadomościami walidacyjnymi.

Nie zmieniłem żadnego pliku projektu z Labu 3 ani nie uruchamiałem ponownie walidacji.

> Przejdźmy do oceny dowodów z Labu 3. \
> \
> 1\. Wypisz najważniejsze wymagane zachowania systemu i powiąż je z konkretnymi plikami wyników/logami zapisanymi w Labie 3 według schematu:\
> &#x20;  [Wymagane zachowanie] -> [Konkretny plik/wynik z Labu 3] -> [Co ten wynik potwierdza] -> [Czego ten wynik NIE obejmuje / jakie ma ograniczenia].\
> \
> 2\. Wskaż, czy dla któregoś z kluczowych wymagań brakuje dowodu, wynik jest niejednoznaczny albo wykryty w poprzednim kroku błąd uniemożliwia jego zaliczenie. \
> \
> 3\. Jeśli brakuje jakiegoś istotnego dowodu (np. testu wczytania samego pliku modelu w izolacji od danych treningowych), zaproponuj i uruchom jedno konkretne sprawdzenie w terminalu, a wynik zapisz w folderze \`lab4/wyniki/\` jako nowy dowód. (Jeśli wszystko jest już udowodnione w Labie 3, nie uruchamiaj nic nowego).\
> \
> 4\. Zaktualizuj plik \`lab4/sprawozdanie.md\`, dopisując \*\*Sekcję 3: Zgodność z celem i dowody\*\* (w formie czytelnej tabeli z relatywnymi linkami do plików z dowodami oraz miejscem na mój własny komentarz do jednego kluczowego dowodu).

<details><summary>4 previous messages</summary>

> Dołączę teraz macierz dowodów. Ponieważ wcześniejszy przegląd wykazał brak rozstrzygającego dowodu dla aktualnie zapisanych modeli, wykonam jedno izolowane sprawdzenie: wczytanie każdej paczki `.joblib` i predykcję krótkiego tekstu bez odczytu `train.csv` ani `validation.csv`; wynik zapiszę wyłącznie w `lab4/wyniki/`.
>
> <details><summary>Ran 2 commands</summary>
>
> - Ran `& wsl.exe bash -lc "cd '/mnt/d/--------------SZKOLA/magisterka-semestr3/miob/lab/miob-2026/lab3/project'; env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -c \"from src import model; texts=['Subject: meeting\\n\\nAgenda for tomorrow.']; [(lambda b,k: print(k, b['trained_on']['file'], b['trained_on']['rows'], b['threshold'], model.predict_bundle(b,texts)[0][0], format(model.predict_bundle(b,texts)[1][0], '.6f')))(model.load_model('artifacts/models/'+k+'.joblib'),k) for k in ('v1','v2','v2_svc')]\""`
> - Ran `& wsl.exe bash -lc 'cd "/mnt/d/--------------SZKOLA/magisterka-semestr3/miob/lab/miob-2026/lab3/project"; env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -c "from src import model; texts=[\"Subject: meeting\\n\\nAgenda for tomorrow.\"]; [(lambda b,k: print(k, b[\"trained_on\"][\"file\"], b[\"trained_on\"][\"rows\"], b[\"threshold\"], model.predict_bundle(b,texts)[0][0], format(model.predict_bundle(b,texts)[1][0], \".6f\")))(model.load_model(\"artifacts/models/\"+k+\".joblib\"),k) for k in (\"v1\",\"v2\",\"v2_svc\")]"'`
>
> </details>
>
> Izolowane sprawdzenie zakończyło się powodzeniem: wszystkie trzy aktualne paczki modeli zostały wczytane i wykonały predykcję bez trenowania oraz bez odczytu obu CSV. Ten dowód potwierdza używalność zapisanych modeli, ale — zgodnie z wcześniejszym ustaleniem — nie potwierdza jeszcze ich tożsamości z modelami ocenionymi w E6.
>
> <details><summary>Created a file, edited a file, ran a command</summary>
>
> - Wrote `./sprawozdanie.md` (+22 -0)
> - Wrote `./wyniki/model_load_isolated.txt` (+30 -0)
> - Ran `Get-ChildItem -Recurse -File . | Select-Object FullName,Length; Get-Content -Tail 95 .\sprawozdanie.md; Get-Content -Raw .\wyniki\model_load_isolated.txt`
>
> </details>
</details>

Dodałem Sekcję 3 do [sprawozdanie.md](./sprawozdanie.md) wraz z tabelą wymaganie → dowód → zakres → ograniczenia.

Wykonałem jedno nowe, izolowane sprawdzenie aktualnych modeli. Wynik: [model_load_isolated.txt](./wyniki/model_load_isolated.txt).

Potwierdza ono, że `v1`, `v2` i `v2_svc` można wczytać z `.joblib` i użyć do predykcji bez treningu oraz bez odczytu CSV. Nadal niezaliczone pozostają:

- jednorazowość oceny walidacyjnej — kod jej nie egzekwuje;
- tożsamość aktualnych modeli z modelami ocenionymi w E6 — brakuje hashów/wersionowania, a pliki modeli są nowsze niż metryki.

> Uprość sprawozdanie.md - chcę żeby było znacznie krótsze

<details><summary>2 previous messages</summary>

> Skrócę raport do zwięzłej metryczki, najważniejszych ustaleń oraz jednej tabeli dowodów, zachowując kluczowe zastrzeżenia odbiorowe i link do nowego sprawdzenia.
>
> <details><summary>Created a file, deleted a file</summary>
>
> - Deleted `./sprawozdanie.md` (+0 -78)
> - Wrote `./sprawozdanie.md` (+50 -0)
>
> </details>
</details>

Skróciłem [sprawozdanie.md](./sprawozdanie.md) do zwięzłej wersji: metryczka, najważniejsze błędy/ryzyka, krótka tabela dowodów i decyzja odbiorowa.
