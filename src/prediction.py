import random

def include_prediction(items, error_rate, optimal_solution, seed):
    random.seed(seed)

    for item_id in range(len(items)):
        items[item_id].prediction = None

    for buyer_id, assigned_items in enumerate(optimal_solution):
        for item_id, fraction in assigned_items.items():
            if fraction == 1.0:
                # Impose error in the prediction, but keep it feasible
                if random.random() < error_rate:
                    if len(items[item_id].interested_buyers) == 1:
                        items[item_id].prediction = buyer_id
                    else:
                        remaining_buyers = set(items[item_id].interested_buyers).difference(set([buyer_id]))
                        items[item_id].prediction = random.sample(remaining_buyers, 1)[0]
                else: # The prediction is the optimal solution
                    items[item_id].prediction = buyer_id
