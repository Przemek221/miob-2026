# Laboratorium 5. Rozpoznawanie odręcznie zapisanych cyfr

## Problem

Zespół digitalizuje formularze zawierające odręcznie zapisane cyfry. Poszczególne znaki są już wycięte z formularzy i zapisane jako małe obrazy. Potrzebny jest lokalny prototyp, który na podstawie obrazu pojedynczego znaku wskaże cyfrę od `0` do `9`.

**Przygotuj z pomocą agenta działające rozwiązanie i ustal, na jakiej podstawie można przyjąć jego wynik.** Samodzielnie dobierz podejście oraz zorganizuj pracę. Nie ma narzuconego modelu, bibliotek ani sposobu podziału kodu.

## Dane

Podstawą zadania jest **1000 obrazów cyfr** wybranych ze zbioru [UCI Optical Recognition of Handwritten Digits](https://archive.ics.uci.edu/dataset/80/optical%2Brecognition%2Bof%2Bhandwritten%2Bdigits). Każdy obraz ma **8 × 8 pikseli**, jeden kanał w skali szarości i etykietę oznaczającą zapisaną cyfrę. W każdej klasie jest 100 obrazów.

ZIP z danymi zawiera pliki PNG, trzy pliki CSV oraz README z opisem formatu i pochodzenia danych. Rozpakuj go we własnym katalogu projektu.

| Plik | Liczba obrazów | Przeznaczenie |
|---|---:|---|
| `data/train.csv` | 600 | Uczenie rozwiązania. |
| `data/validation.csv` | 200 | Sprawdzanie pomysłów i wybór ustawień. |
| `data/test.csv` | 200 | Końcowa ocena wybranego rozwiązania. |

Każdy CSV zawiera `image_id` — identyfikator obrazu, `image_path` — ścieżkę do pliku względem katalogu `data/`, oraz `label` — prawidłową cyfrę. Obrazy znajdują się w `data/images/`. Podczas przewidywania odpowiedź ma wynikać z obrazu. Znana etykieta służy do uczenia i porównania z przewidywaniem.

<details class="demo">
<summary>Przykład: obrazy cyfr z danych do uczenia</summary>

![Po jednym obrazie każdej cyfry od zera do dziewięciu. Obrazy 8 × 8 pikseli powiększono bez wygładzania.](https://agents-ml-course-2026.czuba-przemyslaw.chatgpt.site/diagrams/lab-5/digits-sample.svg)

</details>

## Oczekiwany rezultat

Rozwiązanie powinno:

- Działać lokalnie i umożliwiać odtworzenie uczenia oraz oceny na dostarczonych danych.
- Zachować dopasowany model i wszystkie elementy potrzebne do jego późniejszego użycia.
- Po odczytaniu tego zapisu przyjąć ścieżkę do obrazu PNG 8 × 8 pikseli i zwrócić przewidywaną cyfrę. To użycie ma działać bez etykiety i bez ponownego uczenia.
- Zapisać przewidywania dla wszystkich 200 obrazów testowych, z identyfikatorami pozwalającymi powiązać odpowiedź z właściwym obrazem.
- Dostarczyć ocenę pokazującą liczbę poprawnych rozpoznań i pomyłek, najczęściej mylone cyfry oraz omówienie wybranych błędnie rozpoznanych obrazów, jeśli takie wystąpią.

Wystarczy uruchamianie z terminala. Prototyp dotyczy przygotowanych obrazów pojedynczych cyfr. Nie obejmuje odczytu całych formularzy ani rozpoznawania dowolnych zdjęć wykonanych telefonem.

## Warunki wykonania

Zachowaj dostarczone obrazy, etykiety i podział danych. Własne przekształcenia mogą być częścią rozwiązania, ale muszą być opisane i stosowane zgodnie z rolą poszczególnych zbiorów. Dobór modelu, ustawień i sposobu przygotowania danych zakończ przed końcową oceną na zbiorze testowym. Wyniki tej oceny nie służą do dalszego dobierania rozwiązania.

Klasyfikator ma działać lokalnie na CPU komputera osobistego, bez płatnych usług i zewnętrznych API. Te ograniczenia dotyczą klasyfikatora, a nie aplikacji agenta używanej podczas pracy. Wyniki sprawdzeń powinny dotyczyć oddawanego kodu i zapisanego modelu.

Nie ma wymaganego minimalnego wyniku klasyfikacji. **Słaby wynik trzeba rozpoznać i wyjaśnić. Wniosek o przyjęciu rozwiązania powinien wynikać z dowodów i uwzględniać jego ograniczenia.**

## Co oddać?

Pracę zapisz w folderze `lab5/` w swoim repozytorium na GitHubie. Dołącz kod, zapis modelu, przewidywania i wyniki sprawdzeń. W `README.md` opisz przygotowanie środowiska, położenie danych i polecenia potrzebne do odtworzenia działania.

W krótkim `sprawozdanie.md` przedstaw:

- Wybrane podejście, najważniejsze decyzje i ich uzasadnienie. Wskaż, co przemówiło za tym rozwiązaniem względem jednej rozważanej alternatywy.
- Organizację współpracy z agentem. Przytocz jedno zlecenie faktycznie przekazane agentowi i uzasadnij jego zakres. Pokaż jeden moment, w którym wynik sprawdzenia wpłynął na dalsze działanie agenta lub Twoją decyzję.
- Wyniki oceny i omówienie pomyłek. Powiąż wnioski z konkretnymi plikami oraz obserwacjami.
- Ocenę, czy rezultat można przyjąć jako prototyp w ustalonym zakresie. Wskaż istotne ograniczenia, niewykonane sprawdzenia i ewentualną pozostałą pracę.

Na początku sprawozdania podaj link do repozytorium, aplikację agenta, używany model językowy i poziom rozumowania, jeśli jest dostępny. W `sesje/` zachowaj pełne zapisy sesji w kolejności pracy. **Treść sesji służy diagnozie trudności i nie jest punktowana.** Podczas krótkiego omówienia bez agenta trzeba umieć wyjaśnić własne decyzje i podstawy przyjęcia wyniku.
