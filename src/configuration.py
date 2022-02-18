class ProblemConfiguration:
    def __init__(self, buyers, items, min_budget, max_budget, min_buyers, max_buyers, min_price, max_price, seed):
        self.num_buyers = buyers
        self.num_items = items

        self.min_budget = min_budget
        self.max_budget = max_budget

        self.min_buyers = min_buyers
        self.max_buyers = max_buyers

        self.min_price = min_price
        self.max_price = max_price

        self.random_seed = seed

    def __str__(self):
        output = 'Configuration:\n'
        output +=  f'Buyers:\t\t{self.num_buyers}\nItems:\t\t{self.num_items}\n'
        output += f'Budget:\t\t[{self.min_budget}, {self.max_budget}]\n'
        output += f'ItemBuyers:\t[{self.min_buyers}, {self.max_buyers}]\nItemPrice:\t[{self.min_price}, {self.max_price}]'
        return output



CONFIGS = {
    0: ProblemConfiguration(10, 10, 10, 100, 1, 3, 0.1, 10, 42),
    1: ProblemConfiguration(100, 100, 10, 100, 1, 10, 0.1, 10, 1976)
}
