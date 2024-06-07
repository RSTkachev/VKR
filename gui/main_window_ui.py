from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QStackedWidget,
    QMainWindow,
    QWidget,
)


class UiMainWindow(QMainWindow):
    """Интерфейс окна"""

    def __init__(self):
        """Инициализация объекта"""

        super().__init__()

        # Создание интерфеса
        self._grid_layout = QGridLayout()
        self._grid_layout.setSpacing(0)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)

        self._title_frame = QFrame()
        self._title_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self._title_frame.setFrameShadow(QFrame.Shadow.Raised)
        self._title_frame.setObjectName("title_frame")

        self._title_frame_layout = QHBoxLayout(self._title_frame)
        self._title_icon = QLabel(self._title_frame)
        self._title_icon.setScaledContents(True)
        self._title_icon.setObjectName("title_icon")

        self._title_label = QLabel(self._title_frame)
        self._title_label.setObjectName("title_label")

        self._menu_btn = QPushButton(self._title_frame)
        self._menu_btn.setText("")
        self._menu_btn.setIconSize(QSize(24, 24))
        self._menu_btn.setObjectName("menu_btn")

        self._title_frame_layout.addWidget(self._title_icon)
        self._title_frame_layout.addWidget(self._title_label)
        self._title_frame_layout.addWidget(
            self._menu_btn, alignment=Qt.AlignmentFlag.AlignRight
        )

        self._grid_layout.addWidget(self._title_frame, 0, 0, 1, 2)

        self._main_content = QStackedWidget()

        self._grid_layout.addWidget(self._main_content, 0, 2, 2, 1)

        self._side_menu_collapsed = QListWidget()
        self._side_menu_collapsed.setObjectName("listWidget_collapsed")
        self._side_menu_collapsed.setMinimumWidth(55)
        self._side_menu_collapsed.setMaximumSize(QSize(55, 16777215))

        self._grid_layout.addWidget(self._side_menu_collapsed, 1, 0, 1, 1)

        self._side_menu = QListWidget()
        self._side_menu.setObjectName("listWidget")
        self._side_menu.setMinimumWidth(200)
        self._side_menu.setMaximumSize(QSize(200, 16777215))

        self._grid_layout.addWidget(self._side_menu, 1, 1, 1, 1)

        self._widget = QWidget()
        self._widget.setLayout(self._grid_layout)
        self.setCentralWidget(self._widget)
