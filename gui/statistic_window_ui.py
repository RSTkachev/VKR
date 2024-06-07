from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout


class StatisticWindowUi(QWidget):
    """Интерфейс страницы статистики"""

    def __init__(self) -> None:
        """Инициализация объекта"""

        super().__init__()

        # Создание интерфеса
        self._refresh_button = QPushButton(
            icon=QIcon("./resources/icons/refresh-cw.svg"),
            text=" Обновить",
        )
        self._refresh_button.setObjectName("btn_refresh")

        self._button_previous = QPushButton()
        self._button_previous.setText("")
        self._button_previous.setIcon(QIcon("./resources/icons/chevron-left.svg"))
        self._button_previous.setToolTip("Перейти к статистике предыдущей детекции")
        self._button_previous.setObjectName("btn_previous")
        self._button_previous.setVisible(False)

        self._button_next = QPushButton()
        self._button_next.setText("")
        self._button_next.setIcon(QIcon("./resources/icons/chevron-right.svg"))
        self._button_next.setToolTip("Перейти к статистике следующей детекции")
        self._button_next.setObjectName("btn_next")
        self._button_next.setVisible(False)

        self._button_clear = QPushButton()
        self._button_clear.setText(" Сбросить статистику")
        self._button_clear.setIcon(QIcon("./resources/icons/trash.svg"))
        self._button_clear.setObjectName("btn_clear")
        self._button_clear.setVisible(False)

        self._chart_text = QLabel()
        self._chart_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._chart_text.setText("Данные для отображения отсутствуют")
        self._chart_text.setObjectName("chart_str")

        self._chart = QLabel()
        self._chart.setObjectName("_chart")
        self._chart.setVisible(False)

        self._layout = QGridLayout()
        self._layout.setContentsMargins(60, 40, 60, 40)
        self._layout.setSpacing(10)

        self._layout.addWidget(
            self._refresh_button, 0, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter
        )

        self._layout.addWidget(
            self._button_clear, 0, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter
        )

        self._layout.addWidget(
            self._button_previous,
            1,
            0,
            1,
            1,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )

        self._layout.addWidget(
            self._chart_text, 1, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter
        )

        self._layout.addWidget(
            self._chart, 1, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter
        )

        self._layout.addWidget(
            self._button_next,
            1,
            2,
            1,
            1,
            alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )

        self._layout.setRowStretch(0, 1)
        self._layout.setRowStretch(1, 9)

        self._layout.setColumnStretch(0, 1)
        self._layout.setColumnStretch(1, 4)
        self._layout.setColumnStretch(2, 1)

        self.setLayout(self._layout)
