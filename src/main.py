import json
import sys

from state import random_state
from objective import evaluate
from visualize import print_report
from genetic_algorithm import genetic_algorithm
# from hill_climbing import hill_climbing
# from simulated_annealing import simulated_annealing


def load_instance(path):
    file = open(path)
    data = json.load(file)
    file.close()
    vehicles = {}
    for v in data["vehicles"]:
        vehicles[v["id"]] = v
    return vehicles, data["ship"]

def run_algorithm(nama, vehicles, ship):
    if nama == "genetic_algorithm" or nama == "ga":
        return genetic_algorithm(vehicles, ship, pop_size=100, generations=100)
    # elif nama == "simulated_annealing":
    #     return simulated_annealing(vehicles, ship)
    # elif nama == "hill_climbing":
    #     return hill_climbing(vehicles, ship)
    else:
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python main.py <instance.json> [algo]")
        sys.exit(1)

    # sys.argv[1] = file instance, sys.argv[2] (opsional) = nama algoritma
    vehicles, ship = load_instance(sys.argv[1])
    if len(sys.argv) > 2:
        nama_algoritma = sys.argv[2]
    else:
        nama_algoritma = "ga"
    result = run_algorithm(nama_algoritma, vehicles, ship)
    if result is None:
        print("algoritma '" + nama_algoritma + "' belum ada")
        sys.exit(1)
    print_report(result, vehicles, ship)

    # plot konvergensi, GIF, & frame awal/akhir
    import os
    folder_output = os.path.join(os.path.dirname(__file__), "..", "output")
    from plot import plot_convergent, draw_gif, export_state
    nama = sys.argv[1].replace("\\", "/").split("/")[-1].replace(".json", "")
    plot_convergent(result, os.path.join(folder_output, "graph_" + nama + ".png"))
    draw_gif(result, vehicles, ship, os.path.join(folder_output, "visualisasi_" + nama + ".gif"))
    export_state(result["initial_state"], vehicles, ship, os.path.join(folder_output, "initial_" + nama + ".png"))
    export_state(result["final_state"], vehicles, ship, os.path.join(folder_output, "final_" + nama + ".png"))
