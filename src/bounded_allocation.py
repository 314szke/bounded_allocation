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
        self.levels = [set() for _ in range(self.bound + 1)]
        for buyer in self.buyers:
            self.levels[0].add(buyer.id)

        self.assignment = [{} for _ in self.buyers]
        self.objective_value = 0


    def _get_buyers(self, item):
        for idx, level in enumerate(self.levels):
            buyers = level.intersection(item.interested_buyers)
            if len(buyers) != 0:
                return idx, buyers
        return -1, set()


    def _get_min_max_budget(self, buyer_ids, fraction_bound):
        min_budget = float('inf')
        for id in buyer_ids:
            available_fraction = ROUND(fraction_bound - self.buyers[id].budget_fraction)
            available_budget = ROUND(self.buyers[id].budget * available_fraction)
            if available_budget < min_budget:
                min_budget = available_budget
        return min_budget


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
            # Split it item equally among the buyers
            fraction_per_buyer = ROUND(remaining_fraction / len(buyer_ids))
            price_fraction_per_buyer = ROUND(item.price * fraction_per_buyer)

            # Max refers to the fraction with which a buyer changes level
            max_price = self._get_min_max_budget(buyer_ids, fraction_bound)
            max_fraction = ROUND(max_price / item.price)

            # The item can be evenly split among the buyers without jumping to higher levels
            if price_fraction_per_buyer <= max_price:
                last_round = True
            # At lest one buyer jumps to higher level with an equal item part
            else:
                fraction_per_buyer = max_fraction
                price_fraction_per_buyer = max_price

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


    def _update_the_level_sets(self, buyer_ids, level_idx):
        fraction_bound = ROUND((level_idx + 1) / self.bound)
        for id in buyer_ids:
            if self.buyers[id].budget_fraction >= fraction_bound:
                self.levels[level_idx].remove(id)
                self.levels[level_idx + 1].add(id)


    def _allocate_for_one_buyer(self, item, remaining_fraction):
        pass


    def _allocate_equally(self, item, remaining_fraction):
        while remaining_fraction > 0.0:
            # Get interested buyers from the lowest level
            level_idx, buyer_ids = self._get_buyers(item)

            # If no buyers is interested or all interested buyers exhausted their budget,
            # continue to the next item
            if level_idx == -1 or level_idx == self.bound:
                return

            # Initialize assignment variables
            if remaining_fraction == 1.0:
                for id in buyer_ids:
                    self.assignment[id][item.id] = 0.0

            # Allocate fractions of the item until all buyers change level or the item is fully allocated
            remaining_fraction = self._allocate_on_level(item, remaining_fraction, level_idx, buyer_ids)
            self._update_the_level_sets(buyer_ids, level_idx)


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
            prediction_fraction = 1 - self.doubt
            remaining_fraction = self.doubt

            self._allocate_for_one_buyer(item, prediction_fraction)
            self._allocate_equally(item, remaining_fraction)

        self._calculate_objective_value()
        return self.objective_value


    def get_solution_gap(self, offline_objective_value):
        ratio = (self.objective_value / offline_objective_value)
        return  ROUND(((1.0 - ratio) * 100))


    def get_maximum_budget_violation(self):
        max_violation = 0.0
        for i, sold_item_fractions in enumerate(self.assignment):
            spent_money = 0
            for j, fraction in sold_item_fractions.items():
                spent_money += self.items[j].price * fraction
            spent_money = ROUND(spent_money)

            if spent_money > self.buyers[i].budget:
                fraction = ROUND((spent_money / self.buyers[i].budget) - 1)
                if fraction > max_violation:
                    max_violation = fraction

        return max_violation


    def print_solution(self, offline_objective_value):
        print('The online solution:')
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
