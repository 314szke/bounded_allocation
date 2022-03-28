import sys

def verify_solution(solution, num_items):
    valid = True
    item_fractions = [0 for _ in range(num_items)]

    for buyer_id, assigned_items in enumerate(solution):
        for item_id, fraction in assigned_items.items():
            if fraction < 0.0 or fraction > 1.0:
                print(f'ERROR: Assigned fraction of {fraction} for buyer {buyer_id} of item {item_id}!')
                valid = False
            item_fractions[item_id] += fraction

    for item_id, fraction in enumerate(item_fractions):
        if round(fraction, 2) > 1.0:
            print(f'ERROR: Item {item_id} was sold in {fraction} fraction!')
            valid = False

    if not valid:
        sys.exit('Verification failed!')

    print('Solution verified!\n')
