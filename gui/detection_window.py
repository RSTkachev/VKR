# Импорт библиотек
import os
import filetype
import cv2

import ultralytics
from PySide6.QtWidgets import QWidget, QFileDialog, QPushButton, QGridLayout, QProgressBar,\
    QLabel, QComboBox, QLineEdit, QDoubleSpinBox, QCheckBox, QMessageBox
from PySide6.QtGui import QIcon, Qt
from PySide6.QtCore import QThread, Signal, Slot


# Класс окна интерфейса
class DetectionWidget(QWidget):
    # Сигналы потоку-обработчику
    load_model_signal = Signal()
    prediction_signal = Signal(str, str, float, bool, bool, bool)

    def __init__(self):
        super().__init__()

        # Элементы окна
        self.btn_upload = QPushButton()
        self.btn_upload.setText('Обработать')
        self.btn_upload.clicked.connect(self.process)
        self.btn_upload.setObjectName(u"btn_upload")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setVisible(True)

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

        # Задание параметров элемента интерфейса
        global_settings = QLabel()
        global_settings.setText('Глобальные настройки')
        global_settings.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        device_text = QLabel()
        device_text.setText('Устройство обработки')

        self.device_list = QComboBox()
        self.device_list.addItem('cpu')
        self.device_list.addItem('cuda')

        loading_text = QLabel()
        loading_text.setText('Директория загрузки')

        self.loading_path = QLineEdit()

        self.loading_button = QPushButton()
        self.loading_button.setText('')
        self.loading_button.setIcon(QIcon('resources/icons/folder.svg'))
        self.loading_button.clicked.connect(self.chose_load_directory)

        saving_text = QLabel()
        saving_text.setText('Директория сохранения')

        self.saving_path = QLineEdit()

        self.saving_button = QPushButton()
        self.saving_button.setText('')
        self.saving_button.setIcon(QIcon('resources/icons/folder.svg'))
        self.saving_button.clicked.connect(self.chose_save_directory)

        confidence_threshold = QLabel()
        confidence_threshold.setText('Порог уверенности')

        self.confidence_value = QDoubleSpinBox()
        self.confidence_value.setValue(0.5)
        self.confidence_value.setMinimum(0)
        self.confidence_value.setMaximum(1)
        self.confidence_value.setSingleStep(0.05)

        saving_settings = QLabel()
        saving_settings.setText('Настройки сохранения')

        self.save_images = QCheckBox()
        self.save_images.setCheckState(Qt.CheckState.Checked)

        save_images_text = QLabel()
        save_images_text.setText('Сохранять обработанные изображения')

        self.save_statistic = QCheckBox()
        self.save_statistic.setCheckState(Qt.CheckState.Checked)

        save_statistic_text = QLabel()
        save_statistic_text.setText('Сохранять статистику')

        self.group_images = QCheckBox()
        self.group_images.setCheckState(Qt.CheckState.Checked)

        group_images_text = QLabel()
        group_images_text.setText('Группировать изображения')

        # Определение и настройка шаблона
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.setContentsMargins(40, 40, 40, 40)

        layout.addWidget(global_settings, 0, 0, 1, 3)
        layout.addWidget(device_text, 1, 0, 1, 1)
        layout.addWidget(self.device_list, 1, 1, 1, 2)
        layout.addWidget(loading_text, 2, 0, 1, 1)
        layout.addWidget(self.loading_path, 2, 1, 1, 1)
        layout.addWidget(self.loading_button, 2, 2, 1, 1)
        layout.addWidget(saving_text, 3, 0, 1, 1)
        layout.addWidget(self.saving_path, 3, 1, 1, 1)
        layout.addWidget(self.saving_button, 3, 2, 1, 1)
        layout.addWidget(confidence_threshold, 4, 0, 1, 1)
        layout.addWidget(self.confidence_value, 4, 1, 1, 1)

        layout.addWidget(saving_settings, 0, 3, 1, 2, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.save_images, 1, 3, 1, 1)
        layout.addWidget(save_images_text, 1, 4, 1, 1)
        layout.addWidget(self.save_statistic, 2, 3, 1, 1)
        layout.addWidget(save_statistic_text, 2, 4, 1, 1)
        layout.addWidget(self.group_images, 3, 3, 1, 1)
        layout.addWidget(group_images_text, 3, 4, 1, 1)

        layout.addWidget(self.btn_upload, 6, 0, 1, 1)
        layout.addWidget(self.progress_bar, 6, 1, 1, 4)

        layout.setContentsMargins(40, 40, 60, 60)
        layout.setSpacing(10)

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
        source = self.loading_path.text()
        destination = self.saving_path.text()
        confidence = self.confidence_value.value()
        save_image = self.save_images.checkState()
        save_statistic = self.save_statistic.checkState()
        group_images = self.group_images.checkState()
        if not source:
            dialog = QMessageBox(self)
            dialog.information(self, 'Обработка невозможна!', 'Пожалуйста, введите источник', QMessageBox.StandardButton.Ok)
            return
        if not destination and save_image:
            dialog = QMessageBox(self)
            dialog.information(self, 'Обработка невозможна!', 'Пожалуйста, введите источник', QMessageBox.StandardButton.Ok)
            return
        self.prediction_signal(source, destination, confidence, save_image, save_statistic, group_images)


    # Блокировка кнопки обработки
    @Slot()
    def upload_btn_set_enable_state(self):
        is_enable = self.btn_upload.isEnabled()
        self.btn_upload.setEnabled(not is_enable)

    # Обновление значения progress bar
    @Slot(int)
    def upload_progress_bar_value(self, progress):
        self.progress_bar.setValue(progress)


# Класс-обработчик
class DetectionWorker(QThread):
    # Сигналы для изменения интерфейса
    set_enable_state = Signal()
    set_progress_bar_value = Signal(int)
    # Переменная для досрочного завершения обработки
    is_working = True

    # Загрузка модели
    @Slot()
    def load_model(self):
        self.model = ultralytics.YOLO('./resources/model_ru.pt', verbose=False)

    # Обарботка
    @Slot(str, str, float, bool, bool, bool)
    def make_prediction(self, source, destination, confidence, to_save_image, to_save_statistic, to_group_images):
        self.set_progress_bar_value.emit(0)
        self.set_enable_state.emit()
        files = []
        for folder, _, filenames in os.walk(source):
            for filename in filenames:
                if filetype.is_image(f'{folder}\{filename}') or filetype.is_video(f'{folder}\{filename}'):
                    files.append(f'{folder}\{filename}')
        count = len(files)
        for index in range(0, count):
            prediction = self.model.predict(files[index], verbose=False, stream=True)
            if filetype.is_video(files[index]):
                vid = cv2.VideoCapture(files[index])
                height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
                width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
                fps = vid.get(cv2.CAP_PROP_FPS)

                fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                video = cv2.VideoWriter(filename="output.avi", fourcc=fourcc, fps=fps, frameSize=(int(width), int(height)))
                for image in prediction:
                    video.write(image.plot())
                video.release()
            else:
                pass
            progress = int((index + 1) / count * 100)
            self.set_progress_bar_value.emit(progress)
        self.set_enable_state.emit()
