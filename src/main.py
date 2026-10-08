import json
import sys

from objective import evaluate
# from hill_climbing import hill_climbing
# from simulated_annealing import simulated_annealing
# from genetic_algorithm import genetic_algorithm


def load_instance(path):
    with open(path) as f:
        data = json.load(f)
    vehicles = {v["id"]: v for v in data["vehicles"]}  # lookup by id
    return vehicles, data["ship"]


if __name__ == "__main__":
    vehicles, ship = load_instance(sys.argv[1])

    # TODO
