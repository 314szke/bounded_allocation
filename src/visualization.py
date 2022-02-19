import matplotlib.pyplot as plt

def plot_results(gaps, violations):
    figure, axis = plt.subplots(1, 2, figsize=(14, 7))
    figure.suptitle(f'Experiment result', fontweight='bold')

    for error, gap in gaps.items():
        axis[0].plot(gap.keys(), gap.values(), label=f'error = {error}')
    axis[0].set_title('Gap values in %')
    axis[0].set_xlabel('eta')
    axis[0].set_yticks(list(range(0, 101, 20)))
    axis[0].legend(loc='upper right')

    for error, violation in violations.items():
        axis[1].plot(violation.keys(), violation.values(), label=f'error = {error}')
    axis[1].set_title('Violations in %')
    axis[1].set_xlabel('eta')
    axis[1].set_yticks(list(range(0, 101, 20)))
    axis[1].legend(loc='upper right')

    figure.tight_layout()
    figure.subplots_adjust(top=0.85)
    plt.show()
