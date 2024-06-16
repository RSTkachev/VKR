from os import remove
from os.path import exists

import matplotlib.pyplot as plt
import pandas as pd
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QPixmap
from seaborn import barplot, color_palette


class PlotCreator(QObject):
    """Класс для построения графиков"""

    # Файл статистики
    __statistic = None
    __current_row = 0
    __total_row = 0

    no_graph = Signal()
    graph_existed = Signal()
    previous = Signal(bool)
    next = Signal(bool)
    plot = Signal(QPixmap)
    clear_error = Signal()

    @Slot()
    def load_statistic(self) -> bool:
        """Загрузка статистики и установка графа"""

        if exists("./resources/statistic.csv"):
            self.__statistic = pd.read_csv("./resources/statistic.csv")
            # Количество выполненных детекций
            self.__total_row = self.__statistic.shape[0]

        else:
            self.__current_row = 0
            self.__total_row = 0

        if self.__total_row:
            self.__plot_chart()
            self.graph_existed.emit()
            self.__check_previous()
            self.__check_next()
            return True

        else:
            self.no_graph.emit()
            return False

    @Slot()
    def clear_statistic(self) -> None:
        """Удаление статистики"""

        if exists("./resources/statistic.csv"):
            try:
                remove("./resources/statistic.csv")
            except PermissionError:
                self.clear_error.emit()
                return

        self.__current_row = 0
        self.__total_row = 0
        self.no_graph.emit()

    @Slot()
    def previous_chart(self) -> None:
        """Переход к предыдущему графу"""

        self.__current_row -= 1
        self.__check_previous()
        self.__check_next()
        self.__plot_chart()

    @Slot()
    def next_chart(self) -> None:
        """Переход к следующему графу"""

        self.__current_row += 1
        self.__check_previous()
        self.__check_next()
        self.__plot_chart()

    def __check_previous(self) -> None:
        """Проверка наличия предыдущего графа и изменение кнопки перехода к предыдущму графу"""

        if self.__current_row > 0:
            self.previous.emit(True)
        else:
            self.previous.emit(False)

    def __check_next(self) -> None:
        """Проверка наличия следующего графа и изменение кнопки перехода к следующему графу"""

        if self.__total_row > self.__current_row + 1:
            self.next.emit(True)
        else:
            self.next.emit(False)

    def __add_labels(self) -> None:
        """Добавление количества изображений с обнаруженным классом на граф"""

        row = self.__statistic.iloc[self.__current_row]

        for column in range(row.shape[0]):
            if row.iloc[column]:
                plt.text(
                    column,
                    row.iloc[column] / 2,
                    row.iloc[column].astype(int),
                    ha="center",
                    rotation=90,
                )

    def __plot_chart(self) -> None:
        """Создание графа"""

        row = self.__statistic.iloc[self.__current_row]

        # Создание графа
        fig, ax = plt.subplots(figsize=(8, 6))
        ax = barplot(
            x=row.keys().to_list(),
            y=row,
            hue=row,
            palette=color_palette("bright", row.nunique()),
            ec="k",
            legend=False,
            ax=ax,
        )

        ax.set_xticks(
            ticks=ax.get_xticks(), labels=ax.get_xticklabels(), rotation=45, ha="right"
        )
        plt.title("Количество обнаруженных животных")

        # Добавление количества изображений с обнаруженным классом на граф
        self.__add_labels()
        # Сохранение графа
        plt.savefig("./resources/plot.jpg", bbox_inches="tight")
        # Закрытие графа для экономии памяти
        plt.close(fig)
        self.plot.emit(QPixmap("./resources/plot.jpg"))
