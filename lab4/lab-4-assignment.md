# Laboratorium 4. Przegląd i odbiór rozwiązania

## Cel i punkt startowy

**Z pomocą agenta przeprowadź code review projektu z Labu 3, oceń istniejące dowody i uzasadnij decyzję o przyjęciu rozwiązania, dodatkowym sprawdzeniu albo poprawce.**

Wykorzystaj plan z Labu 2, delegację z Labu 3 oraz gotowy projekt: kod, model, README, przewidywania i wyniki sprawdzeń. Cel i wymagania wynikają z wcześniejszych ustaleń, z uwzględnieniem zmian uzgodnionych podczas implementacji. Nie trzeba ustalać ich od nowa. Teraz chodzi o ocenę, czy rezultat je spełnia i co to potwierdza.

Przegląd kodu i analizę dowodów możesz oddelegować agentowi. **Twoją pracą jest zrozumienie kluczowych ustaleń, ocena ich podstaw i podjęcie decyzji.** Nie musisz znać całej implementacji ani powtarzać całej analizy agenta.

## Co trzeba zrobić?

1. **Przekaż agentowi materiały do przeglądu.** Wskaż projekt, plan, delegację i zapisane wyniki z Labu 3. Poproś o ocenę rozwiązania względem wcześniejszych ustaleń, bez zmieniania plików.
2. **Zleć code review.** Poproś o znalezienie błędów, regresji i problemów technicznych wpływających na wymagane działanie. Przy każdym ustaleniu agent powinien wyjaśnić skutek i wskazać podstawę wniosku. Oddzielcie potwierdzone błędy od podejrzeń. Jeśli przegląd wykonano już w Labie 3, wykorzystaj jego ustalenia. Uzupełnij go o istotne części, których wcześniej nie oceniono, oraz późniejsze zmiany. Brak znalezionych błędów również jest możliwym wynikiem.
3. **Oceń dowody z Labu 3.** Powiąż najważniejsze wymagane zachowania z konkretnymi wynikami sprawdzeń. Wyjaśnij z agentem, co każdy wynik potwierdza, czego nie obejmuje i czy pozostają istotne braki. Nie powtarzaj wszystkich sprawdzeń. Dodatkowe zleć tylko wtedy, gdy brak dowodu, niejednoznaczny wynik lub późniejsza poprawka uniemożliwiają ocenę ważnego wymagania.
4. **Podejmij decyzję.** Uwzględnij dowody, ustalenia code review i znane ograniczenia. Przyjmij rozwiązanie w uzgodnionym zakresie albo wskaż konkretne sprawdzenie lub poprawkę potrzebną przed jego przyjęciem. Jeśli zlecisz poprawkę, oceń jej skutek przed zmianą decyzji.

W projekcie rozpoznawania spamu istotne są m.in. rozdzielenie uczenia i oceny, ponowne użycie zapisanego modelu bez uczenia oraz porównanie przewidywań z etykietami tych samych wiadomości. Odnieś ocenę do własnego planu i delegacji. **Nie jest wymagane osiągnięcie określonej jakości klasyfikacji.** Słaby wynik modelu nie oznacza sam w sobie błędu wykonania, a przyjęcie prototypu nie oznacza gotowości do obsługi rzeczywistej poczty.

## Co powinno zawierać sprawozdanie?

Przygotuj krótki dokument zawierający:

1. **Cel i oceniany rezultat** — krótko przypomnij, do czego miało służyć rozwiązanie i jakie najważniejsze zachowania uzgodniono. Dodaj linki do planu, delegacji i projektu, zamiast przepisywać je w całości.
2. **Ustalenia code review** — najważniejsze problemy, ich skutki i podstawy wniosków albo informację, że nie znaleziono potwierdzonych problemów. Przy istotnym ustaleniu wskaż fragment kodu lub wynik sprawdzenia, na którym opiera się wniosek. Wskaż nierozstrzygnięte podejrzenia, jeśli mogą wpłynąć na odbiór.
3. **Zgodność z celem i dowody** — pokaż powiązanie: **wymagane zachowanie → konkretny wynik sprawdzenia → co ten wynik potwierdza i czego nie obejmuje**. Możesz użyć krótkiej tabeli z linkami do wyników z Labu 3. Przy jednym kluczowym dowodzie wyjaśnij własnymi słowami, dlaczego pozwala uznać dane wymaganie za spełnione albo dlaczego jeszcze nie wystarcza.
4. **Decyzję z uzasadnieniem** — co przyjmujesz i na jakiej podstawie albo co wymaga dodatkowego sprawdzenia lub poprawy. Wskaż ograniczenia, które pozostają, oraz ewentualne nowe wyniki uzyskane podczas przeglądu.

**Sprawozdanie nie musi być długie.** Liczą się rozumienie kluczowych dowodów i uzasadnienie decyzji. Sama rekomendacja agenta nie zastępuje wyników, na których się opiera.

<div class="discussion-question">

**Kiedy zadanie jest wykonane?**

Zadanie jest wykonane, gdy przeprowadzono code review, oceniono dowody z Labu 3 i zapisano uzasadnioną decyzję. Przyjęcie wymaga potwierdzenia najważniejszych uzgodnionych zachowań i rozstrzygnięcia problemów blokujących odbiór. Jeśli dowody nie wystarczają albo potwierdzono istotny błąd, poprawnym wynikiem zadania jest wskazanie, co dokładnie wymaga sprawdzenia lub poprawy i dlaczego blokuje przyjęcie.

</div>

## Oddanie i ocena

Sprawozdanie zapisz jako `lab4/sprawozdanie.md` w swoim repozytorium na GitHubie. Na początku podaj link do repozytorium oraz nazwę aplikacji agenta, używanego modelu językowego i poziom rozumowania, jeśli jest dostępny. Do projektu i dowodów z Labu 3 odsyłaj linkami. Ewentualne nowe wyniki zachowaj w repozytorium i wskaż ich lokalizacje.

W `lab4/sesje/` dołącz pełne zapisy wykorzystanych sesji, w kolejności pracy i w formacie eksportu aplikacji. **Pełne sesje są wymagane, ale służą wyłącznie diagnozie trudności i nie są punktowane.**

Oceniane będą rozumienie ustaleń code review, powiązanie dowodów z wymaganiami, ocena ograniczeń wyników i uzasadnienie decyzji. Podczas krótkich pytań lub wejściówki bez agenta wyjaśnisz, co potwierdza wybrany dowód i dlaczego uzasadnia przyjęcie rozwiązania albo dalszą pracę. Długość raportu i liczba znalezionych błędów nie są kryteriami oceny.
