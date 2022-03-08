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


    def _allocate_for_one_buyer(self, item, remaining_fraction):
        if remaining_fraction <= 0:
            return 0.0

        if self.buyers[item.prediction].budget_fraction >= 1.0:
            return remaining_fraction

        prediction_fraction = ROUND(1.0 - self.doubt)
        if remaining_fraction < prediction_fraction:
            prediction_fraction = remaining_fraction

        price_fraction = ROUND(item.price * prediction_fraction)
        available_budget = self.buyers[item.prediction].budget - self.buyers[item.prediction].spent

        if price_fraction > available_budget:
            prediction_fraction = ROUND(available_budget / item.price)
            price_fraction = ROUND(item.price * prediction_fraction)

        self._assign_fraction(item.prediction, item.id, prediction_fraction)
        self.buyers[item.prediction].spend(price_fraction)
        self._update_buyer_level(item.prediction)

        return ROUND(remaining_fraction - prediction_fraction)


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
