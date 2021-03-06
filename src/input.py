from src.utils import ROUND


class Buyer:
    def __init__(self, buyer_id, budget):
        self.id = buyer_id
        self.budget = budget

        self.spent = 0.0
        self.budget_fraction = 0.0

        self.wanted_item_ids = []
        self.potential_expense = 0


    def __repr__(self):
        return f'Buyer\t[{self.id}]:\tbudget = {self.budget},\t\tbudget_fraction = {self.budget_fraction},   \twanted_items = {self.wanted_item_ids}'


    def reset(self):
        self.spent = 0
        self.budget_fraction = 0.0


    def spend(self, amount):
        self.spent = ROUND(self.spent + amount)
        self.budget_fraction = ROUND(self.spent / self.budget)



class Item:
    def __init__(self, item_id, price, buyer_ids):
        self.id = item_id
        self.price = price
        self.interested_buyers = buyer_ids
        self.prediction = None


    def __repr__(self):
        return f'Item\t[{self.id}]:\tprice = {self.price},\t\tprediction = {self.prediction},   \t\tinterested_buyers = {self.interested_buyers}'



class ProblemInput:
    def __init__(self, configuration):
        self.config = configuration
        self.buyers = []
        self.buyer_ids = list(range(self.config.num_buyers))
        self.items = []
        self.item_ids = list(range(self.config.num_items))
        self.bound = self.config.max_buyers
        self.metrics = {}


    def _get_metric_string(self, display_name, value_list, all):
        name = display_name.split(':')[0]
        self.metrics[name] = {}
        self.metrics[name]['min'] = int(min(value_list))
        self.metrics[name]['max'] = int(max(value_list))
        sum_value = int(sum(value_list))
        self.metrics[name]['avg'] = int(ROUND(sum_value / all))
        return f"{display_name}\tmin = {self.metrics[name]['min']},\tmax = {self.metrics[name]['max']},\taverage = {self.metrics[name]['avg']}\n"


    def __str__(self):
        output = self.config.__str__()
        output += '\n\nObservations of the input:\n'

        budget_list = [x.budget for x in self.buyers]
        output += self._get_metric_string('Budget:\t', budget_list, self.config.num_buyers)

        price_list = [x.price for x in self.items]
        output += self._get_metric_string('Price:\t', price_list, self.config.num_items)

        buyers_list = [len(x.interested_buyers) for x in self.items]
        output += self._get_metric_string('NumBuyers:', buyers_list, self.config.num_items)

        items_list = [len(x.wanted_item_ids) for x in self.buyers]
        output += self._get_metric_string('NumItems:', items_list, self.config.num_buyers)

        expense_list = [x.potential_expense for x in self.buyers]
        output += self._get_metric_string('Expenses:', expense_list, self.config.num_buyers)

        overflow = sum([x.potential_expense > x.budget for x in self.buyers])
        percentage = ROUND((overflow / self.config.num_buyers) * 100)
        output += f'{int(percentage)} % number of buyers want to spend more, than their budget.\n'
        return output
