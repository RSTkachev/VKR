# Импорт библиотек
import os

from PySide6.QtWidgets import QWidget, QFileDialog, QPushButton, QGridLayout, QProgressBar,\
    QLabel, QComboBox, QLineEdit, QDoubleSpinBox, QCheckBox, QMessageBox
from PySide6.QtGui import QIcon, Qt
from PySide6.QtCore import QThread, Signal, Slot
from torch.cuda import device_count, get_device_name

from detection_worker import DetectionWorker


# Класс окна интерфейса
class DetectionWidget(QWidget):
    # Сигналы потоку-обработчику
    load_model_signal = Signal()
    prediction_signal = Signal(str, str, str, float, Qt.CheckState, Qt.CheckState, Qt.CheckState)

    def __init__(self):
        super().__init__()

        # Определение обработчика
        self.worker = DetectionWorker()
        self.worker_thread = QThread()
        self.worker.set_enable_state.connect(self.upload_btn_set_enable_state)
        self.worker.set_progress_bar_value.connect(self.upload_progress_bar_value)
        self.load_model_signal.connect(self.worker.load_model)
        self.prediction_signal.connect(self.worker.make_prediction)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()
        self.load_model_signal.emit()

        # Элементы окна
        self.btn_upload = QPushButton()
        self.btn_upload.setText('Обработать')
        self.btn_upload.clicked.connect(self.process)
        self.btn_upload.setObjectName(u"btn_upload")
        self.btn_upload.setMaximumWidth(150)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setVisible(True)

        global_settings = QLabel()
        global_settings.setText('Глобальные настройки')
        global_settings.setObjectName(u"global_settings")

        device_text = QLabel()
        device_text.setObjectName(u"device_text")
        device_text.setText('Устройство обработки')
        device_text.setToolTip('Параметр определяет, на каком устройстве будет производиться детекция')

        dev_cnt = device_count()
        devices = ['CPU']
        for device_index in range(dev_cnt):
            devices.append(get_device_name(device_index))

        self.device_list = QComboBox()
        for device in devices:
            self.device_list.addItem(device)

        loading_text = QLabel()
        loading_text.setObjectName(u"loading_text")
        loading_text.setText('Директория загрузки')
        device_text.setToolTip('Параметр определяет расположение файлов для детекции')

        self.loading_path = QLineEdit()

        self.loading_button = QPushButton()
        self.loading_button.setText('')
        self.loading_button.setIcon(QIcon('resources/icons/folder.svg'))
        self.loading_button.setObjectName(u"loading_button")
        self.loading_button.clicked.connect(self.chose_load_directory)

        saving_text = QLabel()
        saving_text.setObjectName(u"saving_text")
        saving_text.setText('Директория сохранения')
        saving_text.setToolTip('Параметр определяет директорию сохранения')

        self.saving_path = QLineEdit()

        self.saving_button = QPushButton()
        self.saving_button.setText('')
        self.saving_button.setIcon(QIcon('resources/icons/folder.svg'))
        self.saving_button.setObjectName(u"saving_button")
        self.saving_button.clicked.connect(self.chose_save_directory)

        confidence_threshold = QLabel()
        confidence_threshold.setObjectName(u"confidence_threshold")
        confidence_threshold.setText('Порог уверенности')
        confidence_threshold.setToolTip('Параметр определяет степень уверенности, с которой принимается детекция')

        self.confidence_value = QDoubleSpinBox()
        self.confidence_value.setValue(0.5)
        self.confidence_value.setMinimum(0)
        self.confidence_value.setMaximum(1)
        self.confidence_value.setSingleStep(0.05)

        saving_settings = QLabel()
        saving_settings.setObjectName(u"saving_settings")
        saving_settings.setText('Настройки сохранения')

        self.save_images = QCheckBox()
        self.save_images.setCheckState(Qt.CheckState.Checked)

        save_images_text = QLabel()
        save_images_text.setText('Сохранять обработанные изображения')
        save_images_text.setObjectName(u"save_image_text")
        save_images_text.setToolTip('Параметр определяет, необходимо ли сохранять обработанные изображения. Требует указания директории сохранения')

        self.save_statistic = QCheckBox()
        self.save_statistic.setCheckState(Qt.CheckState.Checked)

        save_statistic_text = QLabel()
        save_statistic_text.setText('Сохранять статистику')
        save_statistic_text.setObjectName(u"save_statistic_text")
        save_statistic_text.setToolTip('Параметр определяет, необходимо ли сохранять сохранять статистику по детекциям. Требует указания директории сохранения')

        self.group_images = QCheckBox()
        self.group_images.setCheckState(Qt.CheckState.Checked)

        group_images_text = QLabel()
        group_images_text.setText('Группировать изображения')
        group_images_text.setObjectName(u"group_images_text")
        group_images_text.setToolTip('Параметр определяет, необходимо ли группировать изображения по классам. Требует указания директории сохранения')

        # Определение и настройка шаблона
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.setContentsMargins(40, 40, 40, 40)

        layout.addWidget(global_settings, 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(device_text, 1, 0, 1, 1,  Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.device_list, 1, 1, 1, 1,  Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(loading_text, 2, 0, 1, 1,  Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.loading_path, 2, 1, 1, 1,  Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.loading_button, 2, 2, 1, 1, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(saving_text, 3, 0, 1, 1,  Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.saving_path, 3, 1, 1, 1,  Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.saving_button, 3, 2, 1, 1, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(confidence_threshold, 4, 0, 1, 1,  Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.confidence_value, 4, 1, 1, 1, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(saving_settings, 0, 3, 1, 2, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.save_images, 1, 3, 1, 1, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        layout.addWidget(save_images_text, 1, 4, 1, 1,  Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.save_statistic, 2, 3, 1, 1, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        layout.addWidget(save_statistic_text, 2, 4, 1, 1,  Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.group_images, 3, 3, 1, 1, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        layout.addWidget(group_images_text, 3, 4, 1, 1,  Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(self.btn_upload, 6, 0, 1, 1,  Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.progress_bar, 6, 1, 1, 4,  Qt.AlignmentFlag.AlignVCenter)

        layout.setContentsMargins(40, 40, 60, 60)
        layout.setVerticalSpacing(20)
        layout.setHorizontalSpacing(10)

        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 1)
        layout.setColumnStretch(4, 4)

        self.setLayout(layout)

    # Установка директории-источника
    def chose_load_directory(self):
        directory = QFileDialog.getExistingDirectory()
        self.loading_path.setText(directory)

    # Установка директории-назначения
    def chose_save_directory(self):
        directory = QFileDialog.getExistingDirectory()
        self.saving_path.setText(directory)

    # Запуск обработки
    def process(self):
        device = self.device_list.currentText()
        source = self.loading_path.text()
        destination = self.saving_path.text()
        confidence = self.confidence_value.value()
        save_image = self.save_images.checkState()
        save_statistic = self.save_statistic.checkState()
        group_images = self.group_images.checkState()
        if not source:
            dialog = QMessageBox(self)
            dialog.warning(self, 'Обработка невозможна!', 'Пожалуйста, введите источник', QMessageBox.StandardButton.Ok)
            return
        if not os.path.isdir(source):
            dialog = QMessageBox(self)
            dialog.warning(self, 'Обработка невозможна!', 'Источник некорректен', QMessageBox.StandardButton.Ok)
            return
        if not destination and save_image == Qt.CheckState.Checked:
            dialog = QMessageBox(self)
            dialog.warning(self, 'Обработка невозможна!', 'Пожалуйста, введите путь сохранения', QMessageBox.StandardButton.Ok)
            return
        if destination and not os.path.isdir(destination):
            dialog = QMessageBox(self)
            dialog.warning(self, 'Обработка невозможна!', 'Путь сохранения некорректен', QMessageBox.StandardButton.Ok)
            return

        self.prediction_signal.emit(device, source, destination, confidence, save_image, save_statistic, group_images)

    # Блокировка кнопки обработки
    @Slot()
    def upload_btn_set_enable_state(self):
        is_enable = self.btn_upload.isEnabled()
        self.btn_upload.setEnabled(not is_enable)

    # Обновление значения progress bar
    @Slot(int)
    def upload_progress_bar_value(self, progress):
        self.progress_bar.setValue(progress)
