import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from main import load_instance                      
from objective import evaluate, summarize           
from hill_climbing import hill_climbing             
from simulated_annealing import simulated_annealing 

DEMO = os.path.join(ROOT, "src", "data", "demo.json")
REQUIRED_KEYS = {"initial_state", "final_state", "history", "duration", "metrics"}

# parameter kecil supaya test cepat
RUNNERS = {
    "hc": lambda v, s, seed: hill_climbing(v, s, max_sideways=30, max_iter=200,
                                           k_neighbors=60, seed=seed),
    "sa": lambda v, s, seed: simulated_annealing(v, s, max_iter=3000, seed=seed),
}


class ContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vehicles, cls.ship = load_instance(DEMO)

    def run_all(self, check):
        for name, run in RUNNERS.items():
            for seed in (1, 2, 3):
                with self.subTest(algo=name, seed=seed):
                    check(name, run(self.vehicles, self.ship, seed))

    def test_keys(self):
        def check(name, r):
            self.assertTrue(REQUIRED_KEYS <= set(r), set(r))
            self.assertGreaterEqual(r["duration"], 0.0)
        self.run_all(check)

    def test_final_not_worse_than_initial(self):
        def check(name, r):
            v0 = evaluate(r["initial_state"], self.vehicles, self.ship)
            v1 = evaluate(r["final_state"], self.vehicles, self.ship)
            self.assertGreaterEqual(v1, v0)
            self.assertEqual(r["history"][0], v0)
            self.assertEqual(r["history"][-1], v1)
            self.assertEqual(r["metrics"]["final_value"], v1)
        self.run_all(check)

    def test_history_monotone_best_so_far(self):
        def check(name, r):
            h = r["history"]
            self.assertTrue(all(b >= a for a, b in zip(h, h[1:])))
        self.run_all(check)

    def test_history_length_consistent(self):
        def check(name, r):
            it = r["metrics"]["iterations"]
            self.assertEqual(len(r["history"]), it + 1)
            if name == "sa":
                m = r["metrics"]
                self.assertEqual(len(r["accept_prob_history"]), it)
                self.assertEqual(len(r["history_current"]), it + 1)
                self.assertTrue(all(0.0 <= p <= 1.0 for p in r["accept_prob_history"]))
                self.assertTrue(all(not isinstance(v, list) for v in m.values()))
                self.assertAlmostEqual(m["stuck_frequency"], m["stuck_count"] / it)
        self.run_all(check)

    def test_state_history_aligned(self):
        def check(name, r):
            self.assertEqual(len(r["state_history"]), len(r["state_history_iter"]))
            for st, it in zip(r["state_history"], r["state_history_iter"]):
                self.assertEqual(evaluate(st, self.vehicles, self.ship), r["history"][it])
        self.run_all(check)

    def test_state_shape_and_final_feasible(self):
        def check(name, r):
            ids = [k["vehicle_id"] for k in r["final_state"]]
            self.assertEqual(sorted(ids), sorted(self.vehicles))
            self.assertTrue(summarize(r["final_state"], self.vehicles, self.ship)["feasible"])
        self.run_all(check)

    def test_same_seed_same_result(self):
        for name, run in RUNNERS.items():
            with self.subTest(algo=name):
                a = run(self.vehicles, self.ship, 7)
                b = run(self.vehicles, self.ship, 7)
                self.assertEqual(a["final_state"], b["final_state"])
                self.assertEqual(a["initial_state"], b["initial_state"])
                self.assertEqual(a["history"], b["history"])

    def test_different_seed_different_initial(self):
        a = RUNNERS["hc"](self.vehicles, self.ship, 1)
        b = RUNNERS["hc"](self.vehicles, self.ship, 2)
        self.assertNotEqual(a["initial_state"], b["initial_state"])

    def test_does_not_touch_global_random(self):
        import random
        random.seed(123)
        expected = random.random()
        random.seed(123)
        RUNNERS["hc"](self.vehicles, self.ship, 1)
        RUNNERS["sa"](self.vehicles, self.ship, 1)
        self.assertEqual(random.random(), expected)

    def test_hc_sideways_limit_respected(self):
        r = hill_climbing(self.vehicles, self.ship, max_sideways=5, max_iter=500,
                          k_neighbors=60, seed=1)
        m = r["metrics"]
        self.assertIn(m["stop_reason"], ("max_sideways", "local_optimum", "max_iter"))
        if m["stop_reason"] == "max_sideways":
            self.assertEqual(m["sideways_used"] >= 6, True)

    def test_given_initial_state_is_used_and_not_mutated(self):
        import copy
        from neighbor_hcsa import make_initial
        init = make_initial(self.vehicles, self.ship, 5)
        snap = copy.deepcopy(init)
        r = hill_climbing(self.vehicles, self.ship, max_iter=50, k_neighbors=30,
                          seed=1, initial_state=init)
        self.assertEqual(init, snap)
        self.assertEqual(r["initial_state"], snap)


if __name__ == "__main__":
    unittest.main()