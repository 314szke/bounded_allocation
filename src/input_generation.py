import random

from src.utils import ROUND
from src.input import Buyer, Item, ProblemInput

class InputGenerator:
    def __init__(self, configuration):
        self.config = configuration
        self.data = ProblemInput(configuration)


    def _get_budget(self):
        return random.randint(self.config.min_budget, self.config.max_budget)


    def _get_price(self):
        ratio = random.random()
        price = ROUND(self.config.max_price * ratio)
        price = max(price, self.config.min_price)
        return price


    def _get_buyer_ids(self):
        num_buyers = random.randint(self.config.min_buyers, self.config.max_buyers)
        return random.sample(self.data.buyer_ids, num_buyers)


    def generate(self):
        random.seed(self.config.random_seed)

        for idx in self.data.buyer_ids:
            self.data.buyers.append(Buyer(idx, self._get_budget()))

        for idx in range(self.config.num_items):
            buyer_ids = self._get_buyer_ids()
            price = self._get_price()
            self.data.items.append(Item(idx, price, buyer_ids))
            for buyer_id in buyer_ids:
                self.data.buyers[buyer_id].wanted_item_ids.append(idx)
                self.data.buyers[buyer_id].potential_expense = ROUND(self.data.buyers[buyer_id].potential_expense + price)

        return self.data
