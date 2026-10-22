import random

from state import random_state, get_dimensions, copy_state

def make_initial(vehicles, ship, seed):
    # random_state() pakai random global
    # simpan, set seed, buat state, kembalikan random global ke kondisi awal
    init = random.getstate()
    random.seed(seed)
    state = random_state(vehicles, ship)
    random.setstate(init)
    return state


def random_position(kendaraan, vehicles, ship, rng):
    # pilih posisi acak (x, y)
    width, height = get_dimensions(kendaraan, vehicles)
    x_max = ship["width"] - width
    y_max = ship["length"] - height
    if x_max < 0 or y_max < 0:
        return None  # kendaraan lebih besar dari kapal, ga muat
    x = rng.randint(0, x_max)
    y = rng.randint(0, y_max)
    return x, y


def random_neighbor(state, vehicles, ship, rng):
    # buat satu neighbor acak
    result = len(state)

    # kendaraan yang ada di kapal dicatat
    on_board = []
    for temp in range(result):
        if state[temp]["on_board"]:
            on_board.append(temp)

    # pilih langkah, move ada 2 agar peluangnya lebih besar kepilih
    if len(on_board) > 0:
        type = rng.choice(["move", "move", "rotate", "toggle", "swap"])
    else:
        type = "toggle"

    new_state = copy_state(state)

    if type == "move":
        temp = rng.choice(on_board)
        pos = random_position(new_state[temp], vehicles, ship, rng)
        if pos is not None:
            new_state[temp]["x"] = pos[0]
            new_state[temp]["y"] = pos[1]
        return new_state

    if type == "rotate":
        temp = rng.choice(on_board)
        new = new_state[temp]
        if new["orientation"] == "H":
            new["orientation"] = "V"
        else:
            new["orientation"] = "H"
        # Setelah diputar ukurannya berubah, geser kalau jadi keluar dari geladak.
        width, height = get_dimensions(new, vehicles)
        new["x"] = max(0, min(new["x"], ship["width"] - width))
        new["y"] = max(0, min(new["y"], ship["length"] - height))
        return new_state

    if type == "swap" and result >= 2:
        temp = rng.choice(on_board)       # kendaraan pertama harus di kapal
        j = rng.randrange(result - 1)       # kendaraan kedua: sembarang yang bukan i
        if j >= temp:
            j = j + 1
        a = new_state[temp]
        b = new_state[j]
        for key in ["on_board", "x", "y", "orientation"]:
            a[key], b[key] = b[key], a[key]
        return new_state

    # else: toggle
    temp = rng.randrange(result)
    new = new_state[temp]
    if new["on_board"]:
        new["on_board"] = False
    else:
        new["on_board"] = True
        # Kalau masuk kapal, beri posisi acak yang muat.
        pos = random_position(new, vehicles, ship, rng)
        if pos is not None:
            new["x"] = pos[0]
            new["y"] = pos[1]
    return new_state


def random_neighbors(state, vehicles, ship, rng, k):
    # Membuat k tetangga acak sekaligus (dipakai Hill-Climbing).
    hasil = []
    for _ in range(k):
        hasil.append(random_neighbor(state, vehicles, ship, rng))
    return hasil