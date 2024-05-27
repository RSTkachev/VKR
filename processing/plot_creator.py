import matplotlib.pyplot as plt
import seaborn as sns


def plot_chart(row, path='./resources/plot.jpg'):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax = sns.barplot(
        x=row.keys().to_list(),
        y=row,
        hue=row,
        palette=sns.color_palette(
            'bright',
            row.nunique()
        ),
        ec='k',
        legend=False,
        ax=ax
    )

    ax.set_xticks(ticks=ax.get_xticks(), labels=ax.get_xticklabels(), rotation=45, ha='right')
    plt.title('Количество обнаруженных животных')
    add_labels(row)
    plt.savefig(path, bbox_inches='tight')
    plt.close(fig)


def add_labels(row):
    for column in range(row.shape[0]):
        if row.iloc[column]:
            plt.text(column, row.iloc[column] / 2, row.iloc[column].astype(int), ha='center', rotation=90)