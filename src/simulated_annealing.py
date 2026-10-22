import math
import random
import time

from objective import evaluate
from state import copy_state
from neighbor_hcsa import make_initial, random_neighbor


def calibrate_t0(vehicles, p0=0.8):
    # set suhu awal
    # step diterima dengan peluang p0 (0.8) di awal: e^(-avg_fee / T0) = p0   ->   T0 = avg_fee / -ln(p0)
    sum_fee = 0
    for v in vehicles.values():
        sum_fee = sum_fee + v["shipping_fee"]
    avg_fee = sum_fee / len(vehicles)
    return avg_fee / -math.log(p0)


def simulated_annealing(vehicles, ship, T0=None, alpha=None, T_min=0.1, max_iter=20000, seed=None, initial_state=None, p0=0.8):
    start = time.perf_counter()
    rng = random.Random(seed)

    # state awal, kalau tidak ada, set acak
    if initial_state is None:
        initial_state = make_initial(vehicles, ship, seed)
    initial_state = copy_state(initial_state)

    # state suhu awal dan laju pendinginan.
    # kalau ga ada alpha, hitung manual berdaasarkan jumlah loop
    if T0 is None:
        T0 = calibrate_t0(vehicles, p0)
    if alpha is None:
        if T0 > T_min:
            alpha = (T_min / T0) ** (1.0 / max_iter)
        else:
            alpha = 0.995

    current = copy_state(initial_state)
    current_value = evaluate(current, vehicles, ship)
    best = copy_state(current)
    best_value = current_value

    # hasil
    history = [best_value]                    # nilai terbaik sementara
    history_current = [current_value]         # nilai state sekarang
    accept_prob_history = []                  # min(1, e^(dE/T)) per iterasi
    temperature_history = [T0]
    state_history = [copy_state(best)]
    state_history_iter = [0]

    count = 0       # berapa kali langkah buruk ditolak
    accepted_worse = 0    # berapa kali langkah buruk diterima
    T = T0
    iterations = 0

    for it in range(1, max_iter + 1):
        if T < T_min:
            break  # stop

        candidate = random_neighbor(current, vehicles, ship, rng)
        candidate_value = evaluate(candidate, vehicles, ship)
        dE = candidate_value - current_value

        if dE >= 0:
            #formula pasti: semua yang lebih atau sama baik selalu diterima
            p = 1.0
            current = candidate
            current_value = candidate_value
        else:
            #kalau lebih buruk, diterima dengan peluang e^(dE/T)
            p = math.exp(dE / T)
            if rng.random() < p:
                current = candidate
                current_value = candidate_value
                accepted_worse = accepted_worse + 1
            else:
                count = count + 1

        # simpan kalau ini state terbaik sejauh ini
        if current_value > best_value:
            best = copy_state(current)
            best_value = current_value
            state_history.append(copy_state(best))
            state_history_iter.append(it)

        accept_prob_history.append(p)
        history.append(best_value)
        history_current.append(current_value)

        T = T * alpha          # dinginkan
        temperature_history.append(T)
        iterations = it

    duration = time.perf_counter() - start

    if iterations > 0:
        stuck_frequency = count / iterations
    else:
        stuck_frequency = 0.0

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
            "stuck_count": count,
            "stuck_frequency": stuck_frequency,
            "accepted_worse": accepted_worse,
            "max_iter": max_iter,
            "seed": seed,
        },
        #list data sekunder disimpan di tempat lain
        "accept_prob_history": accept_prob_history,
        "history_current": history_current,
        "temperature_history": temperature_history,
        "state_history": state_history,
        "state_history_iter": state_history_iter,
    }