from src.bounded_allocation import BoundedAllocationProblemSolver
from src.utils import ROUND


class Algorithm_2(BoundedAllocationProblemSolver):
    def __init__(self, input, verbose):
        BoundedAllocationProblemSolver.__init__(self, input, verbose)
        self.allocation_step = ROUND(1 / (self.bound * 10))
        self.max_steps = int(1 / self.allocation_step)


    def _all_buyers_spent_enough(self, buyer_ids):
        for id in buyer_ids:
            if self.buyers[id].budget_fraction < self.doubt:
                return False
        return True


    def solve(self, eta):
        self.doubt = ROUND(eta)
        self._init_solver()

        for item in self.items:
            if item.prediction is None:
                self._allocate_equally(item, self.doubt)
            else:
                allocated = 0.0
                for _ in range(self.max_steps):
                    if self._all_buyers_spent_enough(item.interested_buyers):
                        break
                    self._allocate_equally(item, self.allocation_step)
                    allocated = ROUND(allocated + self.allocation_step)

                remaining_fraction = ROUND(1 - allocated)
                remaining_fraction = self._allocate_for_one_buyer(item, remaining_fraction)
                self._allocate_equally(item, remaining_fraction)

        self._calculate_objective_value()
        return self.objective_value
