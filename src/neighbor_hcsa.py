import random

from state import random_state, get_dimensions, copy_state


def make_initial(vehicles, ship, seed):
    saved = random.getstate()
    try:
        random.seed(seed)
        return random_state(vehicles, ship)
    finally:
        random.setstate(saved)


def _random_fit_position(kendaraan, vehicles, ship, rng):
    """Koordinat acak yang membuat kendaraan muat di geladak (None jika tidak)."""
    w, h = get_dimensions(kendaraan, vehicles)
    max_x = ship["width"] - w
    max_y = ship["length"] - h
    if max_x < 0 or max_y < 0:
        return None
    return rng.randint(0, max_x), rng.randint(0, max_y)


def _on_board_indices(state):
    return [i for i, k in enumerate(state) if k["on_board"]]


def random_neighbor(state, vehicles, ship, rng):
    """Satu neighbor acak dari state. Mengembalikan state baru (deep copy)."""
    n = len(state)
    on_idx = _on_board_indices(state)

    # kalau belum ada kendaraan di kapal, satu-satunya move bermakna: toggle masuk
    if on_idx:
        jenis = rng.choice(["move", "move", "rotate", "toggle", "swap"])
    else:
        jenis = "toggle"

    new_state = copy_state(state)

    if jenis == "move":
        i = rng.choice(on_idx)
        pos = _random_fit_position(new_state[i], vehicles, ship, rng)
        if pos is not None:
            new_state[i]["x"], new_state[i]["y"] = pos
        return new_state

    if jenis == "rotate":
        i = rng.choice(on_idx)
        k = new_state[i]
        k["orientation"] = "V" if k["orientation"] == "H" else "H"
        w, h = get_dimensions(k, vehicles)
        k["x"] = max(0, min(k["x"], ship["width"] - w))
        k["y"] = max(0, min(k["y"], ship["length"] - h))
        return new_state

    if jenis == "swap" and n >= 2:
        i = rng.choice(on_idx)
        j = rng.randrange(n - 1)
        if j >= i:
            j += 1
        a, b = new_state[i], new_state[j]
        for key in ("on_board", "x", "y", "orientation"):
            a[key], b[key] = b[key], a[key]
        return new_state

    # toggle (juga fallback)
    i = rng.randrange(n)
    k = new_state[i]
    if k["on_board"]:
        k["on_board"] = False
    else:
        k["on_board"] = True
        pos = _random_fit_position(k, vehicles, ship, rng)
        if pos is not None:
            k["x"], k["y"] = pos
    return new_state


def random_neighbors(state, vehicles, ship, rng, k):
    """Sampel k neighbor acak (dipakai HC sebagai pengganti seluruh neighbor)."""
    return [random_neighbor(state, vehicles, ship, rng) for _ in range(k)]