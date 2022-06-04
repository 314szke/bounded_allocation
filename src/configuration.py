from dataclasses import dataclass

@dataclass
class ProblemConfiguration:
    num_buyers: int
    num_items: int

    min_budget: int
    max_budget: int

    min_buyers: int
    max_buyers: int

    min_price: int
    max_price: int

    random_seed: int


    def __str__(self):
        output = 'Configuration:\n'
        output +=  f'Buyers:\t\t{self.num_buyers}\nItems:\t\t{self.num_items}\n'
        output += f'Budget:\t\t[{self.min_budget}, {self.max_budget}]\n'
        output += f'ItemBuyers:\t[{self.min_buyers}, {self.max_buyers}]\nItemPrice:\t[{self.min_price}, {self.max_price}]'
        return output



CONFIGS = {
    0: ProblemConfiguration(10, 10, 10, 100, 1, 3, 0.1, 10, 42),
    1: ProblemConfiguration(100, 100, 10, 100, 1, 10, 0.1, 10, 1976),
    2: ProblemConfiguration(100, 1000, 10, 100, 2, 5, 0.1, 8, 22),
    3: ProblemConfiguration(100, 10_000, 10, 1000, 2, 3, 1, 10, 2022),
    4: ProblemConfiguration(4, 8, 10, 100, 1, 4, 10, 100, 1984),
    5: ProblemConfiguration(4, 8, 10, 100, 1, 3, 10, 50, 1984),
    6: ProblemConfiguration(10, 100, 100, 100, 2, 10, 10, 10, 101),
    7: ProblemConfiguration(80, 80, 10, 100, 1, 40, 10, 100, 1984)
}
