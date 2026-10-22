# Hasil HC (sideways) dan SA - instance demo

Batas atas objective (knapsack berat, abaikan geometri): **189**

## Hill-Climbing with Sideways Move

| seed | objective awal | objective akhir | iterasi | sideways dipakai | max sideways | berhenti karena | durasi (s) |
|---|---|---|---|---|---|---|---|
| 1 | 95 | 184 | 111 | 106 | 100 | max_sideways | 3.666 |
| 2 | -1297 | 189 | 157 | 148 | 100 | max_sideways | 5.138 |
| 3 | -7199 | 181 | 106 | 101 | 100 | max_sideways | 3.163 |

## Simulated Annealing

| seed | objective awal | objective akhir | iterasi | T0 | alpha | T akhir | stuck | frekuensi stuck | langkah buruk diterima | durasi (s) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 95 | 187 | 20000 | 86.27 | 0.999662 | 0.1 | 13441 | 0.6721 | 577 | 2.681 |
| 2 | -1297 | 189 | 20000 | 86.27 | 0.999662 | 0.1 | 13349 | 0.6674 | 579 | 2.623 |
| 3 | -7199 | 189 | 20000 | 86.27 | 0.999662 | 0.1 | 13362 | 0.6681 | 580 | 2.308 |
