from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy, QGridLayout
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap, QFont

import resources.strings


# Информационная страница
class InfoWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()

        # Создание графического интерфеса
        app_icon = QLabel()
        app_icon.setPixmap(QPixmap(resources.strings.label_path))
        app_icon.setMaximumSize(QSize(200, 200))
        app_icon.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        app_icon.setScaledContents(True)
        app_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        app_name = QLabel()
        app_name.setText('\n' + resources.strings.app_name.upper())
        app_name.setFont(QFont('Open Sans Semibold', 14))
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text_info = QLabel()
        text_info.setText(resources.strings.info_text)
        text_info.setFont(QFont('Open Sans', 12))
        text_info.adjustSize()
        text_info.setWordWrap(True)
        text_info.setScaledContents(True)

        python_icon = QLabel()
        python_icon.setPixmap(QPixmap(resources.strings.python_path))
        python_icon.setMaximumSize(QSize(150, 150))
        python_icon.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        python_icon.setScaledContents(True)
        python_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pyside_icon = QLabel()
        pyside_icon.setPixmap(QPixmap(resources.strings.pyside_path))
        pyside_icon.setMaximumSize(QSize(150, 150))
        pyside_icon.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        pyside_icon.setScaledContents(True)
        pyside_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        yolo_icon = QLabel()
        yolo_icon.setPixmap(QPixmap(resources.strings.ultralytics_yolo_path))
        yolo_icon.setMaximumSize(QSize(150, 150))
        yolo_icon.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        yolo_icon.setScaledContents(True)
        yolo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        contact_info = QLabel()
        contact_info.setText('КОНТАКТНАЯ ИНФОРМАЦИЯ')
        contact_info.setFont(QFont('Open Sans Semibold', 14))
        contact_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        phone_number = QLabel()
        phone_number.setText(f'Телефон:\n{resources.strings.phone_number}')
        phone_number.setFont(QFont('Open Sans', 12))
        phone_number.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        email = QLabel()
        email.setText(f'Email:\n{resources.strings.email}')
        email.setFont(QFont('Open Sans', 12))
        email.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout = QGridLayout()

        layout.addWidget(app_icon, 0, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(app_name, 1, 1, 1, 1, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(text_info, 2, 0, 1, 3, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(python_icon, 3, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(pyside_icon, 3, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(yolo_icon, 3, 2, 1, 1, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(contact_info, 4, 1, 1, 1, Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(phone_number, 5, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(email, 5, 2, 1, 1, Qt.AlignmentFlag.AlignCenter)

        layout.setColumnStretch(0, 4)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(2, 4)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 2)
        layout.setRowStretch(3, 1)
        layout.setRowStretch(4, 1)
        layout.setRowStretch(5, 1)
        layout.setContentsMargins(80, 80, 80, 80)

        self.setLayout(layout)
