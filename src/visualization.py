import matplotlib.pyplot as plt


def plot_result(gaps, best_etas):
    figure, axis = plt.subplots(1, 1, figsize=(14, 7))
    figure.suptitle('Experiment result', fontweight='bold')

    shift = 0.3
    for error, gap in gaps.items():
        axis.plot(gap.keys(), gap.values(), linewidth=2, linestyle=(0, (5, 8 + shift)), label=f'prediction error = {error}')
        axis.scatter(best_etas[error], gap[best_etas[error]], label=f'best eta for {error} error')
        shift += 0.3

    axis.set_xlabel('eta')
    axis.set_ylabel('Gap values in %')
    axis.legend(loc='lower right')

    figure.tight_layout()
    plt.show()
