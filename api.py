import os
import cv2
import ultralytics
from tkinter import filedialog as fd
from threading import Thread
from queue import Queue
from statistic import Statistic
from pathlib import Path


def load_model() -> ultralytics.YOLO:
    return ultralytics.YOLO('model_ru.pt', verbose=False)


def make_prediction(model, queue_predict: Queue) -> None:
    while True:
        pocket = queue_predict.get()
        if pocket:
            for image in pocket:
                prediction = model.predict(image, verbose=False)


        else:
            break


def show_prediction(queue_show: Queue) -> None:
    while True:
        image = queue_show.get()
        if image:
            cv2.imshow('image', image.plot())
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            break


def save_prediction(queue_save: Queue) -> None:
    save_path: str = ''
    sort = False
    classes = {}
    statistic_result: Statistic = None
    while True:
        image = queue_save.get()
        if image:
            if image['path'] != save_path:
                if statistic_result:
                    statistic_result.save_statistic(save_path)
                if sort:
                    for class_name in classes.values():
                        if len(os.listdir(f'{save_path}/{class_name}')) == 0:
                            os.rmdir(f'{save_path}/{class_name}')
                save_path = image['path']
                statistic_result = Statistic(image['prediction'].names)
                sort = image['sort']
                if sort:
                    classes = image['prediction'].names
                    for class_name in classes.values():
                        Path(f'{save_path}/{class_name}').mkdir(parents=True, exist_ok=True)
            detected_objects = set(image['prediction'].boxes.cls.tolist())
            filename = image['prediction'].path.split('\\')[-1]
            if sort and image['save_image']:
                if len(detected_objects):
                    for detected_object in detected_objects:
                        image['prediction'].save(f'{save_path}/{classes[detected_object]}/{filename}')
                elif not image['only_detection']:
                    image['prediction'].save(f'{save_path}/empty/{filename}')
            elif image['save_image']:
                image['prediction'].save(f'{save_path}/{filename}')
            if statistic_result:
                statistic_result.add_prediction_result(image['prediction'].path, detected_objects)

        else:
            if statistic_result:
                statistic_result.save_statistic(save_path)
            if sort:
                for class_name in classes.values():
                    if len(os.listdir(f'{save_path}/{class_name}')) == 0:
                        os.rmdir(f'{save_path}/{class_name}')
            break


if __name__ == "__main__":
    queue_to_predict = Queue(100)
    queue_to_show = Queue(100)
    queue_to_save = Queue(100)

    prediction_thread = Thread(
        target=make_prediction,
        args=[
            queue_to_predict,
            queue_to_show,
            queue_to_save
        ]
    )

    show_thread = Thread(
        target=show_prediction,
        args=[
            queue_to_show
        ]
    )

    save_thread = Thread(
        target=save_prediction,
        args=[
            queue_to_save
        ]
    )
    prediction_thread.start()
    show_thread.start()
    save_thread.start()

    path = get_directory()
    path_to_save = get_directory()

    queue_to_predict.put(
        {
            'path': path,
            'show': False,
            'only_detection': True,
            'classes': False,
            'path_save': path_to_save,
            'sort': True,
            'save_stats': True
        }
    )

    queue_to_predict.put(None)
    prediction_thread.join()
    show_thread.join()
    save_thread.join()
