from state import get_cells

PENALTY_OVERLAP = 1000      # per cell yang overlap
PENALTY_OUT_OF_BOUNDS = 1000  # per cell di luar geladak
PENALTY_OVERWEIGHT = 1000   # per satuan berat berlebih


def evaluate(state, vehicles, ship):
    fee, weight, penalty = 0, 0, 0
    # TODO ini fitness function
    return fee - penalty


def summarize(state, vehicles, ship):
    # TODO info detail output fee, berat, feasible/tidak
    raise NotImplementedError
