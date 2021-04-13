import matplotlib.pyplot as plt
import seaborn as sns


def bar_graph(dictionary, limit, label, title, filename):
    x = []
    y = []
    for count, (key, value) in enumerate(dictionary.items()):
        if count == limit:
            break
        x.append(key)
        y.append(value)
    make_bar_graph(x, y, label, title, filename)


def make_bar_graph(x, y, label, title, save_as):
    sns.set_style('darkgrid')
    sns.color_palette('Set2')
    plt.figure(figsize=(10, 6), dpi=160)
    ax = sns.barplot(y, x)
    ax.set_xlabel(label)
    ax.set_title(title)
    plt.tight_layout()
    plt.savefig(save_as)


def histogram(dictionary, title, save_as):
    sns.set_style('darkgrid')
    sns.color_palette('Set2')
    plt.figure(figsize=(10, 6), dpi=160)
    sns.barplot(
        x=[int(x) for x in dictionary.keys()],
        y=list(dictionary.values())
    )
    plt.xlabel('Time')
    plt.ylabel('Messages')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(save_as)
