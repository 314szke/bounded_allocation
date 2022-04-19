import sys

def verify_solution(solution, data):
    valid = True
    budget_spent = [0 for _ in data.buyer_ids]
    item_fractions = [0 for _ in data.item_ids]

    for buyer_id, assigned_items in enumerate(solution):
        for item_id, fraction in assigned_items.items():
            if fraction < 0.0 or fraction > 1.0:
                print(f'ERROR: Assigned fraction of {fraction} for buyer {buyer_id} of item {item_id}!')
                valid = False
            budget_spent[buyer_id] += fraction * data.items[item_id].price
            item_fractions[item_id] += fraction

    for buyer_id, spent in enumerate(budget_spent):
        if round(spent, 2) > data.buyers[buyer_id].budget:
            print(f'ERROR: Buyer {buyer_id} spent {spent} while its budget is {data.buyers[buyer_id].budget}!')
            valid = False

    for item_id, fraction in enumerate(item_fractions):
        if round(fraction, 2) > 1.0:
            print(f'ERROR: Item {item_id} was sold in {fraction} fraction!')
            valid = False

    if not valid:
        sys.exit('Verification failed!')

    print('Solution verified!\n')
