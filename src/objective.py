from state import get_cells, get_vehicle

PENALTY_OVERLAP = 200        # per cell yang overlap
PENALTY_OUT_OF_BOUNDS = 200  # per cell di luar geladak
PENALTY_OVERWEIGHT = 200     # per satuan berat berlebih


def calc_fee(state, vehicles):
    # total shipping fee semua kendaraan yang on_board
    fee = 0
    for kendaraan in state:
        if kendaraan["on_board"]:
            v = get_vehicle(vehicles, kendaraan["vehicle_id"])
            fee = fee + v["shipping_fee"]
    return fee


def calc_berat(state, vehicles):
    # total berat semua kendaraan yang on_board
    berat = 0
    for kendaraan in state:
        if kendaraan["on_board"]:
            v = get_vehicle(vehicles, kendaraan["vehicle_id"])
            berat = berat + v["weight"]
    return berat


def calc_keluar_batas(state, vehicles, ship):
    # jumlah cell yang berada di luar batas kapal
    jumlah = 0
    for kendaraan in state:
        if kendaraan["on_board"]:
            cells = get_cells(kendaraan, vehicles)
            for cell in cells:
                x = cell[0]
                y = cell[1]
                if x < 0 or x >= ship["width"] or y < 0 or y >= ship["length"]:
                    jumlah = jumlah + 1
    return jumlah


def calc_overlap(state, vehicles, ship):
    # jumlah cell yang ditempati lebih dari 1 kendaraan (yang kelebihan dihitung jg)
    jumlah = 0
    for i in range(len(state)):
        if not state[i]["on_board"]:
            continue
        cells_i = get_cells(state[i], vehicles)
        for j in range(i + 1, len(state)):
            if not state[j]["on_board"]:
                continue
            cells_j = get_cells(state[j], vehicles)
            # cek cell yang sama
            for cell in cells_i:
                if cell in cells_j:
                    jumlah = jumlah + 1
    return jumlah


def calc_overweight(state, vehicles, ship):
    berat = calc_berat(state, vehicles)
    lebih = berat - ship["max_weight"]
    if lebih < 0:
        return 0
    return lebih


def evaluate(state, vehicles, ship):
    fee = calc_fee(state, vehicles)
    overlap = calc_overlap(state, vehicles, ship)
    keluar = calc_keluar_batas(state, vehicles, ship)
    overweight = calc_overweight(state, vehicles, ship)
    penalty = (PENALTY_OVERLAP * overlap
               + PENALTY_OUT_OF_BOUNDS * keluar
               + PENALTY_OVERWEIGHT * overweight)
    return fee - penalty


def summarize(state, vehicles, ship):
    # info detail: fee, berat, pelanggaran, feasible/tidak
    fee = calc_fee(state, vehicles)
    berat = calc_berat(state, vehicles)
    overlap = calc_overlap(state, vehicles, ship)
    keluar = calc_keluar_batas(state, vehicles, ship)
    overweight = calc_overweight(state, vehicles, ship)

    # hitung jumlah kendaraan on_board
    on_board = 0
    for kendaraan in state:
        if kendaraan["on_board"]:
            on_board = on_board + 1

    if overlap == 0 and keluar == 0 and overweight == 0:
        feasible = True
    else:
        feasible = False

    return {
        "total_fee": fee,
        "total_weight": berat,
        "vehicles_on_board": on_board,
        "overlap_cells": overlap,
        "out_of_bounds_cells": keluar,
        "overweight_units": overweight,
        "feasible": feasible,
    }
