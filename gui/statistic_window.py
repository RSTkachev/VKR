from os.path import exists

import pandas as pd
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QSizePolicy, QGridLayout
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap, QFont, QIcon

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

matplotlib.use('Qt5Agg')


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

        self.button_previous = QPushButton()
        self.button_previous.setText('')
        self.button_previous.setIcon(QIcon('./resources/icons/chevron-left.svg'))
        self.button_previous.setObjectName(u'btn_previous')
        self.button_previous.setEnabled(False)
        self.button_previous.setVisible(False)
        self.button_previous.clicked.connect(self.load_previous_chart)

        self.button_next = QPushButton()
        self.button_next.setText('')
        self.button_next.setIcon(QIcon('./resources/icons/chevron-right.svg'))
        self.button_next.setObjectName(u'btn_next')
        self.button_previous.setEnabled(False)
        self.button_previous.setVisible(False)
        self.button_next.clicked.connect(self.load_next_chart)

        self.chart_text = QLabel()
        self.chart_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_text.setText('Данные для отображения отсутствуют')
        self.chart_text.setObjectName(u'chart_str')

        self.chart = QLabel()
        self.chart.setObjectName(u'chart')
        self.chart.setVisible(False)

        if exists('./statistic.csv'):
            self.statistic_file = pd.read_csv('./statistic.csv')
            self.cnt_detections = self.statistic_file.shape[0]

        if self.cnt_detections > 0:
            self.button_previous.setVisible(True)
            self.button_next.setVisible(True)
            self.chart_text.setVisible(False)
            self.chart.setVisible(True)
            self.plot_chart()
            if self.cnt_detections > 1:
                self.button_next.setEnabled(True)

        layout = QGridLayout()
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(10)

        layout.addWidget(self.refresh_button, 0, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.button_previous, 1, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.chart_text, 1, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.chart, 1, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.button_next, 1, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 9)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 1)

        self.setLayout(layout)

    def load_previous_chart(self):
        self.current_detection -= 1
        if self.current_detection == 0:
            self.button_previous.setEnabled(False)
        if self.current_detection < self.cnt_detections - 1:
            self.button_next.setEnabled(True)
        self.plot_chart()

    def load_next_chart(self):
        self.current_detection += 1
        if self.current_detection == self.cnt_detections - 1:
            self.button_next.setEnabled(False)
        if self.current_detection > 0:
            self.button_previous.setEnabled(True)
        self.plot_chart()

    def refresh_detections(self):
        if exists('./statistic.csv'):
            self.statistic_file = pd.read_csv('./statistic.csv')
            self.cnt_detections = self.statistic_file.shape[0]

            if self.cnt_detections:
                self.button_previous.setVisible(True)
                self.button_next.setVisible(True)
                self.chart.setVisible(True)

        if self.current_detection < self.cnt_detections - 1:
            self.button_next.setEnabled(True)

    def plot_chart(self):
        fig, ax = plt.subplots(1, 1)
        ax = plt.bar(self.statistic_file.columns, self.statistic_file.loc[self.current_detection])
        fig.autofmt_xdate(rotation=90)
        plt.title('Количество обнаруженных животных')
        self.addlabels(self.statistic_file.columns, self.statistic_file.loc[self.current_detection].astype(int))
        plt.savefig('./resources/plot.jpg', bbox_inches='tight')
        self.chart.setPixmap(QPixmap('./resources/plot.jpg'))

    def addlabels(self, x, y):
        for i in range(len(x)):
            if y[i]:
                plt.text(i, y[i] / 2, y[i], ha='center', rotation=90)


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=8, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.autofmt_xdate(rotation=90)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
