# Импорт библиотек
import os
import shutil
from time import strftime, localtime

import filetype
import cv2
from pathlib import Path

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

    # Загрузка модели
    @Slot()
    def load_model(self):
        self.model = ultralytics.YOLO('./resources/model_ru.pt', verbose=False)

    # Обарботка
    @Slot(str, str, float, Qt.CheckState, Qt.CheckState, Qt.CheckState)
    def make_prediction(self, source, destination, confidence, to_save_image, to_save_statistic, to_group_images):
        current_time = localtime()
        # Сигналы для обновления элементов интерфейса
        self.set_progress_bar_value.emit(0)
        self.set_enable_state.emit()

        all_classes = self.model.names

        # Количество животных на детекциях
        animal_count = {x: 0 for x in all_classes.keys()}

        # Список валидных файлов
        files = []
        for folder, _, filenames in os.walk(source):
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
                        frameSize=(int(width), int(height))
                    )

                    for image in prediction:
                        if not self.is_working:
                            return
                        detected_objects.update(image.boxes.cls.tolist())
                        video.write(image.plot())
                        video.release()

                elif to_group_images == Qt.CheckState.Checked:
                    shutil.copy2(files[index], f"{destination}/detection/{files[index].split('/')[-1]}")

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
                            image.copy2(files[index], f'{destination}/detection/{all_classes[index_class]}/{files[index].split("/")[-1]}')

                elif to_save_image == Qt.CheckState.Checked:
                    image.save(f'{destination}/detection/{files[index].split("/")[-1]}')

            for detected_object in detected_objects:
                animal_count[detected_object] += 1

            progress = int((index + 1) / count * 100)
            self.set_progress_bar_value.emit(progress)

        if to_save_statistic == Qt.CheckState.Checked:
            with open(f'{destination}/statistic.txt', 'а') as file:
                file.write(f'{strftime("%d-%m-%Y %H:%M:%S", current_time)}')
                file.write(f'Обработано {count}')
                for key in all_classes:
                    file.write(f'{all_classes[key]}: {animal_count[key]}\n')
        self.set_enable_state.emit()
