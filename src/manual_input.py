from src.configuration import ProblemConfiguration
from src.input import Buyer, Item, Input


def Input_1():
    config = ProblemConfiguration(5, 6, 100, 100, 1, 5, 40, 100, 1111)
    new_input = Input(config)

    new_input.buyers.append(Buyer(0, 100))
    new_input.buyers[0].wanted_item_ids = [0]
    new_input.buyers[0].potential_expense = 100

    new_input.buyers.append(Buyer(1, 100))
    new_input.buyers[1].wanted_item_ids = [0, 1, 2]
    new_input.buyers[1].potential_expense = 200

    new_input.buyers.append(Buyer(2, 100))
    new_input.buyers[2].wanted_item_ids = [0, 1, 2, 3]
    new_input.buyers[2].potential_expense = 300

    new_input.buyers.append(Buyer(3, 100))
    new_input.buyers[3].wanted_item_ids = [0, 1, 2, 3, 4]
    new_input.buyers[3].potential_expense = 400

    new_input.buyers.append(Buyer(4, 100))
    new_input.buyers[4].wanted_item_ids = [0, 1, 3, 4, 5]
    new_input.buyers[4].potential_expense = 460

    new_input.items.append(Item(0, 100, [0, 1, 2, 3, 4]))
    new_input.items.append(Item(1, 60, [1, 2, 3, 4]))
    new_input.items.append(Item(2, 40, [1, 2, 3]))
    new_input.items.append(Item(3, 100, [2, 3, 4]))
    new_input.items.append(Item(4, 100, [3, 4]))
    new_input.items.append(Item(5, 100, [4]))
    return new_input


MANUAL_INPUTS = {
    1: Input_1()
}
