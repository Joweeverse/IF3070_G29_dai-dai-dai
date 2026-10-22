import random
import time

from objective import evaluate
from state import copy_state
from neighbor_hcsa import make_initial, random_neighbors

# Varian hill-climbing buat bonus 2: steepest ascent, stochastic, random restart.
# (sideways move ada di hill_climbing.py)
# Referensi: slide kuliah IF3070 (Hill-climbing) dan M. L. Khodra,
# "Beyond Classical Search: Hill-climbing Search", YouTube, 2021.
#
# Pembuatan tetangga sama kayak hill_climbing.py: k_neighbors tetangga acak
# tiap iterasi (sampling biar nggak lambat). Bedanya antar varian cuma di
# cara milih tetangganya.


def _state_awal(vehicles, ship, seed, initial_state):
    if initial_state is None:
        initial_state = make_initial(vehicles, ship, seed)
    return copy_state(initial_state)


def _bungkus(awal, final, history, state_history, state_iter, durasi, metrics):
    return {
        "initial_state": awal,
        "final_state": final,
        "history": history,
        "duration": durasi,
        "metrics": metrics,
        "state_history": state_history,
        "state_history_iter": state_iter,
    }


def _pilih_steepest(current, nilai_now, vehicles, ship, rng, k):
    # ambil tetangga terbaik, kalau seri pilih acak
    kandidat = random_neighbors(current, vehicles, ship, rng, k)
    nilai = [evaluate(c, vehicles, ship) for c in kandidat]
    terbaik = max(nilai)
    seri = [i for i, v in enumerate(nilai) if v == terbaik]
    return kandidat[rng.choice(seri)], terbaik


def _pilih_stochastic(current, nilai_now, vehicles, ship, rng, k):
    # acak di antara tetangga yang lebih baik dari current (bukan yang terbaik)
    kandidat = random_neighbors(current, vehicles, ship, rng, k)
    lebih_baik = []
    for c in kandidat:
        v = evaluate(c, vehicles, ship)
        if v > nilai_now:
            lebih_baik.append((c, v))
    if not lebih_baik:
        return None, nilai_now
    return rng.choice(lebih_baik)


def _mendaki(pilih, vehicles, ship, rng, awal, max_iter, k):
    # naik terus selama masih ada tetangga yang lebih baik
    current = copy_state(awal)
    nilai_now = evaluate(current, vehicles, ship)
    values = [nilai_now]
    states = [copy_state(current)]
    alasan = "max_iter"

    for _ in range(max_iter):
        nxt, nilai = pilih(current, nilai_now, vehicles, ship, rng, k)
        if nxt is None or nilai <= nilai_now:
            alasan = "local_optimum"
            values.append(nilai_now)
            states.append(copy_state(current))
            break
        current, nilai_now = nxt, nilai
        values.append(nilai_now)
        states.append(copy_state(current))

    return current, nilai_now, values, states, alasan


def _jalankan(nama, pilih, vehicles, ship, max_iter, k, seed, initial_state):
    t0 = time.perf_counter()
    rng = random.Random(seed)
    awal = _state_awal(vehicles, ship, seed, initial_state)
    final, nilai_final, history, states, alasan = _mendaki(
        pilih, vehicles, ship, rng, awal, max_iter, k)

    metrics = {
        "algorithm": nama,
        "final_value": nilai_final,
        "iterations": len(history) - 1,
        "k_neighbors": k,
        "max_iter": max_iter,
        "stop_reason": alasan,
        "seed": seed,
    }
    return _bungkus(awal, final, history, states, list(range(len(history))),
                    time.perf_counter() - t0, metrics)


def steepest_ascent(vehicles, ship, max_iter=1000, k_neighbors=200, seed=None,
                    initial_state=None):
    return _jalankan("hill_climbing_steepest_ascent", _pilih_steepest,
                     vehicles, ship, max_iter, k_neighbors, seed, initial_state)


def stochastic_hill_climbing(vehicles, ship, max_iter=1000, k_neighbors=200,
                             seed=None, initial_state=None):
    return _jalankan("hill_climbing_stochastic", _pilih_stochastic,
                     vehicles, ship, max_iter, k_neighbors, seed, initial_state)


def random_restart_hill_climbing(vehicles, ship, max_restart=10, max_iter=1000,
                                 k_neighbors=200, seed=None, initial_state=None):
    # tiap restart = 1 run steepest ascent dari state awal acak baru,
    # hasil akhirnya yang terbaik dari semua restart
    t0 = time.perf_counter()
    rng = random.Random(seed)
    base_seed = 0 if seed is None else seed

    awal_pertama = _state_awal(vehicles, ship, seed, initial_state)
    best = None
    best_value = None
    history = []
    state_history = []
    state_iter = []
    iter_per_restart = []

    for r in range(max_restart):
        if r == 0:
            awal = awal_pertama
        else:
            awal = make_initial(vehicles, ship, base_seed * 1000 + r)

        _, _, values, states, _ = _mendaki(
            _pilih_steepest, vehicles, ship, rng, awal, max_iter, k_neighbors)
        iter_per_restart.append(len(values) - 1)

        # gabung ke history global, isinya nilai terbaik sejauh ini
        for i, v in enumerate(values):
            if r > 0 and i == 0:
                continue  # nilai awal restart baru bukan iterasi
            if best_value is None or v > best_value:
                best_value = v
                best = copy_state(states[i])
                history.append(best_value)
                state_history.append(copy_state(best))
                state_iter.append(len(history) - 1)
            else:
                history.append(best_value)

    metrics = {
        "algorithm": "hill_climbing_random_restart",
        "final_value": best_value,
        "iterations": len(history) - 1,
        "restarts": max_restart,
        "max_restart": max_restart,
        "iterations_per_restart": iter_per_restart,
        "k_neighbors": k_neighbors,
        "max_iter": max_iter,
        "stop_reason": "max_restart",
        "seed": seed,
    }
    return _bungkus(awal_pertama, best, history, state_history, state_iter,
                    time.perf_counter() - t0, metrics)