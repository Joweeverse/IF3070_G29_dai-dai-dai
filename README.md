# IF3070_G29_dai-dai-dai

# Optimasi Pemuatan Kendaraan ke Kapal

Repository ini berisi implementasi algoritma *local search* dan *evolutionary search* untuk menentukan susunan kendaraan pada geladak kapal. Tujuannya adalah memaksimalkan total biaya pengiriman kendaraan yang dimuat, dengan mempertimbangkan ukuran geladak, orientasi kendaraan, overlap, dan batas berat kapal. Proyek ini bertujuan untuk menyelesaikan Tugas Besar 1 Mata Kuliah IF3070 Dasar Inteligensi Artifisial.

Algoritma yang tersedia adalah Genetic Algorithm (GA), Hill Climbing dengan *sideways move* (HC), Simulated Annealing (SA), serta bonus varian HC: steepest ascent, stochastic hill climbing, dan random-restart hill climbing. Program dapat menampilkan ringkasan solusi dan menghasilkan grafik, gambar state, serta GIF visualisasi.

## Setup

Pastikan Python 3 telah terpasang, kemudian instal dependensi:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Menjalankan program

Jalankan dari root repository dengan format berikut:

```powershell
python src/main.py <instance.json> [algoritma]
```

Contoh menggunakan data demo:

```powershell
python src/main.py src/data/demo.json ga
python src/main.py src/data/demo.json hc
python src/main.py src/data/demo.json sa
```

Pilihan algoritma adalah `ga`/`genetic_algorithm`, `hc`/`hill_climbing`, atau `sa`/`simulated_annealing`. Pada kode ini, jika algoritma tidak diberikan, program memakai GA. Hasil visualisasi disimpan pada folder `output`.

Untuk menjalankan eksperimen perbandingan HC dan SA atau varian HC:

```powershell
python src/experiment_hc_sa.py
python src/experiment_hc_variants.py
```

Kedua skrip eksperimen memakai `src/data/demo.json` secara default dan menyimpan hasilnya ke `output/experiment/`.

## Pembagian tugas

| Anggota | Tugas |
|---|---|
| EmirMF | Menyusun fondasi proyek, implementasi dan pengembangan Genetic Algorithm, fungsi umum/visualisasi, serta eksperimen GA. |
| Johanes Sebastian S (18224062) | Implementasi Hill Climbing dengan *sideways move*, Simulated Annealing, pembangkitan tetangga, dan eksperimen HC-SA. |
| `18224010-greg` | Implementasi objective berbobot ETA dan varian Hill Climbing: steepest ascent, stochastic, serta random restart. |

Detail format state, objective, dan kontrak keluaran algoritma tersedia di [docs/kontrak.md](docs/kontrak.md).
