from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QStackedWidget,
    QWidget,
    QMainWindow,
)


class UiMainWindow:
    """Интерфейс окна"""

    def __init__(self, main_window: QMainWindow):
        """
        Инициализация объекта

        Args:
            main_window - родительский элемент
        """

        # Создание интерфеса
        self.central_widget = QWidget(main_window)

        self.gridLayout = QGridLayout(self.central_widget)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        self.title_frame = QFrame(self.central_widget)
        self.title_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.title_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.title_frame.setObjectName("title_frame")

        self.horizontalLayout = QHBoxLayout(self.title_frame)
        self.title_icon = QLabel(self.title_frame)
        self.title_icon.setPixmap(QPixmap("./resources/icons/deer.svg"))
        self.title_icon.setScaledContents(True)
        self.title_icon.setObjectName("title_icon")

        self.title_label = QLabel(self.title_frame)
        self.title_label.setText("WLD")
        self.title_label.setObjectName("title_label")

        self.menu_btn = QPushButton(self.title_frame)
        self.menu_btn.setIcon(QIcon("./resources/icons/menu.svg"))
        self.menu_btn.setText("")
        self.menu_btn.setIconSize(QSize(24, 24))
        self.menu_btn.setObjectName("menu_btn")

        self.horizontalLayout.addWidget(self.title_icon)
        self.horizontalLayout.addWidget(self.title_label)
        self.horizontalLayout.addWidget(
            self.menu_btn, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.gridLayout.addWidget(self.title_frame, 0, 0, 1, 2)

        self.stackedWidget = QStackedWidget(self.central_widget)

        self.gridLayout.addWidget(self.stackedWidget, 0, 2, 2, 1)

        self.listWidget_collapsed = QListWidget(self.central_widget)
        self.listWidget_collapsed.setObjectName("listWidget_collapsed")
        self.listWidget_collapsed.setMinimumWidth(55)
        self.listWidget_collapsed.setMaximumSize(QSize(55, 16777215))

        self.gridLayout.addWidget(self.listWidget_collapsed, 1, 0, 1, 1)

        self.listWidget = QListWidget(self.central_widget)
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setMinimumWidth(200)
        self.listWidget.setMaximumSize(QSize(200, 16777215))

        self.gridLayout.addWidget(self.listWidget, 1, 1, 1, 1)

        main_window.setCentralWidget(self.central_widget)
