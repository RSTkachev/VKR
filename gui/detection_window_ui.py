from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QGridLayout,
    QProgressBar,
    QLabel,
    QComboBox,
    QLineEdit,
    QDoubleSpinBox,
    QCheckBox,
)


class DetectionWidgetUi(QWidget):
    """Интерфейс страницы детекции"""

    def __init__(self) -> None:
        """Инициализация объекта"""

        super().__init__()
        # Элементы окна
        self._btn_process = QPushButton()
        self._btn_process.setText("Выполнить детекцию")
        self._btn_process.setObjectName("btn_process")
        self._btn_process.setMaximumWidth(200)
        self._btn_process.setToolTip("Выполнить детекцию на выбранных материалах")

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setObjectName("progress_bar")

        self._label_global_settings = QLabel()
        self._label_global_settings.setText("Глобальные настройки")
        self._label_global_settings.setObjectName("global_settings")

        self._label_device_text = QLabel()
        self._label_device_text.setObjectName("device_text")
        self._label_device_text.setText("Устройство выполнения детекции")
        self._label_device_text.setToolTip(
            "Параметр определяет, на каком устройстве будет производиться детекция"
        )

        self._device_list = QComboBox()

        self._label_loading_text = QLabel()
        self._label_loading_text.setObjectName("loading_text")
        self._label_loading_text.setText("Директория загрузки")
        self._label_loading_text.setToolTip(
            "Параметр определяет расположение файлов для детекции"
        )

        self._line_edit_loading_path = QLineEdit()

        self._btn_loading_directory = QPushButton()
        self._btn_loading_directory.setText("")
        self._btn_loading_directory.setIcon(QIcon("resources/icons/folder.svg"))
        self._btn_loading_directory.setObjectName("loading_button")

        self._checkbox_find_subdirectories = QCheckBox()

        self._label_find_subdirectories = QLabel()
        self._label_find_subdirectories.setObjectName("find_subdirectories")
        self._label_find_subdirectories.setText("Искать в подкаталогах")
        self._label_find_subdirectories.setToolTip(
            "Параметр определяет, искать ли материалы для детекции в подкаталогах"
        )

        self._layout_find_subdirectories = QHBoxLayout()
        self._layout_find_subdirectories.addWidget(self._checkbox_find_subdirectories)
        self._layout_find_subdirectories.addWidget(self._label_find_subdirectories)
        self._layout_find_subdirectories.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )
        self._layout_find_subdirectories.setSpacing(10)

        self._label_saving_text = QLabel()
        self._label_saving_text.setObjectName("saving_text")
        self._label_saving_text.setText("Директория сохранения")
        self._label_saving_text.setToolTip("Параметр определяет директорию сохранения")

        self._line_edit_saving_path = QLineEdit()
        self._line_edit_saving_path.setEnabled(False)

        self._btn_saving_directory = QPushButton()
        self._btn_saving_directory.setText("")
        self._btn_saving_directory.setIcon(QIcon("resources/icons/folder.svg"))
        self._btn_saving_directory.setObjectName("saving_button")
        self._btn_saving_directory.setEnabled(False)

        self._label_confidence_threshold = QLabel()
        self._label_confidence_threshold.setObjectName("confidence_threshold")
        self._label_confidence_threshold.setText("Порог уверенности")
        self._label_confidence_threshold.setToolTip(
            "Параметр определяет степень уверенности, с которой принимается детекция"
        )

        self._d_spin_box_confidence_value = QDoubleSpinBox()
        self._d_spin_box_confidence_value.setValue(0.5)
        self._d_spin_box_confidence_value.setMinimum(0)
        self._d_spin_box_confidence_value.setMaximum(1)
        self._d_spin_box_confidence_value.setSingleStep(0.05)

        self._label_saving_settings = QLabel()
        self._label_saving_settings.setObjectName("saving_settings")
        self._label_saving_settings.setText("Настройки сохранения")

        self._checkbox_save_images = QCheckBox()
        self._checkbox_save_images.setCheckState(Qt.CheckState.Unchecked)

        self._label_save_images_text = QLabel()
        self._label_save_images_text.setText("Сохранить материалы детекции")
        self._label_save_images_text.setObjectName("save_images_text")
        self._label_save_images_text.setToolTip(
            "Параметр определяет, сохранять ли материалы детекции"
        )

        self._checkbox_draw_bbox = QCheckBox()
        self._checkbox_draw_bbox.setCheckState(Qt.CheckState.Unchecked)

        self._label_draw_bbox = QLabel()
        self._label_draw_bbox.setText("Выделить детекции объектов")
        self._label_draw_bbox.setObjectName("draw_bbox_text")
        self._label_draw_bbox.setToolTip(
            "Параметр определяет, выделять ли на сохраняемых материалах детекции объектов ограничивающими рамками"
        )

        self._layout_draw_bbox = QHBoxLayout()
        self._layout_draw_bbox.addWidget(self._checkbox_draw_bbox)
        self._layout_draw_bbox.addWidget(self._label_draw_bbox)
        self._layout_draw_bbox.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )
        self._layout_draw_bbox.setSpacing(10)

        self._checkbox_group_images = QCheckBox()
        self._checkbox_group_images.setCheckState(Qt.CheckState.Unchecked)

        self._label_group_images_text = QLabel()
        self._label_group_images_text.setText("Сгруппировать изображения по классам")
        self._label_group_images_text.setObjectName("group_images_text")
        self._label_group_images_text.setToolTip(
            "Параметр определяет, необходимо ли группировать сохраняемые материалы по классам объектов"
        )

        self._layout_group_images = QHBoxLayout()
        self._layout_group_images.addWidget(self._checkbox_group_images)
        self._layout_group_images.addWidget(self._label_group_images_text)
        self._layout_group_images.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )
        self._layout_group_images.setSpacing(10)

        self._checkbox_save_statistic = QCheckBox()
        self._checkbox_save_statistic.setCheckState(Qt.CheckState.Unchecked)

        self._label_save_statistic_text = QLabel()
        self._label_save_statistic_text.setText("Сохранить подробную статистику")
        self._label_save_statistic_text.setObjectName("save_statistic_text")
        self._label_save_statistic_text.setToolTip(
            "Параметр определяет, необходимо ли сохранять сохранять статистику для каждого файла"
        )

        self._btn_abort = QPushButton()
        self._btn_abort.setText("")
        self._btn_abort.setIcon(QIcon("./resources/icons/x.svg"))
        self._btn_abort.setObjectName("abort_button")
        self._btn_abort.setEnabled(False)
        self._btn_abort.setToolTip("Прервать выполнение детекции")

        # Определение и настройка шаблона
        self._layout = QGridLayout()
        self._layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        self._layout.addWidget(
            self._label_global_settings, 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter
        )
        self._layout.addWidget(
            self._label_device_text, 1, 0, 1, 1, Qt.AlignmentFlag.AlignVCenter
        )
        self._layout.addWidget(
            self._device_list, 1, 1, 1, 1, Qt.AlignmentFlag.AlignVCenter
        )
        self._layout.addWidget(
            self._label_loading_text, 2, 0, 1, 1, Qt.AlignmentFlag.AlignVCenter
        )
        self._layout.addWidget(
            self._line_edit_loading_path, 2, 1, 1, 1, Qt.AlignmentFlag.AlignVCenter
        )
        self._layout.addWidget(
            self._btn_loading_directory,
            2,
            2,
            1,
            1,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
        )
        self._layout.addLayout(
            self._layout_find_subdirectories,
            3,
            0,
            1,
            3,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
        )
        self._layout.addWidget(
            self._label_saving_text, 4, 0, 1, 1, Qt.AlignmentFlag.AlignVCenter
        )
        self._layout.addWidget(
            self._line_edit_saving_path, 4, 1, 1, 1, Qt.AlignmentFlag.AlignVCenter
        )
        self._layout.addWidget(
            self._btn_saving_directory,
            4,
            2,
            1,
            1,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
        )
        self._layout.addWidget(
            self._label_confidence_threshold, 5, 0, 1, 1, Qt.AlignmentFlag.AlignVCenter
        )
        self._layout.addWidget(
            self._d_spin_box_confidence_value,
            5,
            1,
            1,
            1,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
        )
        self._layout.addWidget(
            self._label_saving_settings, 0, 4, 1, 3, Qt.AlignmentFlag.AlignCenter
        )

        self._layout.addWidget(
            self._checkbox_save_images,
            1,
            4,
            1,
            1,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
        )

        self._layout.addWidget(
            self._label_save_images_text, 1, 5, 1, 2, Qt.AlignmentFlag.AlignVCenter
        )

        self._layout.addLayout(
            self._layout_draw_bbox,
            2,
            5,
            1,
            2,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
        )

        self._layout.addLayout(
            self._layout_group_images,
            3,
            5,
            1,
            2,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
        )

        self._layout.addWidget(
            self._checkbox_save_statistic,
            4,
            4,
            1,
            1,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
        )
        self._layout.addWidget(
            self._label_save_statistic_text, 4, 5, 1, 2, Qt.AlignmentFlag.AlignVCenter
        )

        self._layout.addWidget(
            self._btn_process, 7, 0, 1, 1, Qt.AlignmentFlag.AlignVCenter
        )
        self._layout.addWidget(
            self._progress_bar, 7, 1, 1, 5, Qt.AlignmentFlag.AlignVCenter
        )
        self._layout.addWidget(
            self._btn_abort,
            7,
            6,
            1,
            1,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
        )

        self._layout.setContentsMargins(60, 40, 60, 40)
        self._layout.setVerticalSpacing(20)
        self._layout.setHorizontalSpacing(10)

        self._layout.setColumnStretch(0, 16)
        self._layout.setColumnStretch(1, 16)
        self._layout.setColumnStretch(2, 9)
        self._layout.setColumnStretch(3, 8)
        self._layout.setColumnStretch(4, 8)
        self._layout.setColumnStretch(5, 32)
        self._layout.setColumnStretch(6, 1)

        self.setLayout(self._layout)
