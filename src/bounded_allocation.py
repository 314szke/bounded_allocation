from src.utils import ROUND

class BoundedAllocationProblemSolver:
    def __init__(self, input, verbose):
        self.buyers = input.buyers
        self.items = input.items
        self.bound = input.bound
        self.verbose = verbose
        self.doubt = 0.0
        self._init_solver()


    def _init_solver(self):
        for idx in range(len(self.buyers)):
            self.buyers[idx].reset()

        self.levels = [set() for _ in range(self.bound + 1)]
        for buyer in self.buyers:
            self.levels[0].add(buyer.id)

        self.assignment = [{} for _ in self.buyers]
        self.objective_value = 0


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


    def _get_buyers(self, item):
        for idx, level in enumerate(self.levels):
            buyers = level.intersection(item.interested_buyers)
            if len(buyers) != 0:
                return idx, buyers
        return -1, set()


    def _get_min_max_price(self, buyer_ids, fraction_bound):
        max_price = float('inf')
        for id in buyer_ids:
            available_fraction = ROUND(fraction_bound - self.buyers[id].budget_fraction)
            available_budget = ROUND(self.buyers[id].budget * available_fraction)
            if available_budget < max_price:
                max_price = available_budget
        return max_price


    def _assign_fraction(self, buyer_id, item_id, fraction):
        try:
            self.assignment[buyer_id][item_id] = ROUND(self.assignment[buyer_id][item_id] + fraction)
        except:
            self.assignment[buyer_id][item_id] = fraction


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

            for id in buyer_ids:
                self._assign_fraction(id, item.id, fraction_per_buyer)
                self.buyers[id].spend(price_fraction_per_buyer)
                if self.buyers[id].budget_fraction >= fraction_bound:
                    exhausted_buyer_ids.add(id)

            if last_round:
                return 0.0

            remaining_fraction = ROUND(remaining_fraction - (len(buyer_ids) * fraction_per_buyer))
            buyer_ids = buyer_ids.difference(exhausted_buyer_ids)

        return remaining_fraction


    def _update_level_sets(self, level_idx, buyer_ids):
        fraction_bound = ROUND((level_idx + 1) / self.bound)
        for id in buyer_ids:
            if self.buyers[id].budget_fraction >= fraction_bound:
                self.levels[level_idx].remove(id)
                self.levels[level_idx + 1].add(id)


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


    def _calculate_objective_value(self):
        self.objective_value = 0.0
        for sold_items in self.assignment:
            for id, fraction in sold_items.items():
                self.objective_value += self.items[id].price * fraction
        self.objective_value = ROUND(self.objective_value)


    def solve(self, eta):
        self.doubt = ROUND(eta)
        self._init_solver()

        for item in self.items:
            remaining_fraction = self._allocate_for_one_buyer(item)
            self._allocate_equally(item, remaining_fraction)

        self._calculate_objective_value()
        return self.objective_value


    def get_solution_gap(self, offline_objective_value):
        ratio = (self.objective_value / offline_objective_value)
        return  ROUND(((1.0 - ratio) * 100))


    def print_solution(self, error, offline_objective_value):
        print('The online solution:')
        print(f'Prediction error = {error}')
        print(f'Eta = {self.doubt}')
        print(f'Objective value = {self.objective_value}')
        print(f'Gap = {self.get_solution_gap(offline_objective_value)} %')
        if self.verbose:
            for idx, items in enumerate(self.assignment):
                print(f'Buyer [{idx}] purchased: {items}')
        print()


    def print(self):
        print('The problem instance:')
        for buyer in self.buyers:
            print(buyer)
        print()

        for item in self.items:
            print(item)
        print()

        self.print_solution()
