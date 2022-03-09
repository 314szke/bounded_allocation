from src.bounded_allocation import BoundedAllocationProblemSolver
from src.utils import ROUND


class Algorithm_1(BoundedAllocationProblemSolver):
    def __init__(self, input, verbose):
        BoundedAllocationProblemSolver.__init__(self, input, verbose)


    def solve(self, eta):
        self.doubt = ROUND(eta)
        self._init_solver()

        for item in self.items:
            remaining_fraction = self._allocate_for_one_buyer(item, 1.0)
            self._allocate_equally(item, remaining_fraction)

        self._calculate_objective_value()
        return self.objective_value
