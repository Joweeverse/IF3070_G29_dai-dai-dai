import copy
import os
import random
import sys
import unittest

# Supaya "import main", "import objective", dst. bisa ditemukan
LOKASI = os.path.dirname(os.path.abspath(__file__))
for folder in [LOKASI, os.path.join(LOKASI, "src"), os.path.join(LOKASI, "..", "src")]:
    if os.path.exists(os.path.join(folder, "objective.py")):
        sys.path.insert(0, folder)

from main import load_instance
from objective import evaluate, summarize
from hill_climbing import hill_climbing
from simulated_annealing import simulated_annealing
from neighbor_hcsa import make_initial

# Cari file demo.json di beberapa kemungkinan lokasi
DEMO = None
for p in [os.path.join(LOKASI, "data", "demo.json"),
          os.path.join(LOKASI, "src", "data", "demo.json"),
          os.path.join(LOKASI, "..", "src", "data", "demo.json"),
          os.path.join(LOKASI, "..", "data", "demo.json")]:
    if DEMO is None and os.path.exists(p):
        DEMO = p

# kunci wajib ada, sesuai kontrak
MAIN_KEYS = ["initial_state", "final_state", "history", "duration", "metrics"]


def jalankan(nama, vehicles, ship, seed):
    # Parameter dibuat kecil supaya test cepat
    if nama == "hc":
        return hill_climbing(vehicles, ship, max_sideway=30, max_loop=200,
                             k_neighbors=60, seed=seed)
    return simulated_annealing(vehicles, ship, max_iter=3000, seed=seed)


class TestKontrak(unittest.TestCase):

    def setUp(self):
        self.vehicles, self.ship = load_instance(DEMO)

    def semua_hasil(self):
        # Mengembalikan daftar (nama, seed, hasil) untuk 2 algoritma x 3 seed
        daftar = []
        for nama in ["hc", "sa"]:
            for seed in [1, 2, 3]:
                daftar.append((nama, seed, jalankan(nama, self.vehicles, self.ship, seed)))
        return daftar

    def test_kunci_hasil_lengkap(self):
        for nama, seed, r in self.semua_hasil():
            for kunci in MAIN_KEYS:
                self.assertIn(kunci, r, nama + " seed " + str(seed))
            self.assertGreaterEqual(r["duration"], 0.0)

    def test_hasil_akhir_tidak_lebih_buruk_dari_awal(self):
        for nama, seed, r in self.semua_hasil():
            nilai_awal = evaluate(r["initial_state"], self.vehicles, self.ship)
            nilai_akhir = evaluate(r["final_state"], self.vehicles, self.ship)
            self.assertGreaterEqual(nilai_akhir, nilai_awal)
            self.assertEqual(r["history"][0], nilai_awal)
            self.assertEqual(r["history"][-1], nilai_akhir)
            self.assertEqual(r["metrics"]["final_value"], nilai_akhir)

    def test_history_tidak_pernah_turun(self):
        # history berisi nilai terbaik sejauh ini, jadi tidak boleh turun
        for nama, seed, r in self.semua_hasil():
            h = r["history"]
            for i in range(1, len(h)):
                self.assertGreaterEqual(h[i], h[i - 1])

    def test_panjang_history(self):
        for nama, seed, r in self.semua_hasil():
            iterasi = r["metrics"]["iterations"]
            self.assertEqual(len(r["history"]), iterasi + 1)
            if nama == "sa":
                m = r["metrics"]
                self.assertEqual(len(r["accept_prob_history"]), iterasi)
                self.assertEqual(len(r["history_current"]), iterasi + 1)
                for p in r["accept_prob_history"]:
                    self.assertTrue(0.0 <= p <= 1.0)
                # metrics tidak boleh berisi list panjang (nanti print_report kebanjiran)
                for nilai in m.values():
                    self.assertFalse(isinstance(nilai, list))
                self.assertAlmostEqual(m["stuck_frequency"], m["stuck_count"] / iterasi)

    def test_state_history_sesuai_history(self):
        for nama, seed, r in self.semua_hasil():
            self.assertEqual(len(r["state_history"]), len(r["state_history_iter"]))
            for i in range(len(r["state_history"])):
                state = r["state_history"][i]
                iterasi = r["state_history_iter"][i]
                self.assertEqual(evaluate(state, self.vehicles, self.ship),
                                 r["history"][iterasi])

    def test_bentuk_state_dan_hasil_akhir_valid(self):
        for nama, seed, r in self.semua_hasil():
            ids = []
            for k in r["final_state"]:
                ids.append(k["vehicle_id"])
            self.assertEqual(sorted(ids), sorted(self.vehicles))
            info = summarize(r["final_state"], self.vehicles, self.ship)
            self.assertTrue(info["feasible"])

    def test_seed_sama_hasil_sama(self):
        for nama in ["hc", "sa"]:
            a = jalankan(nama, self.vehicles, self.ship, 7)
            b = jalankan(nama, self.vehicles, self.ship, 7)
            self.assertEqual(a["initial_state"], b["initial_state"])
            self.assertEqual(a["final_state"], b["final_state"])
            self.assertEqual(a["history"], b["history"])

    def test_seed_beda_state_awal_beda(self):
        a = jalankan("hc", self.vehicles, self.ship, 1)
        b = jalankan("hc", self.vehicles, self.ship, 2)
        self.assertNotEqual(a["initial_state"], b["initial_state"])

    def test_tidak_mengganggu_random_global(self):
        random.seed(123)
        yang_diharapkan = random.random()
        random.seed(123)
        jalankan("hc", self.vehicles, self.ship, 1)
        jalankan("sa", self.vehicles, self.ship, 1)
        self.assertEqual(random.random(), yang_diharapkan)

    def test_batas_sideways(self):
        r = hill_climbing(self.vehicles, self.ship, max_sideway=5, max_loop=500, k_neighbors=60, seed=1)
        m = r["metrics"]
        self.assertIn(m["stop_reason"], ["max_sideways", "local_optimum", "max_iter"])
        if m["stop_reason"] == "max_sideways":
            self.assertGreaterEqual(m["sideway_used"], 6)

    def test_state_awal_yang_diberikan_dipakai_dan_tidak_berubah(self):
        awal = make_initial(self.vehicles, self.ship, 5)
        salinan = copy.deepcopy(awal)
        r = hill_climbing(self.vehicles, self.ship, max_loop=50, k_neighbors=30, seed=1, initial_state=awal)
        self.assertEqual(awal, salinan)
        self.assertEqual(r["initial_state"], salinan)


if __name__ == "__main__":
    unittest.main()