import json
import os
import pulp

from src.utils import ROUND

class LPSolverWrapper:
    def __init__(self, data, cache_file, verbose):
        self.buyers = data.buyers
        self.buyer_ids = data.buyer_ids

        self.items = data.items
        self.item_ids = data.item_ids

        self.budgets = [x.budget for x in data.buyers]
        self.prices = [x.price for x in data.items]

        self.cache_file = cache_file
        self.verbose = verbose
        self.print_solver_messages = (self.verbose == 2)

        self.status = None
        self.integral_objective_value = 0
        self.integral_solution = []
        self.fractional_objective_value = 0
        self.fractional_solution = []


    def _load_data_from_cache(self):
        print('Load LP data from cache file.')
        with open(self.cache_file, 'r') as in_file:
            data = json.load(in_file)
            self.status = data['status']
            self.integral_objective_value = data['integral_objective_value']
            self.fractional_objective_value = data['fractional_objective_value']

            # The json format converts the integral keys to strings, so we convert it back
            self.integral_solution = []
            for dictionary in data['integral_solution']:
                self.integral_solution.append({int(key): value for key, value in dictionary.items()})

            self.fractional_solution = []
            for dictionary in data['fractional_solution']:
                self.fractional_solution.append({int(key): value for key, value in dictionary.items()})


    def _save_data_to_cache(self):
        data = {
            'status': self.status,
            'integral_objective_value': self.integral_objective_value,
            'integral_solution': self.integral_solution,
            'fractional_objective_value': self.fractional_objective_value,
            'fractional_solution': self.fractional_solution
        }
        with open(self.cache_file, 'w+') as out_file:
            json.dump(data, out_file, indent=4)


    def _init_model(self, category):
        # Define the variables
        self.vars = []
        for i in self.buyer_ids:
            buyer_variables = {}
            for j in self.buyers[i].wanted_item_ids:
                buyer_variables[j] = pulp.LpVariable(name=f"y{i}_{j}", cat=category, lowBound=0)
            self.vars.append(buyer_variables)

        # Objective value
        weighted_vars = []
        for i in self.buyer_ids:
            for j in self.buyers[i].wanted_item_ids:
                weighted_vars.append(self.prices[j] * self.vars[i][j])
        self.model += pulp.lpSum(weighted_vars)

        # Constraints
        for j in self.item_ids:
            self.model += (pulp.lpSum(self.vars[i][j] for i in self.items[j].interested_buyers) <= 1, f"item_fraction_{j}")
        for i in self.buyer_ids:
            self.model += (pulp.lpSum(self.prices[j] * self.vars[i][j] for j in self.buyers[i].wanted_item_ids) <= self.budgets[i], f"budget_{i}")


    def _get_solution(self):
        self.solution = []
        for i in self.buyer_ids:
            buyer_variables = {}
            for j in self.buyers[i].wanted_item_ids:
                buyer_variables[j] = self.vars[i][j].varValue
            self.solution.append(buyer_variables)
        return self.solution


    def solve(self):
        if os.path.exists(self.cache_file):
            self._load_data_from_cache()
            return self.fractional_objective_value

        self.model = pulp.LpProblem(name='max-profit-bounded-allocation', sense=pulp.LpMaximize)
        self._init_model('Binary')
        self.model.solve(pulp.GUROBI_CMD(msg=self.print_solver_messages))
        self.status = self.model.status
        self.integral_objective_value = self.model.objective.value()
        self.integral_solution = self._get_solution()

        self.model = pulp.LpProblem(name='max-profit-bounded-allocation', sense=pulp.LpMaximize)
        self._init_model("Continuous")
        self.model.solve(pulp.GUROBI_CMD(msg=self.print_solver_messages))
        self.fractional_objective_value = ROUND(self.model.objective.value())
        self.fractional_solution = self._get_solution()

        self._save_data_to_cache()
        return self.fractional_objective_value


    def print_solution(self):
        ratio = (self.integral_objective_value / self.fractional_objective_value)
        integrality_gap = ROUND((1.0 - ratio) * 100)

        print('The offline solution:')
        print(f'Status: {self.status} - {pulp.LpStatus[self.status]}')
        print(f'Objective value = {self.fractional_objective_value}')
        print(f'Integrality gap = {integrality_gap} %')
        if self.verbose:
            for idx, items in enumerate(self.fractional_solution):
                print(f'Buyer [{idx}] purchased: {items}')
        print()
