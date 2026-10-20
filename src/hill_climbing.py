"""Hill-Climbing with Sideways Move.

Pseudocode
----------
    current <- initial_state (random, reproducible dari seed)
    sideways <- 0
    ulangi sampai max_iter:
        N <- sampel k neighbor acak dari current
        best <- neighbor dengan evaluate tertinggi (seri dipilih acak)
        jika evaluate(best) >  evaluate(current): current <- best; sideways <- 0
        jika evaluate(best) == evaluate(current): current <- best; sideways += 1
                                                  jika sideways > max_sideways: berhenti
        jika evaluate(best) <  evaluate(current): berhenti (local optimum)
    kembalikan current

Heuristik (untuk laporan): neighbor TIDAK dievaluasi seluruhnya karena
himpunannya besar (n kendaraan x W*L koordinat); tiap iterasi hanya
disampel `k` neighbor acak lalu diambil yang terbaik (steepest ascent pada
sampel). Neighbor dibangkitkan oleh neighbor_hcsa.random_neighbor.

Alasan memilih varian sideways: objective hanya menjumlahkan fee kendaraan
yang on_board, sehingga banyak move (menggeser / memutar kendaraan yang
sudah dalam kapal) menghasilkan delta = 0 (plateau). Steepest ascent murni
akan berhenti di plateau; sideways move memungkinkan menyeberangi plateau.
"""
import random
import time

from objective import evaluate
from state import copy_state
from neighbor_hcsa import make_initial, random_neighbors


def hill_climbing(vehicles, ship, max_sideways=100, max_iter=1000,
                  k_neighbors=200, seed=None, initial_state=None):
    start = time.perf_counter()
    rng = random.Random(seed)

    if initial_state is None:
        initial_state = make_initial(vehicles, ship, seed)
    initial_state = copy_state(initial_state)

    current = copy_state(initial_state)
    current_value = evaluate(current, vehicles, ship)

    history = [current_value]          # nilai objective per iterasi (monoton naik)
    state_history = [copy_state(current)]
    state_history_iter = [0]           # indeks iterasi tiap snapshot (index ke history)

    sideways_used = 0                  # total sideways move
    sideways_streak = 0                # sideways berturut-turut (yang dibatasi max_sideways)
    stop_reason = "max_iter"
    iterations = 0

    for it in range(1, max_iter + 1):
        cands = random_neighbors(current, vehicles, ship, rng, k_neighbors)
        values = [evaluate(c, vehicles, ship) for c in cands]
        best_value = max(values)
        best_idx = [i for i, v in enumerate(values) if v == best_value]
        chosen = cands[rng.choice(best_idx)]
        iterations = it

        if best_value > current_value:
            current, current_value = chosen, best_value
            sideways_streak = 0
            state_history.append(copy_state(current))
            state_history_iter.append(it)
        elif best_value == current_value:
            current = chosen
            sideways_used += 1
            sideways_streak += 1
            if sideways_streak > max_sideways:
                history.append(current_value)
                stop_reason = "max_sideways"
                break
        else:
            history.append(current_value)
            stop_reason = "local_optimum"
            break
        history.append(current_value)

    duration = time.perf_counter() - start
    return {
        "initial_state": initial_state,
        "final_state": current,
        "history": history,
        "duration": duration,
        "metrics": {
            "algorithm": "hill_climbing_sideways",
            "final_value": current_value,
            "iterations": iterations,
            "sideways_used": sideways_used,
            "max_sideways": max_sideways,
            "k_neighbors": k_neighbors,
            "max_iter": max_iter,
            "stop_reason": stop_reason,
            "seed": seed,
        },
        "state_history": state_history,
        "state_history_iter": state_history_iter,
    }