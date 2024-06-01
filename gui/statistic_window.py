from os import remove
from os.path import exists

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout

from processing.plot_creator import plot_chart


class StatisticWidget(QWidget):
    """Страница статистики"""

    # Переменные для хранения данных для реализации графов
    statistic_file = None
    cnt_detections = 0
    current_detection = 0

    def __init__(self) -> None:
        """Инициализация объекта"""

        super().__init__()

        # Создание интерфеса
        self.refresh_button = QPushButton(
            icon=QIcon("./resources/icons/refresh-cw.svg"),
            text=" Обновить",
        )
        self.refresh_button.setObjectName("btn_refresh")
        self.refresh_button.clicked.connect(self.refresh_detections)

        self.button_previous = QPushButton()
        self.button_previous.setText("")
        self.button_previous.setIcon(QIcon("./resources/icons/chevron-left.svg"))
        self.button_previous.setToolTip("Перейти к статистике предыдущей детекции")
        self.button_previous.setObjectName("btn_previous")
        self.button_previous.setVisible(False)
        self.button_previous.clicked.connect(self.load_previous_chart)

        self.button_next = QPushButton()
        self.button_next.setText("")
        self.button_next.setIcon(QIcon("./resources/icons/chevron-right.svg"))
        self.button_next.setToolTip("Перейти к статистике следующей детекции")
        self.button_next.setObjectName("btn_next")
        self.button_next.setVisible(False)
        self.button_next.clicked.connect(self.load_next_chart)

        self.button_clear = QPushButton()
        self.button_clear.setText("Сбросить статистику")
        self.button_clear.setIcon(QIcon("./resources/icons/trash.svg"))
        self.button_clear.setObjectName("btn_clear")
        self.button_clear.setVisible(False)
        self.button_clear.clicked.connect(self.clear_statistic)

        self.chart_text = QLabel()
        self.chart_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_text.setText("Данные для отображения отсутствуют")
        self.chart_text.setObjectName("chart_str")

        self.chart = QLabel()
        self.chart.setObjectName("chart")
        self.chart.setVisible(False)

        layout = QGridLayout()
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(10)

        layout.addWidget(
            self.refresh_button, 0, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            self.button_clear, 0, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            self.button_previous,
            1,
            0,
            1,
            1,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )

        layout.addWidget(
            self.chart_text, 1, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(self.chart, 1, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(
            self.button_next,
            1,
            2,
            1,
            1,
            alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 9)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 1)

        self.setLayout(layout)

        # Попытка открытия файла со статистикой
        if exists("./resources/statistic.csv"):
            self.statistic_file = pd.read_csv("./resources/statistic.csv")
            # Количество выполненных детекций
            self.cnt_detections = self.statistic_file.shape[0]

        # Если файл со статистикой существует и непустой
        if self.cnt_detections > 0:
            # Обновление графического интерфейса
            self.chart_text.setVisible(False)
            self.chart.setVisible(True)
            self.button_clear.setVisible(True)
            # Установка графа
            self.set_plot()
            # Обновление графического интерфейса
            if self.cnt_detections > 1:
                self.button_next.setVisible(True)

    def load_previous_chart(self) -> None:
        """Переход к предыдущему графу"""

        # Уменьшение номера детекции
        self.current_detection -= 1
        # Обновление графического интерфейса
        if self.current_detection == 0:
            self.button_previous.setVisible(False)
        if self.current_detection < self.cnt_detections - 1:
            self.button_next.setVisible(True)
        # Установка графа
        self.set_plot()

    def load_next_chart(self) -> None:
        """Переход к следующему графу"""

        # Увеличение номера детекции
        self.current_detection += 1
        # Обновление графического интерфейса
        if self.current_detection == self.cnt_detections - 1:
            self.button_next.setVisible(False)
        if self.current_detection > 0:
            self.button_previous.setVisible(True)
        # Установка графа
        self.set_plot()

    def refresh_detections(self) -> None:
        """Обновление статистики из файла"""

        # Попытка чтения файла
        if exists("./resources/statistic.csv"):
            self.statistic_file = pd.read_csv("./resources/statistic.csv")
            # Новое количество выполненных детекций
            self.cnt_detections = self.statistic_file.shape[0]

            # Обновление графического интерфейса
            if self.current_detection < self.cnt_detections - 1:
                self.button_next.setVisible(True)

            # Если имеются данные статистики
            if self.cnt_detections:
                self.chart_text.setVisible(False)
                self.chart.setVisible(True)
                self.button_clear.setVisible(True)
                # Установка графа
                self.set_plot()

    def clear_statistic(self) -> None:
        """Удаление файла статистики"""

        # Удаление файла
        if exists("./resources/statistic.csv"):
            remove("./resources/statistic.csv")
        # Обновление графического интерфейса
        self.button_previous.setVisible(False)
        self.button_next.setVisible(False)
        self.chart.setVisible(False)
        self.chart_text.setVisible(True)
        self.button_clear.setVisible(False)
        # Обнуление данных по детекциям
        self.current_detection = 0
        self.cnt_detections = 0

    def set_plot(self) -> None:
        """Установка графа"""

        # Строка для построения графа
        row = self.statistic_file.iloc[self.current_detection]
        # Построение графа
        plot_chart(row)
        # Установка графа
        self.chart.setPixmap(QPixmap("./resources/plot.jpg"))
