from collections import defaultdict
from src.utils import ROUND


class BoundedAllocationSolver:
    def __init__(self, data, verbose):
        self.buyers = data.buyers
        self.items = data.items
        self.bound = data.bound
        self.verbose = verbose

        self.eta = 0.0
        self.objective_value = 0
        self.allocation_step = ROUND(1 / (self.bound * 10))
        self._init_solver()


    def _init_solver(self):
        for idx in range(len(self.buyers)):
            self.buyers[idx].reset()

        self.levels = [set() for _ in range(self.bound + 1)]
        for buyer in self.buyers:
            self.levels[0].add(buyer.id)

        self.assignment = [defaultdict(lambda: 0) for _ in self.buyers]


    def _update_buyer_level(self, buyer_id):
        for idx, level in enumerate(self.levels):
            if buyer_id in level:
                self.levels[idx].remove(buyer_id)
                break

        fraction = self.buyers[buyer_id].budget_fraction
        for idx in range(self.bound):
            lower_bound = ROUND(idx / self.bound)
            upper_bound = ROUND((idx + 1) / self.bound)
            if lower_bound <= fraction and fraction < upper_bound:
                self.levels[idx].add(buyer_id)
                break


    def _allocate_for_one_buyer(self, item, remaining_fraction):
        # If there is nothing to assign, return
        if remaining_fraction <= 0:
            return 0.0

        # If the prediction is to not sell, we do not assign the prediction fraction
        if item.prediction is None:
            return self.eta

        # The predicted buyer cannot buy the item, try to allocate it to other buyers
        if self.buyers[item.prediction].budget_fraction >= 1.0:
            return remaining_fraction

        prediction_fraction = ROUND(1.0 - self.eta)
        new_fraction = ROUND(remaining_fraction - prediction_fraction)

        if remaining_fraction < prediction_fraction:
            prediction_fraction = remaining_fraction
            new_fraction = 0.0

        available_budget = self.buyers[item.prediction].budget - self.buyers[item.prediction].spent
        price_fraction = ROUND(item.price * prediction_fraction)

        if price_fraction > available_budget:
            prediction_fraction = ROUND(available_budget / item.price)
            price_fraction = available_budget
            new_fraction = ROUND(remaining_fraction - prediction_fraction)

        self.assignment[item.prediction][item.id] = ROUND(self.assignment[item.prediction][item.id] + prediction_fraction)
        self.buyers[item.prediction].spend(price_fraction)
        self._update_buyer_level(item.prediction)

        return new_fraction


    def _get_buyers(self, item):
        for idx, level in enumerate(self.levels):
            buyers = level.intersection(item.interested_buyers)
            if len(buyers) != 0:
                return idx, buyers
        return -1, set()


    def _get_min_max_price(self, buyer_ids, fraction_bound):
        max_price = float('inf')
        for buyer_id in buyer_ids:
            available_fraction = ROUND(fraction_bound - self.buyers[buyer_id].budget_fraction)
            available_budget = ROUND(self.buyers[buyer_id].budget * available_fraction)
            if available_budget < max_price:
                max_price = available_budget
        return max_price


    def _allocate_on_level(self, item, remaining_fraction, level_idx, buyer_ids):
        fraction_bound = ROUND((level_idx + 1) / self.bound)
        exhausted_buyer_ids = set()
        last_round = False

        while len(buyer_ids) != 0:
            # Split the item equally among the buyers
            fraction_per_buyer = ROUND(remaining_fraction / len(buyer_ids))
            price_fraction_per_buyer = ROUND(item.price * fraction_per_buyer)

            # Max refers to the min spent amount with which at least one buyer changes level
            max_price_per_buyer = self._get_min_max_price(buyer_ids, fraction_bound)
            max_fraction_per_buyer = ROUND(max_price_per_buyer / item.price)

            # The item can be evenly split among the buyers without jumping to higher levels
            if price_fraction_per_buyer <= max_price_per_buyer:
                last_round = True
            else: # At lest one buyer jumps to a higher level with an equal item part
                fraction_per_buyer = max_fraction_per_buyer
                price_fraction_per_buyer = max_price_per_buyer

            for buyer_id in buyer_ids:
                self.assignment[buyer_id][item.id] = ROUND(self.assignment[buyer_id][item.id] + fraction_per_buyer)
                self.buyers[buyer_id].spend(price_fraction_per_buyer)
                if self.buyers[buyer_id].budget_fraction >= fraction_bound:
                    exhausted_buyer_ids.add(buyer_id)

            if last_round:
                return 0.0

            remaining_fraction = ROUND(remaining_fraction - (len(buyer_ids) * fraction_per_buyer))
            buyer_ids = buyer_ids.difference(exhausted_buyer_ids)

        return remaining_fraction


    def _update_level_sets(self, level_idx, buyer_ids):
        fraction_bound = ROUND((level_idx + 1) / self.bound)
        for buyer_id in buyer_ids:
            if self.buyers[buyer_id].budget_fraction >= fraction_bound:
                self.levels[level_idx].remove(buyer_id)
                self.levels[level_idx + 1].add(buyer_id)


    def _allocate_equally(self, item, remaining_fraction):
        while remaining_fraction > 0.0:
            # Get interested buyers from the lowest level
            level_idx, buyer_ids = self._get_buyers(item)

            # If no buyers is interested or all interested buyers exhausted their budget,
            # continue to the next item
            if level_idx == -1 or level_idx == self.bound:
                return

            # Allocate fractions of the item until all buyers change level or the item is fully allocated
            remaining_fraction = self._allocate_on_level(item, remaining_fraction, level_idx, buyer_ids)
            self._update_level_sets(level_idx, buyer_ids)


    def _needed_amount_to_reach_limit(self, buyer_ids):
        amount = 0.0
        for buyer_id in buyer_ids:
            if self.buyers[buyer_id].budget_fraction < self.eta:
                amount += (self.eta - self.buyers[buyer_id].budget_fraction) * self.buyers[buyer_id].budget
        return ROUND(amount)


    def _all_buyers_spent_enough(self, buyer_ids):
        for buyer_id in buyer_ids:
            if self.buyers[buyer_id].budget_fraction < self.eta:
                return False
        return True


    def _calculate_objective_value(self):
        self.objective_value = 0.0
        for sold_items in self.assignment:
            for item_id, fraction in sold_items.items():
                self.objective_value += self.items[item_id].price * fraction
        self.objective_value = ROUND(self.objective_value)


    def solve(self, eta):
        self.eta = ROUND(eta)
        self._init_solver()

        for item in self.items:
            if item.prediction is None:
                self._allocate_equally(item, self.eta)
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


    def get_solution_robustness(self, offline_objective_value):
        return ROUND(self.objective_value / offline_objective_value)


    def print_solution(self, error, offline_objective_value):
        print('The online solution:')
        print(f'Prediction error = {error}')
        print(f'Eta = {self.eta}')
        print(f'Objective value = {self.objective_value}')
        print(f'Robustness = {self.get_solution_robustness(offline_objective_value)}')
        if self.verbose:
            self.print_assignment()
        print()


    def print_assignment(self):
        for idx, items in enumerate(self.assignment):
            print(f'Buyer [{idx}] purchased: {dict(items)}')
