import random
import copy


def get_vehicle(vehicles, vehicle_id):
    return vehicles[vehicle_id]


def random_state(vehicles, ship):
    state = []
    for vehicle_id in vehicles:
        kendaraan = {}
        kendaraan["vehicle_id"] = vehicle_id
        kendaraan["on_board"] = random.random() < 0.7
        kendaraan["x"] = random.randint(0, ship["width"] - 1)
        kendaraan["y"] = random.randint(0, ship["length"] - 1)
        if random.random() < 0.5:
            kendaraan["orientation"] = "H"
        else:
            kendaraan["orientation"] = "V"
        state.append(kendaraan)
    return state


def get_dimensions(kendaraan, vehicles):
    v = get_vehicle(vehicles, kendaraan["vehicle_id"])
    if kendaraan["orientation"] == "H":
        return v["width"], v["length"]
    else:
        return v["length"], v["width"]


def get_cells(kendaraan, vehicles):
    # semua cell (x, y) yang ditempati suatu kendaraan
    width, height = get_dimensions(kendaraan, vehicles)
    cells = []
    for dy in range(height):
        for dx in range(width):
            cell = (kendaraan["x"] + dx, kendaraan["y"] + dy)
            cells.append(cell)
    return cells


def copy_state(state):
    return copy.deepcopy(state)


def move_swap(state, i, j):
    new_state = copy_state(state)
    a = new_state[i]
    b = new_state[j]
    a["x"], b["x"] = b["x"], a["x"]
    a["y"], b["y"] = b["y"], a["y"]
    a["orientation"], b["orientation"] = b["orientation"], a["orientation"]
    return new_state


def move_to(state, i, x, y):
    new_state = copy_state(state)
    new_state[i]["x"] = x
    new_state[i]["y"] = y
    return new_state


def move_relocate(state, i, ship):
    # move ke random di geladak
    new_state = copy_state(state)
    new_state[i]["x"] = random.randint(0, ship["width"] - 1)
    new_state[i]["y"] = random.randint(0, ship["length"] - 1)
    return new_state


def move_rotate(state, i):
    # flip orientasi
    new_state = copy_state(state)
    if new_state[i]["orientation"] == "H":
        new_state[i]["orientation"] = "V"
    else:
        new_state[i]["orientation"] = "H"
    return new_state


def move_toggle(state, i):
    # kendaraan i keluar/masuk kapal
    new_state = copy_state(state)
    if new_state[i]["on_board"]:
        new_state[i]["on_board"] = False
    else:
        new_state[i]["on_board"] = True
    return new_state
