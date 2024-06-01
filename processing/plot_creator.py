import matplotlib.pyplot as plt
from seaborn import barplot, color_palette


# Отрисовщик графов
class PlotCreator:

    # Добавление количества изображений с обнаруженным классом на граф
    # Входные параметры:
    # row - строка с данными
    def add_labels(self, row):
        for column in range(row.shape[0]):
            if row.iloc[column]:
                plt.text(column, row.iloc[column] / 2, row.iloc[column].astype(int), ha='center', rotation=90)

    # Создание графа
    # Входные параметры:
    # row - строка с данными
    # path - путь сохранения
    def plot_chart(self, row, path='./resources/plot.jpg'):
        # Создание графа
        fig, ax = plt.subplots(figsize=(8, 6))
        ax = barplot(
            x=row.keys().to_list(),
            y=row,
            hue=row,
            palette=color_palette(
                'bright',
                row.nunique()
            ),
            ec='k',
            legend=False,
            ax=ax
        )

        ax.set_xticks(ticks=ax.get_xticks(), labels=ax.get_xticklabels(), rotation=45, ha='right')
        plt.title('Количество обнаруженных животных')

        # Добавление количества изображений с обнаруженным классом на граф
        self.add_labels(row)
        # Сохранение графа
        plt.savefig(path, bbox_inches='tight')
        # Закрытие графа для экономии памяти
        plt.close(fig)
