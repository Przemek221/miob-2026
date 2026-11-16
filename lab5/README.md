# Dane do Labu 5: odręcznie zapisane cyfry

Katalog `data/` zawiera 1000 obrazów PNG i odpowiadające im etykiety od `0` do `9`. Nie zawiera implementacji ani wytrenowanego modelu.

## Format

Każdy obraz ma 8 × 8 pikseli i jeden 8-bitowy kanał szarości. Ciemne tło ma wartość bliską 0, a jasny znak wartości bliższe 255. Pliki PNG zachowują układ 64 wartości źródłowego obrazu. Wartości od 0 do 16 przeliczono wzorem `round(wartość * 255 / 16)`.

Pliki `data/train.csv`, `data/validation.csv` i `data/test.csv` mają kolumny:

| Kolumna | Znaczenie |
|---|---|
| `image_id` | Stały identyfikator obrazu. |
| `image_path` | Ścieżka do PNG względem katalogu `data/`, na przykład `images/digit-….png`. |
| `label` | Prawidłowa cyfra od 0 do 9. |

Zbiór do uczenia zawiera 600 obrazów, walidacyjny 200 i testowy 200. Każda cyfra ma odpowiednio 60, 20 i 20 przykładów. W dostarczonych podziałach identyfikatory i obrazy nie powtarzają się między zbiorami.

## Pochodzenie i zakres danych

Źródło: E. Alpaydin i C. Kaynak, *Optical Recognition of Handwritten Digits* (1998), [UCI Machine Learning Repository](https://doi.org/10.24432/C50P49). Dane są udostępnione na licencji [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

To przygotowany podzbiór dydaktyczny. Obrazy do uczenia i walidacji wybrano z oryginalnego `optdigits.tra`, a do końcowej oceny z `optdigits.tes`. Oryginalny zbiór rozdziela te dwa pliki według autorów pisma. Podział na uczenie i walidację w tym zadaniu nie rozdziela dodatkowo autorów.

Dokonane zmiany: wybór 100 obrazów każdej cyfry, przygotowanie podziałów i identyfikatorów oraz zapis macierzy 8 × 8 jako PNG. Losowanie wykonano z ziarnem `20261114`. `data/manifest.json` zawiera źródło, sumy kontrolne, pozycje wybranych rekordów w plikach źródłowych i przypisanie do zbiorów.

Obrazy są już wyodrębnionymi, przygotowanymi znakami. Wynik na tych danych nie potwierdza rozpoznawania całych formularzy, zdjęć z telefonu ani skuteczności na każdym stylu pisma.
