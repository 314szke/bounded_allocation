from src.bounded_allocation import BoundedAllocationProblemSolver
from src.utils import ROUND


class Algorithm_2(BoundedAllocationProblemSolver):
    def __init__(self, input, verbose):
        BoundedAllocationProblemSolver.__init__(self, input, verbose)
        self.allocation_step = ROUND(1 / (self.bound * 10))


    def _all_buyers_spent_enough(self, buyer_ids):
        for id in buyer_ids:
            if self.buyers[id].budget_fraction < self.doubt:
                return False
        return True


    def _needed_amount_to_reach_limit(self, buyer_ids):
        amount = 0.0
        for id in buyer_ids:
            if self.buyers[id].budget_fraction < self.doubt:
                amount += (self.doubt - self.buyers[id].budget_fraction) * self.buyers[id].budget
        return ROUND(amount)


    def solve(self, eta):
        self.doubt = ROUND(eta)
        self._init_solver()

        for item in self.items:
            if item.prediction is None:
                self._allocate_equally(item, self.doubt)
            else:
                amount = self._needed_amount_to_reach_limit(item.interested_buyers)
                fraction = 1.0

                if amount >= item.price:
                    self._allocate_equally(item, fraction)
                else:
                    fraction = ROUND(amount / item.price)
                    self._allocate_equally(item, fraction)

                    max_steps = int((1 - fraction) / self.allocation_step)
                    for _ in range(max_steps):
                        if self._all_buyers_spent_enough(item.interested_buyers):
                            break
                        self._allocate_equally(item, self.allocation_step)
                        fraction = ROUND(fraction + self.allocation_step)

                remaining_fraction = ROUND(1 - fraction)
                remaining_fraction = self._allocate_for_one_buyer(item, remaining_fraction)
                self._allocate_equally(item, remaining_fraction)

        self._calculate_objective_value()
        return self.objective_value
