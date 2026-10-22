import json
import os
import sys

import matplotlib
matplotlib.use("Agg")   # supaya bisa menyimpan gambar tanpa membuka jendela
import matplotlib.pyplot as plt

from main import load_instance
from objective import summarize
from visualize import render_deck
from plot import draw_panel
from hill_climbing import hill_climbing
from simulated_annealing import simulated_annealing

#3 run per algoritma
SEEDS = [1, 2, 3]

#parameter eksperimen. T0 dan alpha dihitung automatically
HC_PARAMS = {"max_sideway": 100, "max_loop": 1000, "k_neighbors": 200}
SA_PARAMS = {"T0": None, "alpha": None, "T_min": 0.1, "max_iter": 20000}

# warna grafik
BIRU = "#2563eb"
ABU = "#9ca3af"
ORANYE = "#d97706"
HITAM = "#111827"

# folder output
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")


def gaya_sumbu(ax, xlabel, ylabel, judul):
    #tampilan sederhana grafik
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(judul, fontsize=11, loc="left", color=HITAM)
    ax.grid(True, alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def simpan_gambar(fig, nama_file):
    #simpan gambar di folder output
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, nama_file)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def hitung_batas_atas(vehicles, ship):
    kapasitas = ship["max_weight"]
    terbaik = [0] * (kapasitas + 1)
    for v in vehicles.values():
        for w in range(kapasitas, v["weight"] - 1, -1):
            kandidat = terbaik[w - v["weight"]] + v["shipping_fee"]
            if kandidat > terbaik[w]:
                terbaik[w] = kandidat
    return terbaik[kapasitas]


def gambar_state(hasil, vehicles, ship, nama_file, judul):
    #menunjukkan state awal dan akhir
    fig, axes = plt.subplots(1, 4, figsize=(13, 5), width_ratios=[ship["width"], 4, ship["width"], 4])
    draw_panel(axes[0], hasil["initial_state"], vehicles, ship, "geladak (awal)", True)
    draw_panel(axes[1], hasil["initial_state"], vehicles, ship, "luar kapal (awal)", False)
    draw_panel(axes[2], hasil["final_state"], vehicles, ship, "geladak (akhir)", True)
    draw_panel(axes[3], hasil["final_state"], vehicles, ship, "luar kapal (akhir)", False)
    fig.suptitle(judul, fontsize=12)
    return simpan_gambar(fig, nama_file)


def gambar_objective_hc(hasil, nama_file, judul):
   #grafik untuk algoritma hc
    history = hasil["history"]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(range(len(history)), history, color=BIRU, lw=2)
    gaya_sumbu(ax, "iterasi", "objective", judul)
    ax.annotate(str(history[-1]), (len(history) - 1, history[-1]),
                textcoords="offset points", xytext=(-4, 6), ha="right",
                color=HITAM, fontsize=9)
    return simpan_gambar(fig, nama_file)


def gambar_objective_sa(hasil, nama_file, judul):
    #grafik untuk algoritma sa
    sekarang = hasil["history_current"]
    terbaik = hasil["history"]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(range(len(sekarang)), sekarang, color=ABU, lw=1, label="objective state saat ini")
    ax.plot(range(len(terbaik)), terbaik, color=BIRU, lw=2, label="terbaik sejauh ini")

    #batas bawah sumbu y
    bawah = min(terbaik[0], terbaik[-1]) - 20
    nilai_awal_dibuang = min(sekarang[len(sekarang) // 20:]) - 20
    ax.set_ylim(max(bawah, nilai_awal_dibuang), max(terbaik) + 15)
    gaya_sumbu(ax, "iterasi", "objective", judul)
    ax.legend(frameon=False, loc="lower right")
    return simpan_gambar(fig, nama_file)


def gambar_peluang_sa(hasil, nama_file, judul):
    # Grafik min(1, e^(dE/T)) terhadap iterasi.
    # Atas: nilai tiap iterasi. Bawah: rata-rata per jendela supaya trennya terlihat.
    p = hasil["accept_prob_history"]
    fig, axes = plt.subplots(2, 1, figsize=(8, 5.5), sharex=True)

    axes[0].scatter(range(1, len(p) + 1), p, s=2, color=ORANYE, alpha=0.4, rasterized=True)
    gaya_sumbu(axes[0], "", "min(1, e^(ΔE/T))", judul)
    axes[0].set_ylim(-0.03, 1.03)

    jendela = max(1, len(p) // 100)
    x_rata = []
    y_rata = []
    for awal in range(0, len(p), jendela):
        potongan = p[awal:awal + jendela]
        x_rata.append(awal + jendela / 2)
        y_rata.append(sum(potongan) / len(potongan))
    axes[1].plot(x_rata, y_rata, color=BIRU, lw=2)
    gaya_sumbu(axes[1], "iterasi", "rata-rata (jendela %d)" % jendela, "")
    axes[1].set_ylim(0, 1.03)
    return simpan_gambar(fig, nama_file)


def teks_state(hasil, vehicles, ship, label):
    # State awal dan akhir dalam bentuk teks, untuk dilampirkan di laporan
    baris = ["=" * 60, label, "=" * 60]
    for kunci, nama in [("initial_state", "state awal"), ("final_state", "state akhir")]:
        state = hasil[kunci]
        baris.append("-- " + nama + " --")
        baris.append(render_deck(state, vehicles, ship))
        baris.append("  " + str(summarize(state, vehicles, ship)))
        di_luar = []
        for k in state:
            if not k["on_board"]:
                di_luar.append(k["vehicle_id"])
        baris.append("  luar kapal: " + ", ".join(di_luar))
    return "\n".join(baris)


def main():
    # Instance: dari argumen, kalau tidak ada pakai src/data/demo.json
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "demo.json")
    vehicles, ship = load_instance(path)
    nama = os.path.basename(path).replace(".json", "")
    batas_atas = hitung_batas_atas(vehicles, ship)

    baris_hasil = []   # satu dict per run, untuk tabel
    teks_semua = []    # teks state tiap run

    for algo in ["HC", "SA"]:
        for seed in SEEDS:
            #jalankan algoritma
            if algo == "HC":
                hasil = hill_climbing(vehicles, ship, seed=seed, **HC_PARAMS)
            else:
                hasil = simulated_annealing(vehicles, ship, seed=seed, **SA_PARAMS)
            m = hasil["metrics"]
            info = summarize(hasil["final_state"], vehicles, ship)

            #simpan gambar
            tag = "%s_%s_seed%d" % (algo, nama, seed)
            judul = "%s seed %d" % (algo, seed)
            gambar_state(hasil, vehicles, ship, "states_" + tag + ".png", judul)
            if algo == "HC":
                gambar_objective_hc(hasil, "obj_" + tag + ".png", judul + ": objective vs iterasi")
            else:
                gambar_objective_sa(hasil, "obj_" + tag + ".png", judul + ": objective vs iterasi")
                gambar_peluang_sa(hasil, "prob_" + tag + ".png", judul + ": e^(ΔE/T) vs iterasi")

            # --- catat hasilnya ---
            baris = {
                "algo": algo,
                "seed": seed,
                "initial_value": hasil["history"][0],
                "final_value": m["final_value"],
                "iterations": m["iterations"],
                "duration_s": round(hasil["duration"], 3),
                "feasible": info["feasible"],
                "vehicles_on_board": info["vehicles_on_board"],
                "total_weight": info["total_weight"],
            }
            if algo == "HC":
                baris["sideway_used"] = m["sideway_used"]
                baris["max_sideway"] = m["max_sideways"]
                baris["stop_reason"] = m["stop_reason"]
                baris["k_neighbors"] = m["k_neighbors"]
            else:
                baris["T0"] = round(m["T0"], 2)
                baris["alpha"] = round(m["alpha"], 6)
                baris["T_final"] = round(m["T_final"], 4)
                baris["stuck_count"] = m["stuck_count"]
                baris["stuck_frequency"] = round(m["stuck_frequency"], 4)
                baris["accepted_worse"] = m["accepted_worse"]
            baris_hasil.append(baris)
            teks_semua.append(teks_state(hasil, vehicles, ship, tag + "  (objective akhir %s)" % m["final_value"]))
            print(tag, baris["initial_value"], "->", baris["final_value"], baris["duration_s"], "s")

    #simpan file hasil
    os.makedirs(OUT, exist_ok=True)
    data = {"instance": nama, "upper_bound_knapsack": batas_atas, "hc_params": HC_PARAMS, "sa_params": SA_PARAMS, "runs": baris_hasil}
    with open(os.path.join(OUT, "results_%s.json" % nama), "w") as f:
        json.dump(data, f, indent=2)
    with open(os.path.join(OUT, "states_%s.txt" % nama), "w") as f:
        f.write("\n\n".join(teks_semua))

    #tabel untuk hasil
    md = ["# Hasil HC (sideways) dan SA - instance %s" % nama, "", "Batas atas objective (knapsack berat, abaikan geometri): **%s**" % batas_atas, "", "## Hill-Climbing with Sideways Move", "", "| seed | objective awal | objective akhir | iterasi | sideways dipakai | max sideways | berhenti karena | durasi (s) |", "|---|---|---|---|---|---|---|---|"]
    for r in baris_hasil:
        if r["algo"] == "HC":
            md.append("| %d | %s | %s | %d | %d | %d | %s | %s |" % (r["seed"], r["initial_value"], r["final_value"], r["iterations"], r["sideway_used"], r["max_sideway"], r["stop_reason"], r["duration_s"]))
    md += ["", "## Simulated Annealing", "", "| seed | objective awal | objective akhir | iterasi | T0 | alpha | T akhir | stuck | frekuensi stuck | langkah buruk diterima | durasi (s) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in baris_hasil:
        if r["algo"] == "SA":
            md.append("| %d | %s | %s | %d | %s | %s | %s | %d | %s | %d | %s |" % (r["seed"], r["initial_value"], r["final_value"], r["iterations"], r["T0"], r["alpha"], r["T_final"], r["stuck_count"], r["stuck_frequency"], r["accepted_worse"], r["duration_s"]))
    with open(os.path.join(OUT, "results_%s.md" % nama), "w") as f:
        f.write("\n".join(md) + "\n")
    print("selesai ->", os.path.abspath(OUT))


if __name__ == "__main__":
    main()