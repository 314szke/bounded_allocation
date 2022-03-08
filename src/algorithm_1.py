from src.bounded_allocation import BoundedAllocationProblemSolver
from src.utils import ROUND


class Algorithm_1(BoundedAllocationProblemSolver):
    def __init__(self, input, verbose):
        BoundedAllocationProblemSolver.__init__(self, input, verbose)


    def _allocate_for_one_buyer(self, item):
        # If the prediction is to not sell, we do not assign the prediction fraction
        if item.prediction is None:
            return self.doubt

        # The predicted buyer cannot buy the item, try to allocate it to other buyers
        if self.buyers[item.prediction].budget_fraction >= 1.0:
            return 1.0

        prediction_fraction = ROUND(1.0 - self.doubt)
        remaining_fraction = self.doubt

        available_budget = self.buyers[item.prediction].budget - self.buyers[item.prediction].spent
        price_fraction = ROUND(item.price * prediction_fraction)

        if price_fraction > available_budget:
            prediction_fraction = ROUND(available_budget / item.price)
            price_fraction = ROUND(item.price * prediction_fraction)
            remaining_fraction = ROUND(1.0 - prediction_fraction)

        self.assignment[item.prediction][item.id] = prediction_fraction
        self.buyers[item.prediction].spend(price_fraction)
        self._update_buyer_level(item.prediction)

        return remaining_fraction

    def solve(self, eta):
        self.doubt = ROUND(eta)
        self._init_solver()

        for item in self.items:
            remaining_fraction = self._allocate_for_one_buyer(item)
            self._allocate_equally(item, remaining_fraction)

        self._calculate_objective_value()
        return self.objective_value
