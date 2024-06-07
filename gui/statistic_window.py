from os import remove
from os.path import exists

import pandas as pd
from PySide6.QtGui import QPixmap

from gui.statistic_window_ui import StatisticWindowUi
from processing.plot_creator import PlotCreator


class StatisticWidget(StatisticWindowUi):
    """Страница статистики"""

    # Переменные для хранения данных для реализации графов
    __statistic_file = None
    __cnt_detections = 0
    __current_detection = 0

    def __init__(self) -> None:
        """Инициализация объекта"""

        super().__init__()

        self._refresh_button.clicked.connect(self.__refresh_detections)
        self._button_previous.clicked.connect(self.__load_previous_chart)
        self._button_next.clicked.connect(self.__load_next_chart)
        self._button_clear.clicked.connect(self.__clear_statistic)

        # Попытка открытия файла со статистикой
        if exists("./resources/statistic.csv"):
            self.__statistic_file = pd.read_csv("./resources/statistic.csv")
            # Количество выполненных детекций
            self.__cnt_detections = self.__statistic_file.shape[0]

        # Если файл со статистикой существует и непустой
        if self.__cnt_detections > 0:
            # Обновление графического интерфейса
            self._chart_text.setVisible(False)
            self._chart.setVisible(True)
            self._button_clear.setVisible(True)
            # Установка графа
            self.__set_plot()
            # Обновление графического интерфейса
            if self.__cnt_detections > 1:
                self._button_next.setVisible(True)

    def __load_previous_chart(self) -> None:
        """Переход к предыдущему графу"""

        # Уменьшение номера детекции
        self.__current_detection -= 1
        # Обновление графического интерфейса
        if self.__current_detection == 0:
            self._button_previous.setVisible(False)
        if self.__current_detection < self.__cnt_detections - 1:
            self._button_next.setVisible(True)
        # Установка графа
        self.__set_plot()

    def __load_next_chart(self) -> None:
        """Переход к следующему графу"""

        # Увеличение номера детекции
        self.__current_detection += 1
        # Обновление графического интерфейса
        if self.__current_detection == self.__cnt_detections - 1:
            self._button_next.setVisible(False)
        if self.__current_detection > 0:
            self._button_previous.setVisible(True)
        # Установка графа
        self.__set_plot()

    def __refresh_detections(self) -> None:
        """Обновление статистики из файла"""

        # Попытка чтения файла
        if exists("./resources/statistic.csv"):
            self.__statistic_file = pd.read_csv("./resources/statistic.csv")
            # Новое количество выполненных детекций
            self.__cnt_detections = self.__statistic_file.shape[0]

            # Обновление графического интерфейса
            if self.__current_detection < self.__cnt_detections - 1:
                self._button_next.setVisible(True)

            # Если имеются данные статистики
            if self.__cnt_detections:
                self._chart_text.setVisible(False)
                self._chart.setVisible(True)
                self._button_clear.setVisible(True)
                # Установка графа
                self.__set_plot()

    def __clear_statistic(self) -> None:
        """Удаление файла статистики"""

        # Удаление файла
        if exists("./resources/statistic.csv"):
            remove("./resources/statistic.csv")
        # Обновление графического интерфейса
        self._button_previous.setVisible(False)
        self._button_next.setVisible(False)
        self._chart.setVisible(False)
        self._chart_text.setVisible(True)
        self._button_clear.setVisible(False)
        # Обнуление данных по детекциям
        self.__current_detection = 0
        self.__cnt_detections = 0

    def __set_plot(self) -> None:
        """Установка графа"""

        # Строка для построения графа
        row = self.__statistic_file.iloc[self.__current_detection]
        # Построение графа
        PlotCreator.plot_chart(row)
        # Установка графа
        self._chart.setPixmap(QPixmap("./resources/plot.jpg"))
