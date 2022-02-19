import matplotlib.pyplot as plt

def plot_result(gaps, best_etas):
    figure, axis = plt.subplots(1, 1, figsize=(14, 7))
    figure.suptitle(f'Experiment result', fontweight='bold')

    for error, gap in gaps.items():
        axis.plot(gap.keys(), gap.values(), label=f'prediction error = {error}')
        axis.scatter(best_etas[error], gap[best_etas[error]], label=f'best eta for {error} error')
    axis.set_xlabel('eta')
    axis.set_ylabel('Gap values in %')
    axis.legend(loc='upper right')

    figure.tight_layout()
    plt.show()
