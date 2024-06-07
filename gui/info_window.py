from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy, QGridLayout

import resources.strings


class InfoWidget(QWidget):
    """Информационная страница"""

    def __init__(self) -> None:
        """Инициализация объекта"""

        super().__init__()

        # Создание графического интерфеса
        self.__app_icon = QLabel()
        self.__app_icon.setPixmap(QPixmap(resources.strings.label_path))
        self.__app_icon.setMaximumSize(QSize(200, 200))
        self.__app_icon.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum
        )
        self.__app_icon.setScaledContents(True)
        self.__app_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__app_name = QLabel()
        self.__app_name.setText("\n" + resources.strings.app_name.upper())
        self.__app_name.setFont(QFont("Open Sans Semibold", 14))
        self.__app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__text_info = QLabel()
        self.__text_info.setText(resources.strings.info_text)
        self.__text_info.setFont(QFont("Open Sans", 12))
        self.__text_info.adjustSize()
        self.__text_info.setWordWrap(True)
        self.__text_info.setScaledContents(True)

        self.__python_icon = QLabel()
        self.__python_icon.setPixmap(QPixmap(resources.strings.python_path))
        self.__python_icon.setMaximumSize(QSize(150, 150))
        self.__python_icon.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum
        )
        self.__python_icon.setScaledContents(True)
        self.__python_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__pyside_icon = QLabel()
        self.__pyside_icon.setPixmap(QPixmap(resources.strings.pyside_path))
        self.__pyside_icon.setMaximumSize(QSize(150, 150))
        self.__pyside_icon.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum
        )
        self.__pyside_icon.setScaledContents(True)
        self.__pyside_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__yolo_icon = QLabel()
        self.__yolo_icon.setPixmap(QPixmap(resources.strings.ultralytics_yolo_path))
        self.__yolo_icon.setMaximumSize(QSize(150, 150))
        self.__yolo_icon.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum
        )
        self.__yolo_icon.setScaledContents(True)
        self.__yolo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__contact_info = QLabel()
        self.__contact_info.setText("КОНТАКТНАЯ ИНФОРМАЦИЯ")
        self.__contact_info.setFont(QFont("Open Sans Semibold", 14))
        self.__contact_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__phone_number = QLabel()
        self.__phone_number.setText(f"Телефон:\n{resources.strings.phone_number}")
        self.__phone_number.setFont(QFont("Open Sans", 12))
        self.__phone_number.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.__email = QLabel()
        self.__email.setText(f"Email:\n{resources.strings.email}")
        self.__email.setFont(QFont("Open Sans", 12))
        self.__email.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.__layout = QGridLayout()

        self.__layout.addWidget(
            self.__app_icon, 0, 1, 1, 1, Qt.AlignmentFlag.AlignCenter
        )

        self.__layout.addWidget(self.__app_name, 1, 1, 1, 1, Qt.AlignmentFlag.AlignTop)
        self.__layout.addWidget(self.__text_info, 2, 0, 1, 3, Qt.AlignmentFlag.AlignTop)
        self.__layout.addWidget(
            self.__python_icon, 3, 0, 1, 1, Qt.AlignmentFlag.AlignCenter
        )

        self.__layout.addWidget(
            self.__pyside_icon, 3, 1, 1, 1, Qt.AlignmentFlag.AlignCenter
        )

        self.__layout.addWidget(
            self.__yolo_icon, 3, 2, 1, 1, Qt.AlignmentFlag.AlignCenter
        )

        self.__layout.addWidget(
            self.__contact_info, 4, 1, 1, 1, Qt.AlignmentFlag.AlignBottom
        )

        self.__layout.addWidget(
            self.__phone_number, 5, 0, 1, 1, Qt.AlignmentFlag.AlignCenter
        )

        self.__layout.addWidget(self.__email, 5, 2, 1, 1, Qt.AlignmentFlag.AlignCenter)

        self.__layout.setColumnStretch(0, 4)
        self.__layout.setColumnStretch(1, 2)
        self.__layout.setColumnStretch(2, 4)

        self.__layout.setRowStretch(0, 1)
        self.__layout.setRowStretch(1, 1)
        self.__layout.setRowStretch(2, 2)
        self.__layout.setRowStretch(3, 1)
        self.__layout.setRowStretch(4, 1)
        self.__layout.setRowStretch(5, 1)
        self.__layout.setContentsMargins(80, 80, 80, 80)

        self.setLayout(self.__layout)
