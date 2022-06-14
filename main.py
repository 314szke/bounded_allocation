import argparse
import os
import sys

from collections import defaultdict

from src.bounded_allocation_solver import BoundedAllocationSolver
from src.configuration import CONFIGS
from src.input_generation import InputGenerator
from src.lp_solver import LPSolverWrapper
from src.manual_input import MANUAL_INPUTS
from src.prediction import include_prediction
from src.utils import ROUND
from src.verification import verify_solution
from src.visualization import plot_result, plot_metrics

DIR = os.path.dirname(os.path.abspath(__file__))

def parse_arguments():
    parser = argparse.ArgumentParser(description='Experiment with the bounded allocation problem.')
    parser.add_argument('-r', '--random_iterations', type=int, default=1, help='Number of random inputs to average over.')
    parser.add_argument('-e', '--prediction_error', type=float, nargs='+', default=[0.0, 0.01, 0.1], help='A list of the error rates of the predictor. Range: [0.0, 1.0]')
    parser.add_argument('-n', '--number_of_experiments', type=int, default=10, help='The value of eta will range from 0/n to n/n.')
    parser.add_argument('-i', '--config_id', type=int, default=1, help='The id of the configuration to use.')
    parser.add_argument('-m', '--manual', action='store_true', help='If set, config id points to a manual input.')
    parser.add_argument('-v', '--verbose', type=int, default=0, help='Sets the execution\'s verbose level. [0, 1 or 2]')
    parser.add_argument('-c', '--clean', action='store_true', help='Deletes the cache and output files.')
    return parser.parse_args()


def validate_arguments(args):
    for error in args.prediction_error:
        if error < 0.0 or error > 1.0:
            sys.exit('ERROR: The prediction error must be in the interval [0.0, 1.0]!')

    if args.random_iterations < 1:
        sys.exit('ERROR: The number of random iterations should be at least 1!')

    if args.number_of_experiments < 2:
        sys.exit('ERROR: The number of experiments should be at least 2!')

    if not args.manual:
        try:
            _ = CONFIGS[args.config_id]
        except KeyError:
            sys.exit(f'ERROR: The configuration with id [{args.config_id}] does not exist!')

    if args.manual:
        try:
            _ = MANUAL_INPUTS[args.config_id]
        except KeyError:
            sys.exit(f'ERROR: The manual input with id [{args.manual}] does not exist!')

    if args.verbose < 0 or args.verbose > 2:
        sys.exit('ERROR: The verbose level must be [0, 1 or 2]!')


def clean_up():
    cache_files = os.listdir(f'{DIR}/cache')
    cache_files.remove('.placeholder')
    output_files = os.listdir(f'{DIR}/output')
    output_files.remove('.placeholder')
    metric_files = os.listdir(f'{DIR}/metrics')
    metric_files.remove('.placeholder')

    for file_name in cache_files:
        path = os.path.abspath(f'{DIR}/cache/{file_name}')
        os.remove(path)
    for file_name in output_files:
        path = os.path.abspath(f'{DIR}/output/{file_name}')
        os.remove(path)
    for file_name in metric_files:
        path = os.path.abspath(f'{DIR}/metrics/{file_name}')
        os.remove(path)

    print('All files have been cleaned up!')


def save_result(result_file, gaps, eta_values):
    with open(result_file, 'w+') as out_file:
        out_file.write('ID;RandomIteration;PredictionError;Eta;Gap\n')
        instance_id = 0
        for idx in range(len(gaps)):
            for key1 in gaps[idx].keys():
                for key2 in gaps[idx][key1].keys():
                    out_file.write(f"{instance_id};{idx};{key1};{key2};{gaps[idx][key1][key2]}\n")
                    instance_id += 1


def save_metrics(metric_file, metrics, integrality_gaps):
    with open(metric_file, 'w+') as out_file:
        out_file.write('ID;IntegralityGap;BudgetMin;BudgetMax;BudgetAvg;')
        out_file.write('PriceMin;PriceMax;PriceAvg;NumBuyersMin;NumBuyersMax;NumBuyersAvg;')
        out_file.write('NumItemsMin;NumItemsMax;NumItemsAvg;ExpensesMin;ExpensesMax;ExpensesAvg\n')
        for idx in range(len(integrality_gaps)):
            out_file.write(f'{idx};{integrality_gaps[idx]};')
            out_file.write(f"{metrics[idx]['Budget']['min']};{metrics[idx]['Budget']['max']};{metrics[idx]['Budget']['avg']};")
            out_file.write(f"{metrics[idx]['Price']['min']};{metrics[idx]['Price']['max']};{metrics[idx]['Price']['avg']};")
            out_file.write(f"{metrics[idx]['NumBuyers']['min']};{metrics[idx]['NumBuyers']['max']};{metrics[idx]['NumBuyers']['avg']};")
            out_file.write(f"{metrics[idx]['NumItems']['min']};{metrics[idx]['NumItems']['max']};{metrics[idx]['NumItems']['avg']};")
            out_file.write(f"{metrics[idx]['Expenses']['min']};{metrics[idx]['Expenses']['max']};{metrics[idx]['Expenses']['avg']}\n")



if __name__ == '__main__':
    # Execution setup
    args = parse_arguments()
    validate_arguments(args)

    if args.clean:
        clean_up()
        sys.exit(0)

    if args.manual:
        manual_str = 'm'
        random_iterations = 1
    else:
        random_iterations = args.random_iterations
        manual_str = ''

    # Result data structures
    metrics = []
    integrality_gaps = [0 for _ in range(random_iterations)]
    gaps = [defaultdict(lambda: {}) for _ in range(random_iterations)]
    eta_values = [k / args.number_of_experiments for k in range(args.number_of_experiments + 1)]

    # Files
    result_file = os.path.abspath(f'{DIR}/output/result_{manual_str}_{args.config_id}.csv')
    metric_file = os.path.abspath(f'{DIR}/metrics/instance_{manual_str}_{args.config_id}.csv')


    # Execute several random iterations and average over the result
    if not os.path.exists(result_file):
        for random_idx in range(random_iterations):
            # Instance setup
            if args.manual:
                data = MANUAL_INPUTS[args.config_id]
            else:
                configuration = CONFIGS[args.config_id]
                configuration.random_seed += random_idx
                data = InputGenerator(configuration).generate()
            print(data)
            metrics.append(data.metrics)

            # LP solving
            cache_file = os.path.abspath(f'{DIR}/cache/cache_{manual_str}_{args.config_id}_{random_idx}.json')
            lp_solver = LPSolverWrapper(data, cache_file, verbose=args.verbose)
            offline_objective_value = lp_solver.solve()
            lp_solver.print_solution()
            integrality_gaps[random_idx] = lp_solver.get_integrality_gap()

            # Iterate over several error rates in the prediction
            for error in args.prediction_error:
                include_prediction(data.items, error, lp_solver.integral_solution, data.config.random_seed)
                solver = BoundedAllocationSolver(data, verbose=args.verbose)

                # Run the solver on several eta values
                best_objective_value = -1
                best_eta = -1
                for eta in eta_values:
                    objective_value = solver.solve(eta)
                    gaps[random_idx][error][eta] = solver.get_solution_robustness(offline_objective_value)

                    if objective_value > best_objective_value:
                        best_objective_value = objective_value
                        best_eta = eta

                # Verify solution on the best eta value
                solver.solve(best_eta)
                solver.print_solution(error, offline_objective_value)
                verify_solution(solver.assignment, data)

        # Save result
        save_result(result_file, gaps, eta_values)
        # Save metrics
        save_metrics(metric_file, metrics, integrality_gaps)


    # Display result
    plot_result(result_file)
    plot_metrics(metric_file)
