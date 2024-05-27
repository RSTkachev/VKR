# Импорт библиотек
from os import walk
from os.path import exists
from shutil import copy2
from pathlib import Path

from filetype import is_image, is_video
import cv2
import pandas as pd
from torch.cuda import device_count, get_device_name, empty_cache

from ultralytics import YOLO
from PySide6.QtGui import Qt
from PySide6.QtCore import QThread, Signal, Slot


# Класс-обработчик
class DetectionWorker(QThread):
    # Модель детектора
    model = None

    # Сигналы для изменения интерфейса
    set_enable_state = Signal()
    set_abort_button_state = Signal(bool)
    set_progress_bar_value = Signal(int)
    inform_end = Signal()

    # Переменная для досрочного завершения обработки
    is_working = False

    # Обарботка
    @Slot(str, str, str, float, Qt.CheckState, Qt.CheckState, Qt.CheckState)
    def make_prediction(self, device, source, destination, confidence, to_save_image, to_save_statistic, to_group_images):
        self.is_working = True
        # Сигналы для обновления элементов интерфейса
        self.set_progress_bar_value.emit(0)
        self.set_enable_state.emit()
        self.set_abort_button_state.emit(False)

        if not self.model:
            self.model = YOLO('../resources/model_ru.pt', verbose=False)

        dev_cnt = device_count()
        devices = {'CPU': 'cpu'}
        for device_index in range(dev_cnt):
            devices[get_device_name(device_index)] = device_index

        self.model.to(devices[device])
        empty_cache()

        all_classes = self.model.names

        # Количество животных на детекциях
        animal_count = {x: 0 for x in all_classes.keys()}

        columns = ['full_path', 'filename']
        for class_name in all_classes.values():
            columns.append(class_name)
        cnt_without_detection = 0

        if exists(f'{destination}/detection/statistic.csv'):
            full_statistic = pd.read_csv(f'{destination}/detection/statistic.csv')
        else:
            full_statistic = pd.DataFrame(columns=columns)

        statistic_size = full_statistic.shape[0]

        # Список валидных файлов
        files = []
        for folder, _, filenames in walk(source):
            for filename in filenames:
                if is_image(f'{folder}/{filename}') or is_video(f'{folder}/{filename}'):
                    files.append(f'{folder}/{filename}')

        # Создание папок для сохранения детектированных изображений
        if to_save_image == Qt.CheckState.Checked or to_save_statistic == Qt.CheckState.Checked:
            Path(f'{destination}/detection').mkdir(parents=True, exist_ok=True)

        # Создание папок для каждого класса животных
        if to_group_images == Qt.CheckState.Checked:
            for class_name in self.model.names.values():
                Path(f'{destination}/detection/{class_name}').mkdir(parents=True, exist_ok=True)

        # Количество файлов. Необходимо для обновления progress bar
        count = len(files)

        for index in range(0, count):
            full_statistic.loc[index + statistic_size, 'full_path'] = files[index]
            full_statistic.loc[index + statistic_size, 'filename'] = files[index].split('/')[-1]
            if not self.is_working:
                self.set_enable_state.emit()
                self.set_abort_button_state.emit(True)
                return
            # Запуск детекции
            prediction = self.model.predict(files[index], verbose=False, stream=True, conf=confidence)

            # Сет классов животных, присутствующих на материале
            detected_objects = set()

            # Если изначальный объект является видео
            if is_video(files[index]):

                # Если необходимо сохранить видео
                if to_save_image == Qt.CheckState.Checked:
                    vid = cv2.VideoCapture(files[index])
                    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
                    fps = vid.get(cv2.CAP_PROP_FPS)

                    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                    video = cv2.VideoWriter(
                        filename=f"{destination}/detection/{files[index]}",
                        fourcc=fourcc,
                        fps=fps,
                        frameSize=(int(width), int(height)),
                    )

                    for image in prediction:
                        if not self.is_working:
                            self.set_enable_state.emit()
                            self.set_abort_button_state.emit(True)
                            return
                        detected_objects.update(image.boxes.cls.tolist())
                        video.write(image.plot())
                        video.release()

                else:
                    for image in prediction:
                        detected_objects.update(image.boxes.cls.tolist())
                        if not self.is_working:
                            self.set_enable_state.emit()
                            self.set_abort_button_state.emit(True)
                            return
                    if to_group_images == Qt.CheckState.Checked:
                        copy2(files[index], f"{destination}/detection/{files[index].split('/')[-1]}")

            else:
                image = prediction.__next__()
                detected_objects.update(item for item in image.boxes.cls.tolist())

                if to_group_images == Qt.CheckState.Checked:
                    if to_save_image == Qt.CheckState.Checked:
                        for index_class in detected_objects:
                            image.save(f'{destination}/detection/{all_classes[index_class]}/{files[index].split("/")[-1]}')

                    else:
                        for index_class in detected_objects:
                            copy2(files[index], f'{destination}/detection/{all_classes[index_class]}')

                elif to_save_image == Qt.CheckState.Checked:
                    image.save(f'{destination}/detection/{files[index].split("/")[-1]}')

            if len(detected_objects) > 0:
                for detected_object in detected_objects:
                    animal_count[detected_object] += 1
                    full_statistic.loc[index + statistic_size, self.model.names[detected_object]] = 1
            else:
                cnt_without_detection += 1

            progress = int((index + 1) / count * 100)
            self.set_progress_bar_value.emit(progress)

        self.save_internal_statistic(animal_count, all_classes, cnt_without_detection)

        if to_save_statistic == Qt.CheckState.Checked:
            full_statistic.to_csv(f'{destination}/detection/statistic.csv', index=False)

        self.set_enable_state.emit()
        self.set_abort_button_state.emit(False)
        self.inform_end.emit()
        self.is_working = False

    def save_internal_statistic(self, counts: dict, names: list, without_detection: int):
        if exists('./resources/statistic.csv'):
            statistic = pd.read_csv('./resources/statistic.csv')
        else:
            statistic = pd.DataFrame()

        size_of_statistic = statistic.shape[0]
        for key, value in zip(counts.keys(), counts.values()):
            statistic.loc[size_of_statistic, names[key]] = value
        statistic.loc[size_of_statistic, 'Без детекции'] = without_detection
        statistic.fillna(0, inplace=True)
        statistic.to_csv('./resources/statistic.csv', index=False)
