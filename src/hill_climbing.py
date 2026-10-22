import random
import time

from objective import evaluate
from state import copy_state
from neighbor_hcsa import make_initial, random_neighbors


def hill_climbing(vehicles, ship, max_sideway=100, max_loop=1000, k_neighbors=200, seed=None, initial_state=None):
    start = time.perf_counter()
    rng = random.Random(seed)

    # State awal: kalau ga ada, buat acak
    if initial_state is None:
        initial_state = make_initial(vehicles, ship, seed)
    initial_state = copy_state(initial_state)

    cur = copy_state(initial_state)
    current_value = evaluate(cur, vehicles, ship)

    # hasil
    history = [current_value]                 # nilai objective di tiap loop
    state_history = [copy_state(cur)]     # state untuk perbaikan
    state_history_iter = [0]                  # loop ke berapa snapshot itu diambil

    sideway_used = 0      # total sideways move selama pencarian
    sideway_streak = 0    # streak move
    stop_reason = "max_iter"
    iterations = 0

    for it in range(1, max_loop + 1):
        iterations = it

        # buat tetangga dan cek satu2 nilainya
        candidates = random_neighbors(cur, vehicles, ship, rng, k_neighbors)
        values = []
        for c in candidates:
            values.append(evaluate(c, vehicles, ship))

        # cari neighboar paling tinggi nilainya (acak kalau ada yang sama nilainya)
        best = max(values)
        best_index = []
        for i in range(len(values)):
            if values[i] == best:
                best_index.append(i)
        chosen = candidates[rng.choice(best_index)]

        if best > current_value:
            # pindah saat lebih baik, streak direset
            cur = chosen
            current_value = best
            sideway_streak = 0
            state_history.append(copy_state(cur))
            state_history_iter.append(it)
        elif best == current_value:
            # pindah, streak sideway nambah 1
            cur = chosen
            sideway_used = sideway_used + 1
            sideway_streak = sideway_streak + 1
            if sideway_streak > max_sideway:
                history.append(current_value)
                stop_reason = "max_sideways"
                break
        else:
            # stop, semua tetangga lebih buruk
            history.append(current_value)
            stop_reason = "local_optimum"
            break

        history.append(current_value)

    duration = time.perf_counter() - start

    return {
        "initial_state": initial_state,
        "final_state": cur,
        "history": history,
        "duration": duration,
        "metrics": {
            "algorithm": "hill_climbing_sideways",
            "final_value": current_value,
            "iterations": iterations,
            "sideway_used": sideway_used,
            "max_sideways": max_sideway,
            "k_neighbors": k_neighbors,
            "max_iter": max_loop,
            "stop_reason": stop_reason,
            "seed": seed,
        },
        "state_history": state_history,
        "state_history_iter": state_history_iter,
    }