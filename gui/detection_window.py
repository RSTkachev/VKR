import ultralytics
from PySide6.QtWidgets import QWidget, QFileDialog, QPushButton, QGridLayout, QProgressBar
from PySide6.QtGui import QIcon
from PySide6.QtCore import QThread, Signal, Slot
from queue import Queue


class DetectionWidget(QWidget):
    load_model_signal = Signal()
    prediction_signal = Signal(list)

    def __init__(self):
        super().__init__()
        self.btn_upload = QPushButton()
        self.btn_upload.setIcon(QIcon('./resources/icons/upload.svg'))
        self.btn_upload.setText('Обработать')
        self.btn_upload.clicked.connect(self.open_directory)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)

        self.worker = DetectionWorker()
        self.worker_thread = QThread()
        self.worker.set_enable_state.connect(self.upload_btn_set_enable_state)
        self.worker.set_progress_bar_value.connect(self.upload_progress_bar_value)
        self.load_model_signal.connect(self.worker.load_model)
        self.prediction_signal.connect(self.worker.make_prediction)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()
        self.load_model_signal.emit()

        layout = QGridLayout()
        layout.addWidget(self.btn_upload, 0, 0, 1, 1)
        layout.addWidget(self.progress_bar, 1, 0, 1, 1)
        self.setLayout(layout)

    def open_directory(self):
        paths = QFileDialog.getOpenFileNames()[0]
        if paths:
            self.prediction_signal.emit(paths)

    @Slot()
    def upload_btn_set_enable_state(self):
        is_enable = self.btn_upload.isEnabled()
        self.btn_upload.setEnabled(not is_enable)

    @Slot(int)
    def upload_progress_bar_value(self, progress):
        self.progress_bar.setValue(progress)


class DetectionWorker(QThread):
    set_enable_state = Signal()
    set_progress_bar_value = Signal(int)
    is_working = True

    @Slot()
    def load_model(self):
        print(QThread.currentThread())
        self.model = ultralytics.YOLO('./resources/model_ru.pt', verbose=False)

    @Slot(list)
    def make_prediction(self, paths):
        print(QThread.currentThread())
        self.set_progress_bar_value.emit(0)
        self.set_enable_state.emit()
        count = len(paths)
        for index in range(0, count):
            prediction = self.model.predict(paths[index], verbose=False, stream=True)
            for image in prediction:
                if not self.is_working:
                    return None
            progress = int((index + 1) / count * 100)
            self.set_progress_bar_value.emit(progress)
        self.set_enable_state.emit()
