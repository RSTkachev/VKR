from os import path

from PySide6.QtCore import QThread, Signal, Slot
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import (
    QWidget,
    QFileDialog,
    QPushButton,
    QGridLayout,
    QProgressBar,
    QLabel,
    QComboBox,
    QLineEdit,
    QDoubleSpinBox,
    QCheckBox,
    QMessageBox,
)
from torch.cuda import device_count, get_device_name

from processing.detection_worker import DetectionWorker


class DetectionWidget(QWidget):
    """Страница детектирования"""

    # Сигнал потоку-обработчику
    load_model = Signal(str)
    set_device = Signal(str)
    prediction_signal = Signal(
        str, str, float, Qt.CheckState, Qt.CheckState, Qt.CheckState
    )

    def __init__(self):
        """Инициализация объекта"""

        super().__init__()

        # Определение обработчика
        self.worker = DetectionWorker()
        self.worker_thread = QThread()
        self.worker.set_enable_state.connect(self.btn_process_set_enable_state)
        self.worker.btn_abort_upload_state.connect(self.btn_abort_upload_state)
        self.worker.set_progress_bar_value.connect(self.upload_progress_bar_value)
        self.worker.inform_end.connect(self.inform_about_end_processing)
        self.load_model.connect(self.worker.load_model)
        self.set_device.connect(self.worker.set_device)
        self.prediction_signal.connect(self.worker.make_prediction)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()
        self.load_model.emit("./resources/model_ru.pt")

        # Элементы окна
        self.btn_process = QPushButton()
        self.btn_process.setText("Выполнить детекцию")
        self.btn_process.clicked.connect(self.process)
        self.btn_process.setObjectName("btn_process")
        self.btn_process.setMaximumWidth(200)
        self.btn_process.setToolTip("Выполнить детекцию на выбранных материалах")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setObjectName("progress_bar")

        label_global_settings = QLabel()
        label_global_settings.setText("Глобальные настройки")
        label_global_settings.setObjectName("global_settings")

        label_device_text = QLabel()
        label_device_text.setObjectName("device_text")
        label_device_text.setText("Устройство выполнения детекции")
        label_device_text.setToolTip(
            "Параметр определяет, на каком устройстве будет производиться детекция"
        )

        dev_cnt = device_count()
        devices = ["CPU"]
        for device_index in range(dev_cnt):
            devices.append(get_device_name(device_index))

        self.device_list = QComboBox()
        for device in devices:
            self.device_list.addItem(device)

        label_loading_text = QLabel()
        label_loading_text.setObjectName("loading_text")
        label_loading_text.setText("Директория загрузки")
        label_loading_text.setToolTip(
            "Параметр определяет расположение файлов для детекции"
        )

        self.line_edit_loading_path = QLineEdit()

        self.btn_loading_directory = QPushButton()
        self.btn_loading_directory.setText("")
        self.btn_loading_directory.setIcon(QIcon("resources/icons/folder.svg"))
        self.btn_loading_directory.setObjectName("loading_button")
        self.btn_loading_directory.clicked.connect(self.chose_load_directory)

        label_saving_text = QLabel()
        label_saving_text.setObjectName("saving_text")
        label_saving_text.setText("Директория сохранения")
        label_saving_text.setToolTip("Параметр определяет директорию сохранения")

        self.line_edit_saving_path = QLineEdit()

        self.btn_saving_directory = QPushButton()
        self.btn_saving_directory.setText("")
        self.btn_saving_directory.setIcon(QIcon("resources/icons/folder.svg"))
        self.btn_saving_directory.setObjectName("saving_button")
        self.btn_saving_directory.clicked.connect(self.chose_save_directory)

        label_confidence_threshold = QLabel()
        label_confidence_threshold.setObjectName("confidence_threshold")
        label_confidence_threshold.setText("Порог уверенности")
        label_confidence_threshold.setToolTip(
            "Параметр определяет степень уверенности, с которой принимается детекция"
        )

        self.d_spin_box_confidence_value = QDoubleSpinBox()
        self.d_spin_box_confidence_value.setValue(0.5)
        self.d_spin_box_confidence_value.setMinimum(0)
        self.d_spin_box_confidence_value.setMaximum(1)
        self.d_spin_box_confidence_value.setSingleStep(0.05)

        label_saving_settings = QLabel()
        label_saving_settings.setObjectName("saving_settings")
        label_saving_settings.setText("Настройки сохранения")

        self.checkbox_save_images = QCheckBox()
        self.checkbox_save_images.setCheckState(Qt.CheckState.Checked)

        label_save_images_text = QLabel()
        label_save_images_text.setText("Сохранять изображения с отметками детекций")
        label_save_images_text.setObjectName("save_image_text")
        label_save_images_text.setToolTip(
            "Параметр определяет, сохранять ли изображения с отметками детекций. Требует указания директории сохранения"
        )

        self.checkbox_save_statistic = QCheckBox()
        self.checkbox_save_statistic.setCheckState(Qt.CheckState.Checked)

        label_save_statistic_text = QLabel()
        label_save_statistic_text.setText("Сохранять статистику")
        label_save_statistic_text.setObjectName("save_statistic_text")
        label_save_statistic_text.setToolTip(
            "Параметр определяет, необходимо ли сохранять сохранять статистику по детекциям. Требует указания директории сохранения"
        )

        self.checkbox_group_images = QCheckBox()
        self.checkbox_group_images.setCheckState(Qt.CheckState.Checked)

        label_group_images_text = QLabel()
        label_group_images_text.setText("Группировать изображения по классам")
        label_group_images_text.setObjectName("group_images_text")
        label_group_images_text.setToolTip(
            "Параметр определяет, необходимо ли группировать изображения по классам. Требует указания директории сохранения"
        )

        self.btn_abort = QPushButton()
        self.btn_abort.setText("")
        self.btn_abort.setIcon(QIcon("./resources/icons/x.svg"))
        self.btn_abort.setObjectName("abort_button")
        self.btn_abort.clicked.connect(self.btn_abort_clicked)
        self.btn_abort.setEnabled(False)
        self.btn_abort.setToolTip("Прервать выполнение детекции")

        # Определение и настройка шаблона
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(
            label_global_settings, 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter
        )
        layout.addWidget(label_device_text, 1, 0, 1, 1, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.device_list, 1, 1, 1, 1, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(label_loading_text, 2, 0, 1, 1, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(
            self.line_edit_loading_path, 2, 1, 1, 1, Qt.AlignmentFlag.AlignVCenter
        )
        layout.addWidget(
            self.btn_loading_directory,
            2,
            2,
            1,
            1,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
        )
        layout.addWidget(label_saving_text, 3, 0, 1, 1, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(
            self.line_edit_saving_path, 3, 1, 1, 1, Qt.AlignmentFlag.AlignVCenter
        )
        layout.addWidget(
            self.btn_saving_directory,
            3,
            2,
            1,
            1,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
        )
        layout.addWidget(
            label_confidence_threshold, 4, 0, 1, 1, Qt.AlignmentFlag.AlignVCenter
        )
        layout.addWidget(
            self.d_spin_box_confidence_value,
            4,
            1,
            1,
            1,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
        )

        layout.addWidget(
            label_saving_settings, 0, 3, 1, 2, Qt.AlignmentFlag.AlignCenter
        )
        layout.addWidget(
            self.checkbox_save_images,
            1,
            3,
            1,
            1,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
        )
        layout.addWidget(
            label_save_images_text, 1, 4, 1, 2, Qt.AlignmentFlag.AlignVCenter
        )
        layout.addWidget(
            self.checkbox_save_statistic,
            2,
            3,
            1,
            1,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
        )
        layout.addWidget(
            label_save_statistic_text, 2, 4, 1, 2, Qt.AlignmentFlag.AlignVCenter
        )
        layout.addWidget(
            self.checkbox_group_images,
            3,
            3,
            1,
            1,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
        )
        layout.addWidget(
            label_group_images_text, 3, 4, 1, 2, Qt.AlignmentFlag.AlignVCenter
        )

        layout.addWidget(self.btn_process, 6, 0, 1, 1, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.progress_bar, 6, 1, 1, 4, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(
            self.btn_abort,
            6,
            5,
            1,
            1,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
        )

        layout.setContentsMargins(60, 40, 60, 40)
        layout.setVerticalSpacing(20)
        layout.setHorizontalSpacing(10)

        layout.setColumnStretch(0, 16)
        layout.setColumnStretch(1, 16)
        layout.setColumnStretch(2, 8)
        layout.setColumnStretch(3, 8)
        layout.setColumnStretch(4, 32)
        layout.setColumnStretch(5, 1)

        self.setLayout(layout)

    def chose_load_directory(self) -> None:
        """Установка директории-источника"""

        directory = QFileDialog.getExistingDirectory()
        self.line_edit_loading_path.setText(directory)

    def chose_save_directory(self):
        """Установка директории-назначения"""

        directory = QFileDialog.getExistingDirectory()
        self.line_edit_saving_path.setText(directory)

    def process(self):
        """Запуск обработки"""

        device = self.device_list.currentText()
        source = self.line_edit_loading_path.text()
        destination = self.line_edit_saving_path.text()
        confidence = self.d_spin_box_confidence_value.value()
        save_image = self.checkbox_save_images.checkState()
        save_statistic = self.checkbox_save_statistic.checkState()
        group_images = self.checkbox_group_images.checkState()
        if not source:
            dialog = QMessageBox(self)
            dialog.warning(
                self,
                "Обработка невозможна!",
                "Пожалуйста, введите директорию загрузки",
                QMessageBox.StandardButton.Ok,
            )
            return
        if not path.isdir(source):
            dialog = QMessageBox(self)
            dialog.warning(
                self,
                "Обработка невозможна!",
                "Путь директории загрузки некорректен",
                QMessageBox.StandardButton.Ok,
            )
            return
        if not destination and (
            save_image == Qt.CheckState.Checked
            or save_statistic == Qt.CheckState.Checked
            or group_images == Qt.CheckState.Checked
        ):
            dialog = QMessageBox(self)
            dialog.warning(
                self,
                "Обработка невозможна!",
                "Пожалуйста, введите директорию сохранения",
                QMessageBox.StandardButton.Ok,
            )
            return
        if destination and not path.isdir(destination):
            dialog = QMessageBox(self)
            dialog.warning(
                self,
                "Обработка невозможна!",
                "Путь директории сохранения некорректен",
                QMessageBox.StandardButton.Ok,
            )
            return

        self.set_device.emit(device)
        self.prediction_signal.emit(
            source, destination, confidence, save_image, save_statistic, group_images
        )

    def btn_abort_clicked(self):
        """Аборт обработки"""
        self.worker.is_working = False

    @Slot()
    def btn_process_set_enable_state(self):
        """Обновление состояния кнопки загрузки"""
        is_enable = self.btn_process.isEnabled()
        self.btn_process.setEnabled(not is_enable)

    @Slot(bool)
    def btn_abort_upload_state(self, is_abort: bool) -> None:
        """
        Обновление состояния кнопки аборта детекции

        Args:
            is_abort - была ли нажата кнопка аборта
        """

        is_enable = self.btn_abort.isEnabled()
        self.btn_abort.setEnabled(not is_enable)
        if is_abort:
            self.progress_bar.setStyleSheet(
                "QProgressBar:chunk" "{" "background-color : #E3887A;" "}"
            )
        else:
            self.progress_bar.setStyleSheet(
                "QProgressBar:chunk" "{" "background-color:rgb(90, 168, 114);" "}"
            )

    @Slot(int)
    def upload_progress_bar_value(self, progress: int) -> None:
        """
        Обновление значения progress bar

        Args:
            progress - прогресс выполнения
        """
        self.progress_bar.setValue(progress)

    @Slot()
    def inform_about_end_processing(self) -> None:
        """Информирование пользователя о конце обработки"""

        QMessageBox.information(
            self, "Детекция завершена", "Детекция материалов завершена успешно"
        )
