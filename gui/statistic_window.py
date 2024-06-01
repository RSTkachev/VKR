from os import remove
from os.path import exists

import pandas as pd
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon

from processing.plot_creator import PlotCreator


# Страница статистики
class StatisticWidget(QWidget):
    # Переменные для хранения данных для реализации графов
    statistic_file = None
    cnt_detections = 0
    current_detection = 0

    def __init__(self) -> None:
        super().__init__()

        # Класс-отрисовщик графов
        self.plotter = PlotCreator()

        # Создание интерфеса
        self.refresh_button = QPushButton(
            icon=QIcon('./resources/icons/refresh-cw.svg'),
            text=' Обновить',
        )
        self.refresh_button.setObjectName(u'btn_refresh')
        self.refresh_button.clicked.connect(self.refresh_detections)

        self.button_previous = QPushButton()
        self.button_previous.setText('')
        self.button_previous.setIcon(QIcon('./resources/icons/chevron-left.svg'))
        self.button_previous.setToolTip('Перейти к статистике предыдущей детекции')
        self.button_previous.setObjectName(u'btn_previous')
        self.button_previous.setVisible(False)
        self.button_previous.clicked.connect(self.load_previous_chart)

        self.button_next = QPushButton()
        self.button_next.setText('')
        self.button_next.setIcon(QIcon('./resources/icons/chevron-right.svg'))
        self.button_next.setToolTip('Перейти к статистике следующей детекции')
        self.button_next.setObjectName(u'btn_next')
        self.button_next.setVisible(False)
        self.button_next.clicked.connect(self.load_next_chart)

        self.button_clear = QPushButton()
        self.button_clear.setText('Сбросить статистику')
        self.button_clear.setIcon(QIcon('./resources/icons/trash.svg'))
        self.button_clear.setObjectName(u'btn_clear')
        self.button_clear.setVisible(False)
        self.button_clear.clicked.connect(self.clear_statistic)

        self.chart_text = QLabel()
        self.chart_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_text.setText('Данные для отображения отсутствуют')
        self.chart_text.setObjectName(u'chart_str')

        self.chart = QLabel()
        self.chart.setObjectName(u'chart')
        self.chart.setVisible(False)

        layout = QGridLayout()
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(10)

        layout.addWidget(
            self.refresh_button,
            0, 0, 1, 1,
            alignment=Qt.AlignmentFlag.AlignCenter
            )

        layout.addWidget(
            self.button_clear,
            0, 2, 1, 1,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            self.button_previous,
            1, 0, 1, 1,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        layout.addWidget(
            self.chart_text,
            1, 1, 1, 1,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            self.chart,
            1, 1, 1, 1,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            self.button_next,
            1, 2, 1, 1,
            alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 9)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 1)

        self.setLayout(layout)

        # Попытка открытия файла со статистикой
        if exists('./resources/statistic.csv'):
            self.statistic_file = pd.read_csv('./resources/statistic.csv')
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

    # Переход к предыдущему графу
    def load_previous_chart(self) -> None:
        # Уменьшение номера детекции
        self.current_detection -= 1
        # Обновление графического интерфейса
        if self.current_detection == 0:
            self.button_previous.setVisible(False)
        if self.current_detection < self.cnt_detections - 1:
            self.button_next.setVisible(True)
        # Установка графа
        self.set_plot()

    # Переход к следующему графу
    def load_next_chart(self) -> None:
        # Увеличение номера детекции
        self.current_detection += 1
        # Обновление графического интерфейса
        if self.current_detection == self.cnt_detections - 1:
            self.button_next.setVisible(False)
        if self.current_detection > 0:
            self.button_previous.setVisible(True)
        # Установка графа
        self.set_plot()

    # Обновление статистики из файла
    def refresh_detections(self) -> None:
        # Попытка чтения файла
        if exists('./resources/statistic.csv'):
            self.statistic_file = pd.read_csv('./resources/statistic.csv')
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

    # Удаление файла статистики
    def clear_statistic(self) -> None:
        # Удаление файла
        if exists('./resources/statistic.csv'):
            remove('./resources/statistic.csv')
        # Обновление графического интерфейса
        self.button_previous.setVisible(False)
        self.button_next.setVisible(False)
        self.chart.setVisible(False)
        self.chart_text.setVisible(True)
        self.button_clear.setVisible(False)
        # Обнуление данных по детекциям
        self.current_detection = 0
        self.cnt_detections = 0

    # Установка графа
    def set_plot(self) -> None:
        # Строка для построения графа
        row = self.statistic_file.iloc[self.current_detection]
        # Построение графа
        self.plotter.plot_chart(row)
        # Установка графа
        self.chart.setPixmap(QPixmap('./resources/plot.jpg'))
