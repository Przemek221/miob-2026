# Metryki końcowej oceny na `data/test.csv`

- Model: `svc_c10.0_gammascale`
- Trafienia: 198
- Pomyłki: 2
- Accuracy: 0.9900
- Predykcje: `artifacts/test_predictions.csv`

## Macierz pomyłek

Wiersze: prawdziwa cyfra; kolumny: przewidziana cyfra.

| true \ pred | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 1 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3 | 0 | 0 | 1 | 19 | 0 | 0 | 0 | 0 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 0 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 | 0 | 0 |
| 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 19 | 0 | 1 |
| 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 |
| 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 |

## Najczęściej mylone pary

| prawdziwa | przewidziana | liczba |
|---:|---:|---:|
| 3 | 2 | 1 |
| 7 | 9 | 1 |

Wizualizacje: `artifacts/confusion_matrix.png` i `artifacts/misclassified_examples.png`.
