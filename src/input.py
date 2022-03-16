from src.utils import ROUND


class Buyer:
    def __init__(self, id, budget):
        self.id = id
        self.budget = budget

        self.spent = 0.0
        self.budget_fraction = 0.0

        self.wanted_item_ids = []
        self.potential_expense = 0


    def __str__(self):
        return f'Buyer\t[{self.id}]:\tbudget = {self.budget},\t\tbudget_fraction = {self.budget_fraction},   \twanted_items = {self.wanted_item_ids}'


    def __repr__(self):
        return self.__str__()


    def reset(self):
        self.spent = 0
        self.budget_fraction = 0.0


    def spend(self, amount):
        self.spent = ROUND(self.spent + amount)
        self.budget_fraction = ROUND(self.spent / self.budget)



class Item:
    def __init__(self, id, price, buyer_ids):
        self.id = id
        self.price = price
        self.interested_buyers = buyer_ids
        self.prediction = None


    def __str__(self):
        return f'Item\t[{self.id}]:\tprice = {self.price},\t\tprediction = {self.prediction},   \t\tinterested_buyers = {self.interested_buyers}'


    def __repr__(self):
        return self.__str__()



class Input:
    def __init__(self, configuration):
        self.config = configuration
        self.buyers = []
        self.buyer_ids = list(range(self.config.num_buyers))
        self.items = []
        self.item_ids = list(range(self.config.num_items))
        self.bound = self.config.max_buyers


    def _get_metric_string(self, name, value_list, all):
        min_value = min(value_list)
        max_value = max(value_list)
        sum_value = sum(value_list)
        avg_value = ROUND(sum_value / all)
        return f'{name}\tmin = {min_value},\tmax = {max_value},\taverage = {avg_value}\n'


    def __str__(self):
        output = self.config.__str__()
        output += '\n\nObservations after generation:\n'

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
        output += f'{percentage} % number of buyers want to spend more, than their budget.\n'
        return output
