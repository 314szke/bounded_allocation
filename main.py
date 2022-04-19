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
from src.verification import verify_solution
from src.visualization import plot_result

DIR = os.path.dirname(os.path.abspath(__file__))

def parse_arguments():
    parser = argparse.ArgumentParser(description='Experiment with the bounded allocation problem.')
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

    for file_name in cache_files:
        path = os.path.abspath(f'{DIR}/cache/{file_name}')
        os.remove(path)
    for file_name in output_files:
        path = os.path.abspath(f'{DIR}/output/{file_name}')
        os.remove(path)

    print('All files have been cleaned up!')


def save_result(gap_file, gaps, best_eta):
    with open(gap_file, 'w+') as out_file:
        out_file.write('# eta   \tgap\n')
        for eta, gap in gaps.items():
            out_file.write(f'{eta}   \t\t{gap}\n')
        out_file.write(f'# best eta = {best_eta}')


if __name__ == '__main__':
    args = parse_arguments()
    validate_arguments(args)

    if args.clean:
        clean_up()
        sys.exit(0)

    if args.manual:
        data = MANUAL_INPUTS[args.config_id]
        manual_str = 'm'
    else:
        data = InputGenerator(CONFIGS[args.config_id]).generate()
        manual_str = ''
    print(data)

    cache_file = os.path.abspath(f'{DIR}/cache/cache_{manual_str}_{args.config_id}.json')
    lp_solver = LPSolverWrapper(data, cache_file, verbose=args.verbose)
    offline_objective_value = lp_solver.solve()
    lp_solver.print_solution()

    gaps = defaultdict(lambda: {})
    best_etas = defaultdict(lambda: 0)

    for error in args.prediction_error:
        include_prediction(data.items, error, lp_solver.integral_solution, data.config.random_seed)
        solver = BoundedAllocationSolver(data, verbose=args.verbose)

        best_objective_value = -1
        for k in range(args.number_of_experiments + 1):
            eta = k / args.number_of_experiments
            objective_value = solver.solve(eta)
            gaps[error][eta] = solver.get_solution_gap(offline_objective_value)

            if objective_value > best_objective_value:
                best_objective_value = objective_value
                best_etas[error] = eta

        solver.solve(best_etas[error])
        solver.print_solution(error, offline_objective_value)
        verify_solution(solver.assignment, data)

        gap_file = os.path.abspath(f'{DIR}/output/gap_{manual_str}_{args.config_id}_{error}.dat')
        save_result(gap_file, gaps[error], best_etas[error])

    plot_result(gaps, best_etas)
