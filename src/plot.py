import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation, PillowWriter

from state import get_dimensions, get_cells
from objective import evaluate

WARNA = ["#60a5fa", "#f87171", "#34d399", "#fbbf24", "#a78bfa",
         "#f472b6", "#22d3ee", "#fb923c", "#4ade80", "#c084fc",
         "#e879f9", "#facc15", "#38bdf8", "#fca5a5", "#86efac"]

# fps gif
FREEZE_FRAMES = 45


def warna_kendaraan(vehicle_id, vehicles):
    ids = list(vehicles.keys())
    index = ids.index(vehicle_id)
    return WARNA[index % len(WARNA)]


def plot_convergent(result, path):
    # grafik objective max & rata-rata populasi vs iterasi
    history = result["history"]
    iterasi = []
    for i in range(len(history)):
        iterasi.append(i)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(iterasi, history, color="#2563eb", label="terbaik (max)")
    if "history_avg" in result:
        ax.plot(iterasi, result["history_avg"], color="#9ca3af",
                linestyle="--", label="rata-rata populasi")
    ax.set_xlabel("iterasi")
    ax.set_ylabel("objective")
    ax.set_title("konvergensi objective")
    ax.legend()
    ax.grid(True, alpha=0.3)

    make_folder(path)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("plot      : " + path)


def constraint_check(kendaraan, state, vehicles, ship):
    # cek overlap & out of bound
    cells = get_cells(kendaraan, vehicles)

    # cek out of bound
    for cell in cells:
        x = cell[0]
        y = cell[1]
        if x < 0 or x >= ship["width"] or y < 0 or y >= ship["length"]:
            return True

    # cek overlap
    for kendaraan in state:
        if not kendaraan["on_board"]:
            continue
        if kendaraan["vehicle_id"] == kendaraan["vehicle_id"]:
            continue
        cells_kendaraan = get_cells(kendaraan, vehicles)
        for cell in cells:
            if cell in cells_kendaraan:
                return True

    return False


def draw_panel(ax, state, vehicles, ship, judul, di_kapal):
    # draw 1 panel
    
    # kapal
    if di_kapal:
        panel_width = ship["width"]
        panel_length = ship["length"]
    else:
        # dermaga
        jumlah = 0
        for kendaraan in state:
            if not kendaraan["on_board"]:
                jumlah = jumlah + 1
        if jumlah == 0:
            jumlah = 1
        panel_width = 4
        panel_length = jumlah

    # latar panel
    ax.add_patch(Rectangle((0, 0), panel_width, panel_length,
                           facecolor="#f3f4f6", edgecolor="#111827"))
    ax.set_xlim(-0.5, panel_width + 0.5)
    ax.set_ylim(panel_length + 0.5, -0.5)  # sumbu y dibalik biar y ke bawah
    ax.set_aspect("equal")
    ax.set_title(judul, fontsize=10)
    ax.set_xticks([])
    ax.set_yticks([])

    # draw kendaraan
    nomor_dermaga = 0
    for kendaraan in state:
        if kendaraan["on_board"] != di_kapal:
            continue
        v = vehicles[kendaraan["vehicle_id"]]
        width, height = get_dimensions(kendaraan, vehicles)
        warna = warna_kendaraan(kendaraan["vehicle_id"], vehicles)

        if di_kapal:
            x = kendaraan["x"]
            y = kendaraan["y"]
        else:
            # kendaraan di dermaga disusun ke bawah
            x = 0.5
            y = nomor_dermaga + 0.1
            nomor_dermaga = nomor_dermaga + 1
            if height > 1:
                height = 1

        # border merah utk pelanggaran constraint (overlap / out of bound)
        if di_kapal and constraint_check(kendaraan, state, vehicles, ship):
            warna_border = "#dc2626"
            tebal_border = 2.5
        else:
            warna_border = "#111827"
            tebal_border = 1.0

        ax.add_patch(Rectangle((x, y), width, height,
                               facecolor=warna, edgecolor=warna_border,
                               linewidth=tebal_border))

        # label id kendaraan di tengah container
        ax.text(x + width / 2, y + height / 2, v["id"],
                ha="center", va="center", fontsize=8, fontweight="bold")


def draw_gif(result, vehicles, ship, path):
    if "state_history" not in result or len(result["state_history"]) == 0:
        print("gif       : dilewati (algoritma tidak punya state_history)")
        return

    frames = result["state_history"]
    history = result["history"]

    fig, (ax_kapal, ax_dermaga) = plt.subplots(
        1, 2, figsize=(7, 6), width_ratios=[ship["width"], 4])

    daftar_frame = []
    for i in range(len(frames)):
        daftar_frame.append(i)
    for i in range(FREEZE_FRAMES):
        daftar_frame.append(len(frames) - 1)

    def update(i):
        ax_kapal.clear()
        ax_dermaga.clear()
        state = frames[i]
        draw_panel(ax_kapal, state, vehicles, ship, "geladak kapal", True)
        draw_panel(ax_dermaga, state, vehicles, ship, "dermaga", False)
        score = history[i]
        fig.suptitle("generasi " + str(i) + " | objective: " + str(score),
                     fontsize=12)

    anim = FuncAnimation(fig, update, frames=daftar_frame, interval=50)
    make_folder(path)
    anim.save(path, writer=PillowWriter(fps=15))
    plt.close(fig)
    print("gif       : " + path + " (" + str(len(daftar_frame)) + " frame)")


def make_folder(path):
    folder = os.path.dirname(path)
    if folder != "" and not os.path.exists(folder):
        os.makedirs(folder)
