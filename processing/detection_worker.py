from os import walk, listdir, remove
from os.path import exists
from pathlib import Path
from shutil import copy2
from typing import Iterator

import cv2
import pandas as pd
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import Qt
from torch.cuda import device_count, get_device_name, empty_cache
from ultralytics import YOLO
from ultralytics.data.utils import IMG_FORMATS, VID_FORMATS
from ultralytics.engine.results import Results


class DetectionWorker(QObject):
    """Класс детектора"""

    # Модель детектора
    __model = None

    # Сигналы для изменения интерфейса
    set_enable_state = Signal()
    btn_abort_upload_state = Signal(bool)
    set_progress_bar_value = Signal(int)
    inform_end = Signal()

    # Переменная для досрочного завершения обработки
    is_working = False

    # Индексы и названия классов детекции
    __classes = None
    __class_indexes = None
    __class_names = None

    @Slot(str)
    def load_model(self, model_name: str) -> None:
        """
        Загрузка детектора.

        Args:
            model_name - название файла модели
        """

        if not self.__model:
            self.__model = YOLO(model_name, verbose=False)

        # Индексы и названия классов детекции
        self.__classes = self.__model.names
        self.__class_indexes = self.__model.names.keys()
        self.__class_names = self.__model.names.values()

    @Slot(str)
    def set_device(self, device: str) -> None:
        """
        Установка девайса обработки

        Args:
            device - строка, кодирующая устройство
        """

        # Количество устройств с поддержкой CUDA
        dev_cnt = device_count()

        # Словарь устройств
        devices = {"CPU": "cpu"}
        # Заполнение словаря устройств устройствами с поддержкой CUDA
        for device_index in range(dev_cnt):
            devices[get_device_name(device_index)] = device_index

        # Перенос модели на устройство выполнения детекции
        self.__model.to(devices[device])
        # Очистка памяти, занимаемой моделью
        empty_cache()

    @Slot(str, Qt.CheckState, str, float, Qt.CheckState, Qt.CheckState, Qt.CheckState)
    def make_prediction(
        self,
        source: str,
        is_find_subdirectories: Qt.CheckState,
        destination: str,
        confidence: float,
        to_save_image: Qt.CheckState,
        to_save_statistic: Qt.CheckState,
        to_group_images: Qt.CheckState,
    ) -> None:
        """
        Выполнение детекции

        Args:
            source - путь до директории с материалами
            is_find_subdirectories - искать материалы для детекции в подкаталогах
            destination - путь до директории сохранения
            confidence - порог уверенности
            to_save_image - выполнять ли сохранение материалов с отметками детекций
            to_save_statistic - выполнять сохранение внешней статистики в выбранную пользователем директорию
            to_group_image - группировать изображения по классам обнаруженных животных
        """

        # Установка переменной досрочного завершения
        self.is_working = True

        # Изменение состояния графического интерфейса
        self.set_progress_bar_value.emit(0)
        self.set_enable_state.emit()
        self.btn_abort_upload_state.emit(False)

        # Количество животных на детекциях
        animal_count = {x: 0 for x in self.__class_indexes}

        # Названия колонок статистики
        columns = ["full_path", "filename"].extend(self.__class_names)

        # Количество изображений без детекции
        cnt_without_detection = 0

        # Если файл статистики существует, дополнить
        # Если файл статистики отсутствует, создать
        if exists(f"{destination}/detection/statistic.csv"):
            full_statistic = pd.read_csv(f"{destination}/detection/statistic.csv")
        else:
            full_statistic = pd.DataFrame(columns=columns)

        # Количество строк статистики для дополнения статистики новыми значениями
        statistic_size = full_statistic.shape[0]

        # Список файлов, являющихся изображениями или видеоматериалами
        files = self.__get_files(source, is_find_subdirectories)

        # Создание папки для сохранения материалов детекции
        if (
            to_save_image == Qt.CheckState.Checked
            or to_save_statistic == Qt.CheckState.Checked
        ):
            Path(f"{destination}/detection").mkdir(parents=True, exist_ok=True)

        # Создание папок для каждого класса животных
        if to_group_images == Qt.CheckState.Checked:
            for class_name in self.__class_names:
                Path(f"{destination}/detection/{class_name}").mkdir(
                    parents=True, exist_ok=True
                )

        # Количество файлов. Необходимо для обновления progress bar
        amount = len(files)
        current_number = 0

        for file in files:
            # Сохранение в файл статистики полного пути и названия файла
            full_statistic.loc[statistic_size + current_number, "full_path"] = file
            full_statistic.loc[statistic_size + current_number, "filename"] = (
                file.split("/")[-1]
            )

            # Досрочное завершение
            if not self.is_working:
                self.shut_down()
                return

            # Запуск детекции
            prediction = self.__model.predict(
                file, verbose=False, stream=True, conf=confidence
            )

            # Животные, обнаруженные на материале
            detected_objects = set()

            # Детекция изображения
            if file.split(".")[-1] in IMG_FORMATS:
                self.__process_image(
                    prediction.__next__(),
                    file,
                    destination,
                    to_save_image,
                    to_group_images,
                    self.__classes,
                    detected_objects,
                )

            # Детекция видео
            else:
                self.__process_video(
                    prediction,
                    file,
                    destination,
                    to_save_image,
                    to_group_images,
                    detected_objects,
                )

            # Запись статистики
            if detected_objects:
                for detected_object in detected_objects:
                    animal_count[detected_object] += 1
                    full_statistic.loc[
                        statistic_size + current_number,
                        self.__classes[detected_object],
                    ] = 1
            else:
                cnt_without_detection += 1

            # Обновление progress bar
            progress = int((current_number + 1) / amount * 100)
            self.set_progress_bar_value.emit(progress)
            current_number += 1

        # Сохранение внутренней статистики
        self.__save_internal_statistic(
            animal_count, self.__classes, cnt_without_detection
        )

        # Сохранение внешней статистики
        if to_save_statistic == Qt.CheckState.Checked:
            try:
                full_statistic.to_csv(
                    f"{destination}/detection/statistic.csv", index=False
                )
            except PermissionError:
                pass

        # Обновление графического интерфейса, завершение работы
        self.set_enable_state.emit()
        self.btn_abort_upload_state.emit(False)
        self.inform_end.emit()
        self.is_working = False

    def __get_files(self, source: str, is_find_subdirectories: Qt.CheckState) -> list:
        """
        Функция получения файлов для детекции

        Args:
            source - источник
            is_find_subdirectories - флаг поиска в подкаталогах

        return:
            files - лист файлов для детекции
        """

        files = []
        if is_find_subdirectories == Qt.CheckState.Checked:
            for folder, _, filenames in walk(source):
                for filename in filenames:
                    filename_splitted = filename.split(".")
                    if len(filename_splitted) < 2:
                        pass
                    elif (
                        filename_splitted[-1].lower() in IMG_FORMATS
                        or filename_splitted[-1].lower() in VID_FORMATS
                    ):
                        files.append(f"{folder}/{filename}")
        else:
            for filename in listdir(source):
                filename_splitted = filename.split(".")
                if len(filename_splitted) < 2:
                    pass
                elif (
                    filename_splitted[-1].lower() in IMG_FORMATS
                    or filename_splitted[-1].lower() in VID_FORMATS
                ):
                    files.append(f"{source}/{filename}")
        return files

    def __process_video(
        self,
        prediction: Iterator,
        file: str,
        destination: str,
        to_save_image: Qt.CheckState,
        to_group_images: Qt.CheckState,
        detected_objects: set,
    ) -> None:
        """
        Выполнение детекции видео

        Args:
            prediction - итератор для детекции видео
            file - имя файла
            destination - директория сохранения
            to_save_image - выполнять ли сохранение материалов с отметками детекций
            to_group_image - группировать изображения по классам обнаруженных животных
            detected_objects - обнаруженные объекты
        """

        # Если необходимо сохранить видео
        if to_save_image == Qt.CheckState.Checked:
            # Получение исходных характеристик видео
            vid = cv2.VideoCapture(file)
            height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
            width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
            fps = vid.get(cv2.CAP_PROP_FPS)

            # Создание объекта для записи видео
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            video = cv2.VideoWriter(
                filename=f"{destination}/detection/{'.'.join(file.split('/')[-1].split('.')[:-1])}.avi",
                fourcc=fourcc,
                fps=fps,
                frameSize=(int(width), int(height)),
            )

            # Детекция кадра видео
            for image in prediction:
                # Досрочное завершение
                if not self.is_working:
                    video.release()
                    if len(detected_objects) == 0:
                        try:
                            remove(
                                f"{destination}/detection/{'.'.join(file.split('/')[-1].split('.')[:-1])}.avi"
                            )
                        except PermissionError:
                            pass

                    self.shut_down()
                    return
                # Добавление обнаруженных объектов
                detected_objects.update(image.boxes.cls.tolist())
                # Запись текущего кадра
                video.write(image.plot())

            # Сохранение видео
            video.release()
            detected_objects.clear()

            if len(detected_objects) == 0:
                try:
                    remove(
                        f"{destination}/detection/{'.'.join(file.split('/')[-1].split('.')[:-1])}.avi"
                    )
                except PermissionError:
                    pass

        else:
            # Детекция кадра видео
            for image in prediction:
                # Добавление обнаруженных объектов
                detected_objects.update(image.boxes.cls.tolist())
                # Досрочное завершение
                if not self.is_working:
                    self.shut_down()
                    return
            # Копирование исходного видео
            if to_group_images == Qt.CheckState.Checked and len(detected_objects) > 0:
                try:
                    copy2(file, f"{destination}/detection/{file.split('/')[-1]}")
                except PermissionError:
                    pass

    def __process_image(
        self,
        image: Results,
        file: str,
        destination: str,
        to_save_image: Qt.CheckState,
        to_group_images: Qt.CheckState,
        all_classes: dict,
        detected_objects: set,
    ) -> None:
        """
        Выполнение детекции изображения

        Args:
            image - результаты детекции
            file - имя файла
            destination - директория сохранения
            to_save_image - выполнять ли сохранение материалов с отметками детекций
            to_group_image - группировать изображения по классам обнаруженных животных
            all_classes - детектируемые классы
            detected_objects - обнаруженные объекты
        """

        # Добавление обнаруженных объектов
        detected_objects.update(item for item in image.boxes.cls.tolist())

        # Сохранение с группировкой
        if to_group_images == Qt.CheckState.Checked:
            # Сохранение результата
            if to_save_image == Qt.CheckState.Checked:
                for index_class in detected_objects:
                    try:
                        image.save(
                            f'{destination}/detection/{all_classes[index_class]}/{file.split("/")[-1]}'
                        )
                    except PermissionError:
                        pass

            # Сохранение исходного изображения
            else:
                for index_class in detected_objects:
                    try:
                        copy2(
                            file, f"{destination}/detection/{all_classes[index_class]}"
                        )
                    except PermissionError:
                        pass

        # Сохранение результата без группировки
        elif to_save_image == Qt.CheckState.Checked:
            try:
                image.save(f'{destination}/detection/{file.split("/")[-1]}')
            except PermissionError:
                pass

    def __save_internal_statistic(
        self, counts: dict, names: list, without_detection: int
    ) -> None:
        """
        Сохранение внутренней статистики

        Args:
            counts - количество животных каждого класса
            names - классы, детектируемые моделью
            without_detection - количество изображений без детекции
        """

        # Создание новой статистики или чтение существующей
        if exists("./resources/statistic.csv"):
            statistic = pd.read_csv("./resources/statistic.csv")
        else:
            statistic = pd.DataFrame()

        # Размер статистики. Необходимо для дополнения статистики
        size_of_statistic = statistic.shape[0]
        # Запись количества животных каждого класса
        for key, value in zip(counts.keys(), counts.values()):
            statistic.loc[size_of_statistic, names[key]] = value
        # Запись количества изображений без детекции
        statistic.loc[size_of_statistic, "Без детекции"] = without_detection
        # Заполнение пропусков нулями
        statistic.fillna(0, inplace=True)
        # Сохранение статистики в файл
        try:
            statistic.to_csv("./resources/statistic.csv", index=False)
        except PermissionError:
            pass

    def shut_down(self) -> None:
        """Обновление графического интерфеса по завершении работы"""

        self.set_enable_state.emit()
        self.btn_abort_upload_state.emit(True)
