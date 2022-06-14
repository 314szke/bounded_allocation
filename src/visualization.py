import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_result(result_file):
    plt.rc('font', size=16)
    plt.rc('axes', titlesize=16)
    plt.rc('axes', labelsize=16)
    plt.rc('xtick', labelsize=16)
    plt.rc('ytick', labelsize=16)
    plt.rc('legend', fontsize=16)

    data = pd.read_csv(result_file, sep=';',index_col=0)

    figure, axis = plt.subplots(1, 1, figsize=(7, 7))

    sns.lineplot(data=data, x='Eta', y='Gap', hue='PredictionError', linewidth=2,
                palette='colorblind', style='PredictionError', markers=True, legend='full')

    axis.set_xlabel(r'$\eta$')
    axis.set_ylabel('ALGO(I) / OPT(I)')
    axis.legend(loc='lower right')

    figure.tight_layout()
    plt.show()


def plot_metrics(metric_file):
    plt.rc('font', size=16)
    plt.rc('axes', titlesize=16)
    plt.rc('axes', labelsize=16)
    plt.rc('xtick', labelsize=16)
    plt.rc('ytick', labelsize=16)
    plt.rc('legend', fontsize=16)

    data = pd.read_csv(metric_file, sep=';')

    figure, axis = plt.subplots(1, 1, figsize=(7, 7))

    sns.regplot(data=data, x='ID', y='IntegralityGap')

    axis.set_xlabel('Random Iteration ID')
    axis.set_ylabel('Integrality Gap')
    axis.legend(loc='lower right')

    figure.tight_layout()
    plt.show()
