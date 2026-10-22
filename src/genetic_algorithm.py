import random
import time

from state import random_state, move_relocate, move_rotate, move_toggle, move_swap
from objective import evaluate

def initiate_pop(vehicles, ship, pop_size):
    populasi = []
    for i in range(pop_size):
        individu = random_state(vehicles, ship)
        populasi.append(individu)
    return populasi


def selection(populasi, scores):
    # normalisasi semua skor ke positif
    skor_terburuk = min(scores)
    fitness = []
    for skor in scores:
        nilai = skor - skor_terburuk + 1
        fitness.append(nilai)

    # sum total fitness, hitung persen tiap individu
    total = 0
    for nilai in fitness:
        total = total + nilai
    persen = []
    for nilai in fitness:
        persen.append(nilai / total * 100)

    # lempar dadu 0-100
    dadu = random.uniform(0, 100)
    batas = 0
    for i in range(len(persen)):
        batas = batas + persen[i]
        if dadu <= batas:
            return populasi[i]

    # fallback (klo dadu meleset dikit karna pembulatan desimal)
    return populasi[len(populasi) - 1]


def crossover(parent_a, parent_b):
    n = len(parent_a)
    titik = random.randint(1, n - 1)

    child_1 = []
    child_2 = []
    for i in range(n):
        if i < titik:
            child_1.append(dict(parent_a[i]))
            child_2.append(dict(parent_b[i]))
        else:
            child_1.append(dict(parent_b[i]))
            child_2.append(dict(parent_a[i]))
    return child_1, child_2


def mutasi(state, ship, mutation_rate):
    # ubah 1 kendaraan random sesuai mutation_rate
    # pindah posisi/putar orientasi/keluar-masuk kapal/tukar posisi 2 kendaraan
    if random.random() >= mutation_rate:
        return state
    i = random.randint(0, len(state) - 1)
    pilihan = random.randint(0, 3)
    if pilihan == 0:
        return move_relocate(state, i, ship)
    elif pilihan == 1:
        return move_rotate(state, i)
    elif pilihan == 2:
        return move_toggle(state, i)
    else:
        # swap: tukar posisi & orientasi kendaraan i dengan kendaraan random lain
        j = random.randint(0, len(state) - 1)
        while j == i:
            j = random.randint(0, len(state) - 1)
        return move_swap(state, i, j)


def genetic_algorithm(vehicles, ship, pop_size=50, generations=100, mutation_rate=0.2):
    start = time.time()

    populasi = initiate_pop(vehicles, ship, pop_size)

    # cari individu terbaik di populasi awal
    best = populasi[0]
    best_score = evaluate(best, vehicles, ship)
    for individu in populasi:
        score = evaluate(individu, vehicles, ship)
        if score > best_score:
            best = individu
            best_score = score

    initial_state = best

    history = [best_score]        # objective terbaik per generasi
    history_avg = [best_score]    # rata-rata objective populasi per generasi
    state_history = [copy(best)]  # state terbaik per generasi

    for generasi in range(generations):
        # hitung score semua individu sekali (utk roulette & rata-rata)
        scores = []
        for individu in populasi:
            scores.append(evaluate(individu, vehicles, ship))

        # elitisme 2 individu terbaik langsung ikut ke generasi berikutnya
        # ref: https://www.tutorialspoint.com/genetic_algorithms/genetic_algorithms_survivor_selection.htm
        idx_best_first = 0
        idx_best_second = 1
        if scores[idx_best_second] > scores[idx_best_first]:
            idx_best_first = 1
            idx_best_second = 0
        for i in range(2, len(populasi)):
            if scores[i] > scores[idx_best_first]:
                idx_best_second = idx_best_first
                idx_best_first = i
            elif scores[i] > scores[idx_best_second]:
                idx_best_second = i

        populasi_baru = [copy(populasi[idx_best_first]), copy(populasi[idx_best_second])]

        while len(populasi_baru) < pop_size:
            parent_a = selection(populasi, scores)
            parent_b = selection(populasi, scores)
            child_1, child_2 = crossover(parent_a, parent_b)
            child_1 = mutasi(child_1, ship, mutation_rate)
            child_2 = mutasi(child_2, ship, mutation_rate)
            populasi_baru.append(child_1)
            if len(populasi_baru) < pop_size:  # biar ga overload popsize
                populasi_baru.append(child_2)

        populasi = populasi_baru

        # update best + catat history (max & avg populasi)
        total = 0
        for individu in populasi:
            score = evaluate(individu, vehicles, ship)
            total = total + score
            if score > best_score:
                best = individu
                best_score = score
        rata_rata = total / len(populasi)

        history.append(best_score)
        history_avg.append(rata_rata)
        state_history.append(copy(best))

    return {
        "initial_state": initial_state,
        "final_state": best,
        "history": history,
        "duration": time.time() - start,
        "metrics": {
            "pop_size": pop_size,
            "generations": generations,
            "mutation_rate": mutation_rate,
            "best_score": best_score,
        },
        "history_avg": history_avg,
        "state_history": state_history
    }


def copy(state):
    hasil_copy = []
    for kendaraan in state:
        hasil_copy.append(dict(kendaraan))
    return hasil_copy
