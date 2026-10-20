import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from main import load_instance
from objective import summarize
from visualize import render_deck
from plot import draw_panel
from hill_climbing import hill_climbing
from simulated_annealing import simulated_annealing

SEEDS = [1, 2, 3]
HC_PARAMS = {"max_sideways": 100, "max_iter": 1000, "k_neighbors": 200}
SA_PARAMS = {"T0": None, "alpha": None, "T_min": 0.1, "max_iter": 20000}

BLUE = "#2563eb"
GRAY = "#9ca3af"
ORANGE = "#d97706"
INK = "#111827"

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")


def style(ax, xlabel, ylabel, title):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=11, loc="left", color=INK)
    ax.grid(True, alpha=0.25)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_states(result, vehicles, ship, name, title):
    fig, axes = plt.subplots(1, 4, figsize=(13, 5),
                             width_ratios=[ship["width"], 4, ship["width"], 4])
    for ax_k, ax_d, key, label in ((axes[0], axes[1], "initial_state", "awal"),
                                   (axes[2], axes[3], "final_state", "akhir")):
        st = result[key]
        draw_panel(ax_k, st, vehicles, ship, "geladak (" + label + ")", True)
        draw_panel(ax_d, st, vehicles, ship, "luar kapal (" + label + ")", False)
    fig.suptitle(title, fontsize=12)
    return save(fig, name)


def plot_hc(result, name, title):
    h = result["history"]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(range(len(h)), h, color=BLUE, lw=2)
    style(ax, "iterasi", "objective", title)
    ax.annotate(str(h[-1]), (len(h) - 1, h[-1]), textcoords="offset points",
                xytext=(-4, 6), ha="right", color=INK, fontsize=9)
    return save(fig, name)


def plot_sa(result, name, title):
    cur, best = result["history_current"], result["history"]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(range(len(cur)), cur, color=GRAY, lw=1, label="objective state saat ini")
    ax.plot(range(len(best)), best, color=BLUE, lw=2, label="terbaik sejauh ini")
    lo = min(best[0], best[-1]) - 20
    ax.set_ylim(max(lo, min(cur[len(cur) // 20:]) - 20), max(best) + 15)
    style(ax, "iterasi", "objective", title)
    ax.legend(frameon=False, loc="lower right")
    return save(fig, name)


def plot_sa_prob(result, name, title):
    p = result["accept_prob_history"]
    fig, axes = plt.subplots(2, 1, figsize=(8, 5.5), sharex=True)
    axes[0].scatter(range(1, len(p) + 1), p, s=2, color=ORANGE, alpha=0.4, rasterized=True)
    style(axes[0], "", "min(1, e^(ΔE/T))", title)
    axes[0].set_ylim(-0.03, 1.03)
    # rata-rata bergerak supaya tren terlihat
    w = max(1, len(p) // 100)
    mov = [sum(p[i:i + w]) / len(p[i:i + w]) for i in range(0, len(p), w)]
    axes[1].plot([i * w + w / 2 for i in range(len(mov))], mov, color=BLUE, lw=2)
    style(axes[1], "iterasi", "rata-rata (jendela %d)" % w, "")
    axes[1].set_ylim(0, 1.03)
    return save(fig, name)


def row_text(r, vehicles, ship, label):
    lines = ["=" * 60, label, "=" * 60]
    for key, nm in (("initial_state", "state awal"), ("final_state", "state akhir")):
        lines.append("-- " + nm + " --")
        lines.append(render_deck(r[key], vehicles, ship))
        lines.append("  " + str(summarize(r[key], vehicles, ship)))
        lines.append("  luar kapal: " + ", ".join(
            k["vehicle_id"] for k in r[key] if not k["on_board"]))
    return "\n".join(lines)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "data", "demo.json")
    vehicles, ship = load_instance(path)
    name = os.path.basename(path).replace(".json", "")

    # batas atas (abaikan geometri): knapsack berat
    cap = ship["max_weight"]
    dp = [0] * (cap + 1)
    for v in vehicles.values():
        for w in range(cap, v["weight"] - 1, -1):
            dp[w] = max(dp[w], dp[w - v["weight"]] + v["shipping_fee"])
    upper = dp[cap]

    rows, dumps = [], []
    for algo, fn, params in (("HC", hill_climbing, HC_PARAMS),
                             ("SA", simulated_annealing, SA_PARAMS)):
        for seed in SEEDS:
            r = fn(vehicles, ship, seed=seed, **params)
            m = r["metrics"]
            info = summarize(r["final_state"], vehicles, ship)
            tag = "%s_%s_seed%d" % (algo, name, seed)
            title = "%s seed %d" % (algo, seed)
            plot_states(r, vehicles, ship, "states_" + tag + ".png", title)
            if algo == "HC":
                plot_hc(r, "obj_" + tag + ".png", title + ": objective vs iterasi")
            else:
                plot_sa(r, "obj_" + tag + ".png", title + ": objective vs iterasi")
                plot_sa_prob(r, "prob_" + tag + ".png",
                             title + ": e^(ΔE/T) vs iterasi")
            row = {
                "algo": algo, "seed": seed,
                "initial_value": r["history"][0], "final_value": m["final_value"],
                "iterations": m["iterations"], "duration_s": round(r["duration"], 3),
                "feasible": info["feasible"], "vehicles_on_board": info["vehicles_on_board"],
                "total_weight": info["total_weight"],
            }
            if algo == "HC":
                row.update(sideways_used=m["sideways_used"], max_sideways=m["max_sideways"],
                           stop_reason=m["stop_reason"], k_neighbors=m["k_neighbors"])
            else:
                row.update(T0=round(m["T0"], 2), alpha=round(m["alpha"], 6),
                           T_final=round(m["T_final"], 4), stuck_count=m["stuck_count"],
                           stuck_frequency=round(m["stuck_frequency"], 4),
                           accepted_worse=m["accepted_worse"])
            rows.append(row)
            dumps.append(row_text(r, vehicles, ship, tag + "  (objective akhir %s)" % m["final_value"]))
            print(tag, row["initial_value"], "->", row["final_value"], row["duration_s"], "s")

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "results_%s.json" % name), "w") as f:
        json.dump({"instance": name, "upper_bound_knapsack": upper,
                   "hc_params": HC_PARAMS, "sa_params": SA_PARAMS, "runs": rows}, f, indent=2)
    with open(os.path.join(OUT, "states_%s.txt" % name), "w") as f:
        f.write("\n\n".join(dumps))

    md = ["# Hasil HC (sideways) dan SA - instance %s" % name, "",
          "Batas atas objective (knapsack berat, abaikan geometri): **%s**" % upper, "",
          "## Hill-Climbing with Sideways Move", "",
          "| seed | objective awal | objective akhir | iterasi | sideways dipakai | max sideways | berhenti karena | durasi (s) |",
          "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["algo"] == "HC":
            md.append("| %d | %s | %s | %d | %d | %d | %s | %s |" % (
                r["seed"], r["initial_value"], r["final_value"], r["iterations"],
                r["sideways_used"], r["max_sideways"], r["stop_reason"], r["duration_s"]))
    md += ["", "## Simulated Annealing", "",
           "| seed | objective awal | objective akhir | iterasi | T0 | alpha | T akhir | stuck | frekuensi stuck | langkah buruk diterima | durasi (s) |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["algo"] == "SA":
            md.append("| %d | %s | %s | %d | %s | %s | %s | %d | %s | %d | %s |" % (
                r["seed"], r["initial_value"], r["final_value"], r["iterations"], r["T0"],
                r["alpha"], r["T_final"], r["stuck_count"], r["stuck_frequency"],
                r["accepted_worse"], r["duration_s"]))
    with open(os.path.join(OUT, "results_%s.md" % name), "w") as f:
        f.write("\n".join(md) + "\n")
    print("selesai ->", os.path.abspath(OUT))


if __name__ == "__main__":
    main()