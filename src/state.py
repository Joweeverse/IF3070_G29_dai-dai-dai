import random
import copy


def random_state(vehicles, ship):
    # random initial state
    return [
        {
            "vehicle_id": v["id"],
            "on_board": random.random() < 0.7,
            "x": random.randint(0, ship["width"] - 1),
            "y": random.randint(0, ship["length"] - 1),
            "orientation": random.choice(["H", "V"]),
        }
        for v in vehicles
    ]


def get_dimensions(gene, vehicles):
    return todo


def get_cells(gene, vehicles):
    # semua cell (x, y) yang ditempati kendaraan
    return todo


def move_swap(state, i, j):
    # swap posisi & orientasi dua kendaraan
    return todo


def move_to(state, i, x, y):
    # move kendaraan i ke koordinat (x, y)
    return todo


def move_relocate(state, i, ship):
    # move kendaraan i ke koordinat random
    return todo


def move_rotate(state, i):
    # flip orientasi kendaraan i di tempat
    return todo


def move_toggle(state, i):
    # keluarkan/masukkan kendaraan dari/ke kapal
    return todo