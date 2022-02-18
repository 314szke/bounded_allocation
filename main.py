import argparse
import os
import sys

from src.bounded_allocation import BoundedAllocationProblemSolver
from src.configuration import CONFIGS
from src.input_generation import InputGenerator
from src.lp_solver import LPSolverWrapper

DIR = os.path.dirname(os.path.abspath(__file__))

def parse_arguments():
    parser = argparse.ArgumentParser(description='Experiment with the bounded allocation problem.')
    parser.add_argument('prediction_error', type=float, help='Determines the error rate of the predictor. [0.0, 1.0]')
    parser.add_argument('number_of_experiments', type=int, help='The value of eta will range from 0/N to N/N.')
    parser.add_argument('config_id', type=int, help='The id of the configuration to use.')
    parser.add_argument('-v', '--verbose', type=int, default=0, help='Sets the execution\'s verbose level. [0, 1 or 2]')
    return parser.parse_args()


def validate_arguments(args):
    if args.prediction_error < 0.0 or args.prediction_error > 1.0:
        sys.exit(f'ERROR: The prediction error must be in the interval [0.0, 1.0]!')

    if args.number_of_experiments < 2:
        sys.exit(f'ERROR: The number of experiments should be at least 2!')

    try:
        _ = CONFIGS[args.config_id]
    except:
        sys.exit(f'ERROR: The configuration with id [{args.config_id}] does not exist!')

    if args.verbose < 0 or args.verbose > 2:
        sys.exit(f'ERROR: The verbose level must be [0, 1 or 2]!')


def save_result(gap_file, violation_file, gaps, violations):
    with open(gap_file, 'w+') as out_file:
        out_file.write('# eta\tgap\n')
        for eta, gap in gaps.items():
            out_file.write(f'{eta}\t\t{gap}\n')

    with open(violation_file, 'w+') as out_file:
        out_file.write('# eta\tviolation\n')
        for eta, violation in violations.items():
            out_file.write(f'{eta}\t\t{violation}\n')


if __name__ == '__main__':
    args = parse_arguments()
    validate_arguments(args)

    cache_file = os.path.abspath(f'{DIR}/cache/cache_{args.config_id}.json')
    gap_file = os.path.abspath(f'{DIR}/output/gap_{args.config_id}_{args.prediction_error}.dat')
    violation_file = os.path.abspath(f'{DIR}/output/violation_{args.config_id}_{args.prediction_error}.dat')

    input = InputGenerator(CONFIGS[args.config_id]).generate()
    if args.verbose:
        print(input)

    lp_solver = LPSolverWrapper(input, cache_file, verbose=args.verbose)
    offline_objective_value = lp_solver.solve()
    lp_solver.print_solution()

    solver = BoundedAllocationProblemSolver(input, verbose=args.verbose)

    gaps = {}
    violations = {}
    best_objective_value = -1
    best_eta = None

    for k in range(args.number_of_experiments + 1):
        eta = k / args.number_of_experiments
        objective_value = solver.solve(eta)

        gaps[eta] = solver.get_solution_gap(offline_objective_value)
        violations[eta] = solver.get_maximum_budget_violation()

        if objective_value > best_objective_value:
            best_objective_value = objective_value
            best_eta = eta

    solver.solve(best_eta)
    solver.print_solution(offline_objective_value)
    save_result(gap_file, violation_file, gaps, violations)
