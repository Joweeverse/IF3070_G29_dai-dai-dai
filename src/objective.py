from state import get_cells, get_vehicle

P_OVERLAP = 200
P_BOUNDS = 200
P_WEIGHT = 200

# "fee" = total fee kendaraan on_board, "eta" = fee dibobot ETA (bonus 1)
OBJECTIVE_MODE = "fee"


def set_objective(mode):
    global OBJECTIVE_MODE
    if mode not in ("fee", "eta"):
        raise ValueError("mode objective harus 'fee' atau 'eta'")
    OBJECTIVE_MODE = mode


def calc_fee(state, vehicles):
    total = 0
    for k in state:
        if k["on_board"]:
            total += get_vehicle(vehicles, k["vehicle_id"])["shipping_fee"]
    return total


def calc_fee_eta(state, vehicles):
    # makin kecil ETA makin urgent, bobot 1..2
    # bobot = 1 + (eta_max - eta) / eta_max
    eta_max = 0
    for v in vehicles.values():
        eta_max = max(eta_max, v.get("eta", 0))

    total = 0
    for k in state:
        if not k["on_board"]:
            continue
        v = get_vehicle(vehicles, k["vehicle_id"])
        bobot = 1
        if eta_max > 0:
            bobot = 1 + (eta_max - v.get("eta", eta_max)) / eta_max
        total += v["shipping_fee"] * bobot
    return total


def calc_nilai(state, vehicles):
    if OBJECTIVE_MODE == "eta":
        return calc_fee_eta(state, vehicles)
    return calc_fee(state, vehicles)


def calc_berat(state, vehicles):
    total = 0
    for k in state:
        if k["on_board"]:
            total += get_vehicle(vehicles, k["vehicle_id"])["weight"]
    return total


def calc_keluar_batas(state, vehicles, ship):
    count = 0
    for k in state:
        if not k["on_board"]:
            continue
        for x, y in get_cells(k, vehicles):
            if x < 0 or x >= ship["width"] or y < 0 or y >= ship["length"]:
                count += 1
    return count


def calc_overlap(state, vehicles, ship):
    # hitung cell kembar untuk tiap pasangan kendaraan
    count = 0
    n = len(state)
    for i in range(n):
        if not state[i]["on_board"]:
            continue
        ci = get_cells(state[i], vehicles)
        for j in range(i + 1, n):
            if not state[j]["on_board"]:
                continue
            cj = get_cells(state[j], vehicles)
            for c in ci:
                if c in cj:
                    count += 1
    return count


def calc_overweight(state, vehicles, ship):
    lebih = calc_berat(state, vehicles) - ship["max_weight"]
    return max(lebih, 0)


def evaluate(state, vehicles, ship):
    nilai = calc_nilai(state, vehicles)
    penalty = (P_OVERLAP * calc_overlap(state, vehicles, ship)
               + P_BOUNDS * calc_keluar_batas(state, vehicles, ship)
               + P_WEIGHT * calc_overweight(state, vehicles, ship))
    return nilai - penalty


def summarize(state, vehicles, ship):
    overlap = calc_overlap(state, vehicles, ship)
    keluar = calc_keluar_batas(state, vehicles, ship)
    overweight = calc_overweight(state, vehicles, ship)
    jumlah = sum(1 for k in state if k["on_board"])

    return {
        "total_fee": calc_fee(state, vehicles),
        "total_weight": calc_berat(state, vehicles),
        "vehicles_on_board": jumlah,
        "overlap_cells": overlap,
        "out_of_bounds_cells": keluar,
        "overweight_units": overweight,
        "feasible": overlap == 0 and keluar == 0 and overweight == 0,
    }