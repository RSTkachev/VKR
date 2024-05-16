# Импорт библиотек
from os import walk
from os.path import exists
from shutil import copy2
from pathlib import Path
from time import strftime, localtime

import filetype
import cv2
import pandas as pd
from torch.cuda import device_count, get_device_name, empty_cache

import ultralytics
from PySide6.QtGui import Qt
from PySide6.QtCore import QThread, Signal, Slot


# Класс-обработчик
class DetectionWorker(QThread):
    # Сигналы для изменения интерфейса
    set_enable_state = Signal()
    set_progress_bar_value = Signal(int)
    # Переменная для досрочного завершения обработки
    is_working = True
    # Файл для сохранения статистики

    # Загрузка модели
    @Slot()
    def load_model(self):
        self.model = ultralytics.YOLO('./resources/model_ru.pt', verbose=False)

    # Обарботка
    @Slot(str, str, str, float, Qt.CheckState, Qt.CheckState, Qt.CheckState)
    def make_prediction(self, device, source, destination, confidence, to_save_image, to_save_statistic, to_group_images):
        # Сигналы для обновления элементов интерфейса
        self.set_progress_bar_value.emit(0)
        self.set_enable_state.emit()

        if exists('statistic.csv'):
            statistic = pd.read_csv('statistic.csv')
        else:
            statistic = pd.DataFrame()

        current_time = localtime()

        dev_cnt = device_count()
        devices = {'CPU': 'cpu'}
        for device_index in range(dev_cnt):
            devices[get_device_name(device_index)] = device_index

        self.model.to(devices[device])
        empty_cache()

        all_classes = self.model.names

        # Количество животных на детекциях
        animal_count = {x: 0 for x in all_classes.keys()}
        cnt_without_detection = 0

        # Список валидных файлов
        files = []
        for folder, _, filenames in walk(source):
            for filename in filenames:
                if filetype.is_image(f'{folder}/{filename}') or filetype.is_video(f'{folder}/{filename}'):
                    files.append(f'{folder}/{filename}')

        # Создание папок для сохранения детектированных изображений
        if to_save_image == Qt.CheckState.Checked:
            Path(f'{destination}/detection').mkdir(parents=True, exist_ok=True)

        # Создание папок для каждого класса животных
        if to_group_images == Qt.CheckState.Checked:
            for class_name in self.model.names.values():
                Path(f'{destination}/detection/{class_name}').mkdir(parents=True, exist_ok=True)

        # Количество файлов. Необходимо для обновления progress bar
        count = len(files)

        for index in range(0, count):
            if not self.is_working:
                return
            # Запуск детекции
            prediction = self.model.predict(files[index], verbose=False, stream=True, conf=confidence)

            # Сет классов животных, присутствующих на материале
            detected_objects = set()

            # Если изначальный объект является видео
            if filetype.is_video(files[index]):

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
                            return
                        detected_objects.update(image.boxes.cls.tolist())
                        video.write(image.plot())
                        video.release()

                elif to_group_images == Qt.CheckState.Checked:
                    copy2(files[index], f"{destination}/detection/{files[index].split('/')[-1]}")

                else:
                    for image in prediction:
                        detected_objects.update(image.boxes.cls.tolist())

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
            else:
                cnt_without_detection += 1

            progress = int((index + 1) / count * 100)
            self.set_progress_bar_value.emit(progress)

        size_of_statistic = statistic.shape[0]
        for key, value in zip(animal_count.keys(), animal_count.values()):
            statistic.loc[size_of_statistic, all_classes[key]] = int(value)
        statistic.loc[size_of_statistic, 'Без детекции'] = int(cnt_without_detection)
        statistic.fillna(0, inplace=True)
        statistic.to_csv('statistic.csv', index=False)

        if to_save_statistic == Qt.CheckState.Checked:
            with open(f'{destination}/detection/statistic.txt', mode='a') as file:
                file.write(f'{strftime("%d-%m-%Y %H:%M:%S", current_time)}\n')
                file.write(f'Обработано {count}\n')
                for key in all_classes:
                    file.write(f'{all_classes[key]}: {animal_count[key]}\n')
        self.set_enable_state.emit()
