from state import get_cells, get_vehicle
from objective import summarize


def render_deck(state, vehicles, ship):
    # draw geladak kapal dlm bentuk grid teks
    # '.' = kosong, huruf = kendaraan, '#' = cell di luar batas
    width = ship["width"]
    length = ship["length"]

    # grid kosong
    grid = []
    for y in range(length):
        baris = []
        for x in range(width):
            baris.append(".")
        grid.append(baris)

    # isi grid dengan kendaraan yang on_board
    for kendaraan in state:
        if not kendaraan["on_board"]:
            continue
        v = get_vehicle(vehicles, kendaraan["vehicle_id"])
        label = v["id"][0]
        cells = get_cells(kendaraan, vehicles)
        for cell in cells:
            x = cell[0]
            y = cell[1]
            if 0 <= x < width and 0 <= y < length:
                grid[y][x] = label
            else:
                # keluar batas pakai '#'
                if x < 0:
                    x = 0
                if x >= width:
                    x = width - 1
                if y < 0:
                    y = 0
                if y >= length:
                    y = length - 1
                grid[y][x] = "#"

    # susun
    hasil = []
    nomor_kolom = "    "
    for x in range(width):
        nomor_kolom = nomor_kolom + str(x % 10)
    hasil.append(nomor_kolom)

    for y in range(length):
        teks = str(y)
        while len(teks) < 3:
            teks = " " + teks
        teks = teks + " "
        for x in range(width):
            teks = teks + grid[y][x]
        hasil.append(teks)

    return "\n".join(hasil)


def print_report(result, vehicles, ship):
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("duration : " + str(result["duration"]))
    print("metrics  : " + str(result["metrics"]))

    print("")
    print("-- initial state --")
    print(render_deck(result["initial_state"], vehicles, ship))
    info = summarize(result["initial_state"], vehicles, ship)
    print("  " + str(info))

    print("")
    print("-- final state (best) --")
    print(render_deck(result["final_state"], vehicles, ship))
    info = summarize(result["final_state"], vehicles, ship)
    print("  " + str(info))
    if info["feasible"]:
        print("  feasible: YA")
    else:
        print("  feasible: TIDAK")

    history = result["history"]
    if len(history) > 0:
        print("")
        print("history  : " + str(len(history)) + " entries, "
              + "first=" + str(history[0])
              + ", last=" + str(history[-1]))
    print("=" * 60)
