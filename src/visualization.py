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

    line_shift = 0.3
    point_shift = 0.01
    for error, gap in gaps.items():
        axis.plot(gap.keys(), gap.values(), linewidth=3, linestyle=(0, (5, 8 + line_shift)), label=f'prediction error = {error}')
        axis.scatter(best_etas[error], point_shift, label=f'best eta for {error} error')
        line_shift += 0.3
        point_shift += 0.01

    axis.set_xlabel('eta')
    axis.set_ylabel('ALGO(I) / OPT(I)')
    axis.legend(loc='lower right')

    figure.tight_layout()
    plt.show()
