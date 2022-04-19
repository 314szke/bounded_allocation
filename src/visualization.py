import matplotlib.pyplot as plt


def plot_result(gaps, best_etas):
    plt.rc('font', size=12)
    plt.rc('axes', titlesize=12)
    plt.rc('axes', labelsize=12)
    plt.rc('xtick', labelsize=12)
    plt.rc('ytick', labelsize=12)
    plt.rc('legend', fontsize=12)

    figure, axis = plt.subplots(1, 1, figsize=(14, 7))
    figure.suptitle('Experiment result', fontweight='bold')

    shift = 0.3
    for error, gap in gaps.items():
        axis.plot(gap.keys(), gap.values(), linewidth=3, linestyle=(0, (5, 8 + shift)), label=f'prediction error = {error}')
        axis.scatter(best_etas[error], gap[best_etas[error]], label=f'best eta for {error} error')
        shift += 0.3

    axis.set_xlabel('eta')
    axis.set_ylabel('ALGO(I) / OPT(I)')
    axis.legend(loc='upper right')

    figure.tight_layout()
    plt.show()
