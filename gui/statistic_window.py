from os import remove
from os.path import exists

import pandas as pd
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon

from processing.plot_creator import plot_chart


class StatisticWidget(QWidget):
    statistic_file = None
    cnt_detections = 0
    current_detection = 0

    def __init__(self):
        super().__init__()

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

        if exists('./resources/statistic.csv'):
            self.statistic_file = pd.read_csv('./resources/statistic.csv')
            self.cnt_detections = self.statistic_file.shape[0]

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


        if self.cnt_detections > 0:
            self.chart_text.setVisible(False)
            self.chart.setVisible(True)
            self.button_clear.setVisible(True)
            self.set_plot()
            if self.cnt_detections > 1:
                self.button_next.setVisible(True)

    def load_previous_chart(self):
        self.current_detection -= 1
        if self.current_detection == 0:
            self.button_previous.setVisible(False)
        if self.current_detection < self.cnt_detections - 1:
            self.button_next.setVisible(True)
        self.set_plot()

    def load_next_chart(self):
        self.current_detection += 1
        if self.current_detection == self.cnt_detections - 1:
            self.button_next.setVisible(False)
        if self.current_detection > 0:
            self.button_previous.setVisible(True)
        self.set_plot()

    def refresh_detections(self):
        if exists('./resources/statistic.csv'):
            self.statistic_file = pd.read_csv('./resources/statistic.csv')
            self.cnt_detections = self.statistic_file.shape[0]

            if self.current_detection < self.cnt_detections - 1:
                self.button_next.setVisible(True)

            if self.cnt_detections:
                self.chart_text.setVisible(False)
                self.chart.setVisible(True)
                self.button_clear.setVisible(True)
                self.set_plot()

    def clear_statistic(self):
        if exists('./resources/statistic.csv'):
            remove('./resources/statistic.csv')
        self.button_previous.setVisible(False)
        self.button_next.setVisible(False)
        self.chart.setVisible(False)
        self.chart_text.setVisible(True)
        self.button_clear.setVisible(False)
        self.current_detection = 0
        self.cnt_detections = 0

    def set_plot(self):
        row = self.statistic_file.iloc[self.current_detection]
        plot_chart(row)
        self.chart.setPixmap(QPixmap('./resources/plot.jpg'))
