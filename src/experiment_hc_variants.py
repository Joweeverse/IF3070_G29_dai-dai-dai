import json
import os
import sys

from main import load_instance
from objective import summarize
from hill_climbing_variants import (steepest_ascent, stochastic_hill_climbing,
                                    random_restart_hill_climbing)
# fungsi gambar dan teks dipakai ulang dari eksperimen HC dan SA
from experiment_hc_sa import (SEEDS, OUT, hitung_batas_atas, gambar_state,
                              gambar_objective_hc, teks_state)

# 3 varian x 3 seed = 9 run
VARIAN = [
    ("STEEPEST", steepest_ascent, {"max_iter": 1000, "k_neighbors": 200}),
    ("STOCHASTIC", stochastic_hill_climbing, {"max_iter": 1000, "k_neighbors": 200}),
    ("RANDOMRESTART", random_restart_hill_climbing,
     {"max_restart": 10, "max_iter": 1000, "k_neighbors": 200}),
]


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "demo.json")
    vehicles, ship = load_instance(path)
    nama = os.path.basename(path).replace(".json", "")
    batas_atas = hitung_batas_atas(vehicles, ship)

    baris_hasil = []
    teks_semua = []

    for kode, fungsi, params in VARIAN:
        for seed in SEEDS:
            hasil = fungsi(vehicles, ship, seed=seed, **params)
            m = hasil["metrics"]
            info = summarize(hasil["final_state"], vehicles, ship)

            tag = "%s_%s_seed%d" % (kode, nama, seed)
            judul = "%s seed %d" % (kode, seed)
            gambar_state(hasil, vehicles, ship, "states_" + tag + ".png", judul)
            gambar_objective_hc(hasil, "obj_" + tag + ".png", judul + ": objective vs iterasi")

            baris = {
                "varian": kode,
                "seed": seed,
                "initial_value": hasil["history"][0],
                "final_value": m["final_value"],
                "iterations": m["iterations"],
                "duration_s": round(hasil["duration"], 3),
                "stop_reason": m["stop_reason"],
                "feasible": info["feasible"],
                "vehicles_on_board": info["vehicles_on_board"],
                "total_weight": info["total_weight"],
            }
            if kode == "RANDOMRESTART":
                baris["restarts"] = m["restarts"]
                baris["iterations_per_restart"] = m["iterations_per_restart"]
            baris_hasil.append(baris)
            teks_semua.append(teks_state(hasil, vehicles, ship,
                                         tag + "  (objective akhir %s)" % m["final_value"]))
            print(tag, baris["initial_value"], "->", baris["final_value"],
                  baris["duration_s"], "s")

    os.makedirs(OUT, exist_ok=True)
    data = {"instance": nama, "upper_bound_knapsack": batas_atas,
            "params": {k: p for k, _, p in VARIAN}, "runs": baris_hasil}
    with open(os.path.join(OUT, "results_variants_%s.json" % nama), "w") as f:
        json.dump(data, f, indent=2)
    with open(os.path.join(OUT, "states_variants_%s.txt" % nama), "w") as f:
        f.write("\n\n".join(teks_semua))

    md = ["# Hasil varian Hill-climbing - instance %s" % nama, "",
          "Batas atas objective (knapsack berat, abaikan geometri): **%s**" % batas_atas, "",
          "| varian | seed | objective awal | objective akhir | iterasi | berhenti karena | durasi (s) | sah |",
          "|---|---|---|---|---|---|---|---|"]
    for r in baris_hasil:
        md.append("| %s | %d | %s | %s | %d | %s | %s | %s |" % (
            r["varian"], r["seed"], r["initial_value"], r["final_value"],
            r["iterations"], r["stop_reason"], r["duration_s"], r["feasible"]))
    with open(os.path.join(OUT, "results_variants_%s.md" % nama), "w") as f:
        f.write("\n".join(md) + "\n")
    print("selesai ->", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
