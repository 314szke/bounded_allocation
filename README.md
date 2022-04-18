# Experiment with the bounded allocation problem

Experiment with an algorithm that integrates prediction information to the solving of the online fractional bounded allocation problem.

## Credits

The algorithm integrates an online algorithm from Section 13 of the survey *The Design of Competitive Online Algorithms via a Primal–Dual Approach* by Niv Buchbinder and Joseph Naor. ([survey available here](https://www.tau.ac.il/~nivb/download/pd-survey.pdf))

The code was inspired by the work of Christoph Durr and Nguyen Kim Thang. ([code available here](https://webia.lip6.fr/~durrc//packing/))

## Minimum requirements

    python 3.9.1
    matplotlib 3.4.3
    PuLP 2.5.1

    Gurobi 9.5.0

## Usage

    python3 main.py
        -e <list of prediction error rates>
        -n <number of experiments>
        -i <configuration id>
        -m <flag to use manual configuration id>


For more details on the parameters, use:

    python3 main.py --help
