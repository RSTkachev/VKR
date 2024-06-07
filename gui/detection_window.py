from os import path

from PySide6.QtCore import QThread, Signal, Slot
from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QMessageBox,
)
from torch.cuda import device_count, get_device_name

from gui.detection_window_ui import DetectionWidgetUi
from processing.detection_worker import DetectionWorker


class DetectionWidget(DetectionWidgetUi):
    """Страница детектирования"""

    # Сигнал потоку-обработчику
    __load_model = Signal(str)
    __set_device = Signal(str)
    __prediction_signal = Signal(
        str, Qt.CheckState, str, float, Qt.CheckState, Qt.CheckState, Qt.CheckState
    )

    def __init__(self):
        """Инициализация объекта"""

        super().__init__()

        self._btn_process.clicked.connect(self.__process)

        dev_cnt = device_count()
        devices = ["CPU"]
        for device_index in range(dev_cnt):
            devices.append(get_device_name(device_index))

        self._checkbox_draw_bbox.setEnabled(False)
        self._checkbox_group_images.setEnabled(False)

        self._btn_loading_directory.clicked.connect(self.__chose_load_directory)
        self._btn_saving_directory.clicked.connect(self.__chose_save_directory)
        self._checkbox_save_images.stateChanged.connect(
            self.__checkbox_saving_images_state
        )
        self._checkbox_draw_bbox.stateChanged.connect(self.__checkbox_check_state)
        self._checkbox_group_images.stateChanged.connect(self.__checkbox_check_state)
        self._checkbox_save_statistic.stateChanged.connect(
            self.__checkbox_save_statistic_state
        )

        for device in devices:
            self._device_list.addItem(device)

        self._btn_abort.clicked.connect(self.stop_worker)

        # Определение обработчика
        self.__worker = DetectionWorker()
        self.__worker_thread = QThread()
        self.__worker.set_enable_state.connect(self.__btn_process_set_enable_state)
        self.__worker.btn_abort_upload_state.connect(self.__btn_abort_upload_state)
        self.__worker.set_progress_bar_value.connect(self.__upload_progress_bar_value)
        self.__worker.inform_end.connect(self.__inform_about_end_processing)
        self.__load_model.connect(self.__worker.load_model)
        self.__set_device.connect(self.__worker.set_device)
        self.__prediction_signal.connect(self.__worker.make_prediction)
        self.__worker.moveToThread(self.__worker_thread)
        self.__worker_thread.start()
        self.__load_model.emit("./resources/model_ru.pt")

    def __chose_load_directory(self) -> None:
        """Установка директории-источника"""

        directory = QFileDialog.getExistingDirectory()
        self._line_edit_loading_path.setText(directory)

    def __checkbox_saving_images_state(self):
        """Проверка состояния чекбокса сохранения материалов"""

        if self._checkbox_save_images.checkState() == Qt.CheckState.Checked:
            self._checkbox_draw_bbox.setEnabled(True)
            self._checkbox_group_images.setEnabled(True)
            self._checkbox_draw_bbox.setCheckState(Qt.CheckState.Checked)
            self._checkbox_group_images.setCheckState(Qt.CheckState.Checked)
            self._line_edit_saving_path.setEnabled(True)
            self._btn_saving_directory.setEnabled(True)
            self._line_edit_saving_path.setEnabled(True)
            self._btn_saving_directory.setEnabled(True)
        else:
            self._checkbox_draw_bbox.setEnabled(False)
            self._checkbox_group_images.setEnabled(False)
            self._checkbox_draw_bbox.setCheckState(Qt.CheckState.Unchecked)
            self._checkbox_group_images.setCheckState(Qt.CheckState.Unchecked)
            if self._checkbox_save_statistic.checkState() == Qt.CheckState.Unchecked:
                self._line_edit_saving_path.setEnabled(False)
                self._btn_saving_directory.setEnabled(False)

    def __checkbox_check_state(self):
        """Проверка состояния чекбоксов"""

        if (
            self._checkbox_draw_bbox.checkState() == Qt.CheckState.Unchecked
            and self._checkbox_group_images.checkState() == Qt.CheckState.Unchecked
        ):
            self._checkbox_save_images.setCheckState(Qt.CheckState.Unchecked)

    def __checkbox_save_statistic_state(self):
        """Проверка состояния чекбокса сохранения статистики"""

        if self._checkbox_save_statistic.checkState() == Qt.CheckState.Checked:
            self._line_edit_saving_path.setEnabled(True)
            self._btn_saving_directory.setEnabled(True)
        elif self._checkbox_save_images.checkState() == Qt.CheckState.Unchecked:
            self._line_edit_saving_path.setEnabled(False)
            self._btn_saving_directory.setEnabled(False)

    def __chose_save_directory(self):
        """Установка директории-назначения"""

        directory = QFileDialog.getExistingDirectory()
        self._line_edit_saving_path.setText(directory)

    def __process(self):
        """Запуск обработки"""

        device = self._device_list.currentText()
        source = self._line_edit_loading_path.text()
        is_find_subdirectories = self._checkbox_find_subdirectories.checkState()
        destination = self._line_edit_saving_path.text()
        confidence = self._d_spin_box_confidence_value.value()
        draw_bbox = self._checkbox_draw_bbox.checkState()
        save_statistic = self._checkbox_save_statistic.checkState()
        group_images = self._checkbox_group_images.checkState()
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
            draw_bbox == Qt.CheckState.Checked
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

        self.__set_device.emit(device)
        self.__prediction_signal.emit(
            source,
            is_find_subdirectories,
            destination,
            confidence,
            draw_bbox,
            save_statistic,
            group_images,
        )

    def check_worker_state(self):
        """
        Проверка состояния потока

        Return:
            Состояние потока
        """

        return self.__worker.is_working

    def stop_worker(self):
        """Остановка потока"""

        self.__worker.is_working = False

    def close_worker(self):
        """Закрытие потока"""

        self.__worker_thread.quit()
        self.__worker_thread.wait()

    @Slot()
    def __btn_process_set_enable_state(self) -> None:
        """Обновление состояния кнопки загрузки"""

        is_enable = self._btn_process.isEnabled()
        self._btn_process.setEnabled(not is_enable)

    @Slot(bool)
    def __btn_abort_upload_state(self, is_abort: bool) -> None:
        """
        Обновление состояния кнопки аборта детекции

        Args:
            is_abort - была ли нажата кнопка аборта
        """

        is_enable = self._btn_abort.isEnabled()
        self._btn_abort.setEnabled(not is_enable)
        if is_abort:
            self._progress_bar.setStyleSheet(
                "QProgressBar:chunk" "{" "background-color : #E3887A;" "}"
            )
        else:
            self._progress_bar.setStyleSheet(
                "QProgressBar:chunk" "{" "background-color:rgb(90, 168, 114);" "}"
            )

    @Slot(int)
    def __upload_progress_bar_value(self, progress: int) -> None:
        """
        Обновление значения progress bar

        Args:
            progress - прогресс выполнения
        """
        self._progress_bar.setValue(progress)

    @Slot()
    def __inform_about_end_processing(self) -> None:
        """Информирование пользователя о конце обработки"""

        QMessageBox.information(
            self, "Детекция завершена", "Детекция материалов завершена успешно"
        )
