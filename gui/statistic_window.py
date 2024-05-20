from os.path import exists

import pandas as pd
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

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
        self.refresh_button.clicked.connect(self.refresh_detections)

        self.button_previous = QPushButton()
        self.button_previous.setText('')
        self.button_previous.setIcon(QIcon('./resources/icons/chevron-left.svg'))
        self.button_previous.setObjectName(u'btn_previous')
        self.button_previous.setVisible(False)
        self.button_previous.clicked.connect(self.load_previous_chart)

        self.button_next = QPushButton()
        self.button_next.setText('')
        self.button_next.setIcon(QIcon('./resources/icons/chevron-right.svg'))
        self.button_next.setObjectName(u'btn_next')
        self.button_next.setVisible(False)
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

        layout = QGridLayout()
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(10)

        layout.addWidget(
            self.refresh_button,
            0, 0, 1, 1,
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
        if exists('./statistic.csv'):
            self.statistic_file = pd.read_csv('./statistic.csv')
            self.cnt_detections = self.statistic_file.shape[0]

            if self.current_detection < self.cnt_detections - 1:
                self.button_next.setVisible(True)

            if self.cnt_detections:
                self.chart_text.setVisible(False)
                self.chart.setVisible(True)
                self.set_plot()

    def set_plot(self):
        row = self.statistic_file.iloc[self.current_detection]
        plot_chart(row)
        self.chart.setPixmap(QPixmap('./resources/plot.jpg'))


def plot_chart(row):
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
    plt.savefig('./resources/plot.jpg', bbox_inches='tight')
    plt.close(fig)


def add_labels(row):
    for column in range(row.shape[0]):
        if row.iloc[column]:
            plt.text(column, row.iloc[column] / 2, row.iloc[column].astype(int), ha='center', rotation=90)
