import sys

def verify_solution(solution, num_items):
    valid = True
    items = set()
    item_fractions = [0 for _ in range(num_items)]

    for buyer_id, assigned_items in enumerate(solution):
        for item_id, fraction in assigned_items.items():
            if fraction < 0.0 or fraction > 1.0:
                print(f'ERROR: Assigned fraction of {fraction} for buyer {buyer_id} of item {item_id}!')
                valid = False

            items.add(item_id)
            item_fractions[item_id] += fraction

    if len(items) != num_items:
        print(f'ERROR: The items listed in the solution do not match the input! Items: {items}')
        valid = False

    for item_id, fraction in enumerate(item_fractions):
        if round(fraction, 1) > 1.0:
            print(f'ERROR: Item {item_id} was sold in {fraction} fraction!')
            valid = False

    if not valid:
        sys.exit(f'Verification failed!')

    print('Solution verified!\n')
