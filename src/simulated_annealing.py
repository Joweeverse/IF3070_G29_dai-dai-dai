"""Simulated Annealing.

Pseudocode
----------
    current <- initial_state (random, reproducible dari seed)
    best <- current
    T <- T0
    untuk it = 1 .. max_iter, selama T >= T_min:
        cand <- satu neighbor acak dari current
        dE <- evaluate(cand) - evaluate(current)
        p <- min(1, exp(dE / T))              # dicatat di accept_prob_history
        jika dE >= 0:            current <- cand
        selain itu, rand < p:    current <- cand        (terima langkah buruk)
        selain itu:              stuck_count += 1       (kandidat buruk ditolak)
        jika evaluate(current) > evaluate(best): best <- current
        T <- alpha * T                                  (cooling geometrik)
    kembalikan best

Definisi 'stuck' (untuk laporan): satu event stuck terjadi ketika kandidat
yang lebih buruk (dE < 0) ditolak karena rand >= exp(dE/T), yaitu search
bertahan di state saat ini. Frekuensi stuck = stuck_count / jumlah iterasi.

Nilai yang diplot untuk e^(dE/T): min(1, e^(dE/T)) per iterasi, sehingga
langkah membaik / sideways bernilai 1.0 dan langkah memburuk bernilai < 1.

history  = objective terbaik (best-so-far) per iterasi, sesuai kontrak.
result["history_current"] = objective state saat ini per iterasi (di luar metrics).
final_state = state terbaik yang pernah dikunjungi.

Kalibrasi T0 (jika T0=None): rata-rata dE negatif yang bermakna adalah
-mean(fee) (mengeluarkan satu kendaraan), lalu T0 = mean(fee) / -ln(p0) dengan
p0 = 0.8, sehingga langkah memburuk 'tipikal' di awal diterima dengan peluang
sekitar 0.8. Jika alpha None, alpha dipilih agar T turun dari T0 ke T_min
tepat pada max_iter (cooling geometrik).
"""
import math
import random
import time

from objective import evaluate
from state import copy_state
from neighbor_hcsa import make_initial, random_neighbor


def calibrate_t0(vehicles, p0=0.8):
    """T0 sehingga kehilangan satu kendaraan rata-rata diterima dengan peluang p0.

    Pada state yang feasible, langkah memburuk yang 'bermakna' adalah
    mengeluarkan kendaraan dari kapal (dE = -fee). Maka rata-rata dE negatif
    bernilai -mean(fee), dan exp(dE/T0) = p0  ->  T0 = mean(fee) / -ln(p0).
    Rata-rata dE negatif dari sampel neighbor state random TIDAK dipakai:
    ia didominasi penalty pelanggaran (200 per sel) sehingga T0 jauh terlalu
    panas dan sebagian besar iterasi terbuang di ruang tak-feasible.
    """
    fees = [v["shipping_fee"] for v in vehicles.values()]
    return (sum(fees) / len(fees)) / -math.log(p0)


def simulated_annealing(vehicles, ship, T0=None, alpha=None, T_min=0.1,
                        max_iter=20000, seed=None, initial_state=None,
                        p0=0.8):
    start = time.perf_counter()
    rng = random.Random(seed)

    if initial_state is None:
        initial_state = make_initial(vehicles, ship, seed)
    initial_state = copy_state(initial_state)

    # kalibrasi memakai rng terpisah agar urutan acak utama tidak tergeser
    if T0 is None:
        T0 = calibrate_t0(vehicles, p0=p0)
    if alpha is None:
        alpha = (T_min / T0) ** (1.0 / max_iter) if T0 > T_min else 0.995

    current = copy_state(initial_state)
    current_value = evaluate(current, vehicles, ship)
    best, best_value = copy_state(current), current_value

    history = [best_value]
    history_current = [current_value]
    accept_prob_history = []
    temperature_history = [T0]
    state_history = [copy_state(best)]
    state_history_iter = [0]

    stuck_count = 0
    accepted_worse = 0
    T = T0
    iterations = 0

    for it in range(1, max_iter + 1):
        if T < T_min:
            break
        cand = random_neighbor(current, vehicles, ship, rng)
        cand_value = evaluate(cand, vehicles, ship)
        dE = cand_value - current_value

        if dE >= 0:
            p = 1.0
            current, current_value = cand, cand_value
        else:
            p = math.exp(dE / T)
            if rng.random() < p:
                current, current_value = cand, cand_value
                accepted_worse += 1
            else:
                stuck_count += 1

        if current_value > best_value:
            best, best_value = copy_state(current), current_value
            state_history.append(copy_state(best))
            state_history_iter.append(it)

        accept_prob_history.append(p)
        history.append(best_value)
        history_current.append(current_value)
        T *= alpha
        temperature_history.append(T)
        iterations = it

    duration = time.perf_counter() - start
    return {
        "initial_state": initial_state,
        "final_state": best,
        "history": history,
        "duration": duration,
        "metrics": {
            "algorithm": "simulated_annealing",
            "final_value": best_value,
            "iterations": iterations,
            "T0": T0,
            "alpha": alpha,
            "T_min": T_min,
            "T_final": T,
            "stuck_count": stuck_count,
            "stuck_frequency": stuck_count / iterations if iterations else 0.0,
            "accepted_worse": accepted_worse,
            "max_iter": max_iter,
            "seed": seed,
        },
        # list panjang disimpan di luar metrics agar print_report tidak membanjiri terminal
        "accept_prob_history": accept_prob_history,   # min(1, e^(dE/T)) per iterasi
        "history_current": history_current,           # objective state saat ini per iterasi
        "temperature_history": temperature_history,
        "state_history": state_history,
        "state_history_iter": state_history_iter,
    }