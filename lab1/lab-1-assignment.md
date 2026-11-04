# Laboratorium 1. Podstawy pracy z agentem

Przed rozpoczęciem skorzystaj ze wspólnej instrukcji [Przygotowanie do pracy](https://agents-ml-course-2026.czuba-przemyslaw.chatgpt.site/przygotowanie). Komendy dla tego projektu znajdziesz w jego README.

<span id="cel-zadania"></span>

## Cel zadania

Dołączasz do zespołu przygotowującego prototyp klasyfikacji poczty. Dostajesz od innej osoby mały projekt i wiadomości ze zbioru SpamAssassin. Zanim zaczniesz eksperymenty z modelem, potrzebujesz potwierdzić, że potrafisz uruchomić projekt i uzyskać raport dla wskazanych danych.

<div id="rezultat-zadania" data-plan-target></div>

**Ustal z agentem wynik i granice pracy, zleć uruchomienie projektu i odbierz raport dla wskazanych danych. Uruchom też gotowy test. Po zmianie jednej etykiety uzyskaj aktualny raport i wyjaśnij różnicę.**

Masz gotowy skrypt Pythona `describe_data.py`; nie musisz zmieniać kodu ani znać ML. Program czyta wiadomości i zlicza je według przypisanych etykiet: `spam` — niechciana poczta, `ham` — prawidłowa wiadomość według autorów zbioru. Nie trenuje modelu ani sam nie klasyfikuje wiadomości.

To początek wspólnego scenariusza laboratoriów 1–4: od uruchomienia projektu, przez pierwszy pomiar i poszukiwanie lepszych ustawień w ustalonych granicach, do końcowej oceny modelu. Pracujesz na prototypie edukacyjnym, bez podłączania go do rzeczywistej skrzynki pocztowej. Każde laboratorium ma osobną paczkę; nie trzeba przenosić wyników ani zmienionych danych do kolejnych zadań.

<span id="start-zadania"></span>

## Od czego zacząć

<div id="przygotowanie-zadania" data-plan-target></div>

Otwórz folder `project/` w aplikacji agenta w sposób pokazany przez prowadzącego i rozpocznij sesję. Znajdź widok wykonywanych poleceń i ich wyników oraz sposób eksportu sesji. Z agentem możesz rozmawiać po polsku; dokumentacja projektu jest po angielsku.

W [project/README.md](https://agents-ml-course-2026.czuba-przemyslaw.chatgpt.site/lab-1-project) znajdziesz instrukcję uruchomienia. Polecenia wykonuj z katalogu `project/`. Ścieżki `project/...` poniżej podano względem folderu laboratorium.

<span id="pierwsze-wykonanie"></span>

## Etap 1 — pierwsze uruchomienie i test

Poniższe punkty wskazują, co należy ustalić, wykonać i sprawdzić. **Nie są listą osobnych poleceń do agenta.** Po rozpoznaniu projektu możesz jednym zleceniem powierzyć mu sprawdzenie środowiska, uruchomienie skryptu, odczyt raportu i test. Nie jest wymagany osobny dokument z planem.

### 1. Rozpoznaj projekt i określ zlecenie

Poproś agenta, żeby na podstawie README wyjaśnił działanie `describe_data.py` i wskazał instrukcję uruchomienia. Odszukaj odczyt tego fragmentu w sesji. Obejrzyj jedną wiadomość z `project/data/exercise.csv` i ustal znaczenie pól `message_id`, `text` i `label`.

Przed wykonaniem określ w rozmowie:

- **Wynik:** raport dla `project/data/exercise.csv`, zapisany w `project/results/exercise-summary.json`.
- **Granice:** w etapie 1 bez zmian kodu, danych i testów. Etap 2 dopuszcza zmianę jednej etykiety i odświeżenie raportu.
- **Odbiór:** agent ma wskazać miejsce raportu, odczytać jego treść oraz pokazać użyte dane, wykonane polecenie i wynik procesu. Ma też podać wynik testu i zgłosić ewentualne niewykonane kroki.

Możesz korzystać z propozycji agenta. Przed zleceniem wykonania upewnij się, że rozumiesz i przyjmujesz ten zakres.

### 2. Wyjaśnij jeden fragment

Wybierz krótki fragment README lub kodu związany z tym zadaniem. Z pomocą agenta wyjaśnij jego znaczenie, a następnie opisz je własnymi słowami. Poproś o mały, zmieniony przypadek dotyczący tego samego mechanizmu; przewidź skutek przed poznaniem odpowiedzi. Sprawdź przewidywanie w dokumentacji, kodzie lub bezpiecznej próbie i wyjaśnij ewentualną różnicę. Nie zmieniaj plików projektu na potrzeby tego ćwiczenia.

Nie musisz analizować całego skryptu ani kodu testu. Fragment powinien pomagać zrozumieć wykonanie lub wynik, a nie służyć zapamiętywaniu składni.

### 3. Zleć wykonanie i odczyt raportu

Zleć agentowi sprawdzenie katalogu roboczego i wersji Pythona, wykonanie skryptu zgodnie z README oraz odczyt zapisanego raportu. Ustal, czy polecenia wykonuje Twój komputer, czy inne środowisko udostępnione przez aplikację.

Odszukaj rzeczywiste wywołanie i wynik procesu. Wyjaśnij podział ról: **model wybiera polecenie → aplikacja obsługuje narzędzie → komputer wykonuje skrypt → wynik wraca do modelu**. Sam tekst komendy lub odpowiedź „gotowe” nie potwierdza wykonania.

### 4. Odbierz wynik

Sprawdź miejsce zapisu, porównaj `input_file` z wejściem podanym w poleceniu i wyjaśnij liczebności w raporcie. Powiąż odczytany raport z zakończonym uruchomieniem; sam istniejący plik może pochodzić z wcześniejszej próby. Zachowaj jego treść w sesji do porównania z etapem 2.

Pomocniczo możesz porównać liczebności z etykietami w CSV. Ręczne liczenie wszystkich wiadomości nie jest wymagane. Jeśli wykonanie się nie udało, nie przedstawiaj starego raportu jako nowego wyniku. Ustal przyczynę z agentem; w razie blokady zgłoś prowadzącemu polecenie, komunikat i niewykonany krok.

### 5. Odczytaj wynik gotowego testu

<div id="pierwszy-test" data-plan-target></div>

Zleć uruchomienie testu poleceniem z README, jeśli nie zostało już objęte wspólnym zleceniem. Odszukaj jego wywołanie i wynik. Z pomocą agenta ustal, jakie dane test wykorzystuje i co porównuje; wyjaśnij to własnymi słowami.

Test uruchamia skrypt na osobnych wiadomościach i porównuje utworzony raport z oczekiwaniem. Nie odczytuje `exercise-summary.json`. Nie musisz analizować porównań w kodzie testu ani go modyfikować. Jeśli test się nie powiedzie, poproś o wyjaśnienie komunikatu; nie zmieniaj oczekiwań, żeby uzyskać powodzenie.

<span id="zmienione-dane"></span>

## Etap 2 — dane się zmieniły

Po przygotowaniu raportu pojawia się nowa wersja danych. Zespół potrzebuje aktualnego podsumowania; dotychczasowy raport nadal jest dostępny. W ćwiczeniu zasymulujesz taką sytuację jedną zmianą etykiety.

<div id="zmiana-etykiety" data-plan-target></div>

Po zakończeniu etapu 1 zmień z pomocą agenta etykietę **jednej** wiadomości w `project/data/exercise.csv` z `ham` na `spam`. Zapisz w sesji jej `message_id` oraz starą i nową etykietę. To celowa zmiana na potrzeby ćwiczenia, a nie ponowna ocena treści wiadomości. Nie zmieniaj pozostałych pól, kodu programu, testu ani danych testowych.

<div id="zatrzymanie-po-zmianie" data-plan-target></div>

Zleć na razie wyłącznie zmianę etykiety, bez uruchamiania programu, testu ani modyfikowania raportu. Treść raportu sprzed zmiany powinna być już zachowana w sesji z etapu 1.

Następnie ustal z agentem:

- Czy dotychczasowy raport opisuje aktualne dane?
- Jak powinny zmienić się liczebności `ham`, `spam` i łączna liczba wiadomości?
- Jakie operacje są potrzebne, żeby uzyskać i potwierdzić aktualny wynik?

<div id="uzasadnienie-dzialan" data-plan-target></div>

Przed wykonaniem zapisz przewidywaną zmianę liczebności oraz wybrane operacje i krótko uzasadnij ich cel. Następnie zleć je agentowi. Odczytaj końcowy raport, porównaj go z przewidywaniem i wskaż uruchomienie, z którego pochodzi. W tym etapie ponowienie gotowego testu nie jest wymagane. Nie poprawiaj ręcznie liczebności w raporcie. Możesz pytać agenta o wyjaśnienia i propozycje; powinieneś rozumieć, dlaczego przyjmujesz wybrany sposób działania.

<details class="demo">
<summary>Przykłady pytań pomocniczych</summary>

Pytania są opcjonalne; wybierz te, które pomogą Ci wyjaśnić trudny fragment zadania. [Cheatsheet](https://agents-ml-course-2026.czuba-przemyslaw.chatgpt.site/handout) podpowiada, jak korzystać z wyjaśnień agenta.

- „Pokaż, jakiego narzędzia użyłeś do uruchomienia programu, jakie polecenie wykonałeś i jaki wynik zwrócił komputer. Gdzie w sesji są te informacje?”
- „Na jednej wiadomości wyjaśnij pola danych i pokaż, co program z nimi robi”.
- „Wyjaśnij ten fragment na małym przykładzie. Podaj podobny przypadek i zaczekaj na przewidywanie wyniku, zanim pokażesz odpowiedź”.

</details>

<span id="oddanie"></span>

## Wymagania dotyczące oddania zadania

<div id="repozytorium" data-plan-target></div>

Pracę zapisz w folderze `lab1/` w swoim repozytorium na GitHubie, wspólnym dla całego semestru. Sprawozdanie umieść w pliku `sprawozdanie.md`, a na jego początku dodaj link do repozytorium. W podfolderze `sesje/` dołącz pełne zapisy wszystkich sesji z agentem użytych do wykonania zadania. Nazwy plików powinny wskazywać ich kolejność; zachowaj format eksportu swojej aplikacji.

Dołącz końcowy `exercise-summary.json` jako plik w repozytorium i dodaj w sprawozdaniu bezpośredni link do niego. Jeśli plik jest już zapisany w oddawanym projekcie, nie trzeba tworzyć drugiej kopii. Link ma umożliwiać odczyt wyniku bez przeszukiwania sesji.

Na początku sprawozdania podaj aplikację, nazwę używanego modelu oraz poziom rozumowania, jeśli aplikacja go udostępnia. Przepisz nazwę modelu widoczną w aplikacji. Jeśli zmieniałeś model lub poziom rozumowania, wymień użyte ustawienia. To informacja diagnostyczna dla prowadzącego — nie jest punktowana.

<details class="demo">
<summary>Przykład: zapis ustawień aplikacji</summary>

**Antigravity · Gemini 4 Argon · Low**

To przykład formatu. Wpisz nazwy i ustawienia rzeczywiście widoczne w swojej aplikacji.

</details>

<div id="sesja-diagnostyczna" data-plan-target></div>

**Oddanie pełnego zapisu sesji jest wymagane, ale jego treść nie podlega ocenie ani punktacji.** Prowadzący korzysta z niego wyłącznie do rozpoznania trudności i poprawy zajęć. Pytaj swobodnie o podstawy, proś o inne wyjaśnienia i zachowaj nieudane próby. Nie ma wymaganej liczby pytań. Prowadzący sprawdza rozumienie osobno — podczas krótkich pytań lub wejściówki.

Dołącz pełny zapis sesji do celów diagnostycznych. W krótkim sprawozdaniu odpowiedz na pięć pytań:

<div id="sprawozdanie" data-plan-target></div>

1. Jaki wynik zlecono, jakie zmiany były dozwolone i o jakie informacje do odbioru poproszono agenta?
2. Jak powstał raport? Wskaż wejście, polecenie, narzędzie, środowisko wykonania i wynik procesu. Dodaj link do końcowego raportu i wyjaśnij jego liczebności.
3. Który fragment dokumentacji lub kodu wyjaśniłeś? Podaj plik i miejsce, własne wyjaśnienie oraz mały przypadek: przewidywanie, sposób sprawdzenia i wniosek.
4. Jak uruchomiono gotowy test, jaki był wynik i czego dotyczyło sprawdzenie?
5. Jaką etykietę zmieniono w etapie 2? Jakiej zmiany liczebności oczekiwałeś, jakie operacje wybrałeś i dlaczego? Porównaj wynik przed zmianą i po nowym wykonaniu.

Treść raportu przed zmianą danych i po wykonaniu etapu 2 ma być widoczna w sesji; końcowy plik jest także dostępny przez link w sprawozdaniu. Podczas krótkiego sprawdzenia rozumienia wyjaśnisz, jak wykonałeś zadanie, w tym postępowanie po zmianie danych. Możesz też otrzymać krótki zmieniony przypadek do przewidzenia wyniku bez edycji plików oraz pytanie o różnicę między pracą na kopii ćwiczeniowej a na ważnych danych. Nie trzeba pamiętać składni poleceń.
