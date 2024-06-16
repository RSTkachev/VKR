from PySide6.QtCore import Signal, Slot, QThread
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QMessageBox

from gui.statistic_window_ui import StatisticWindowUi
from processing.plot_creator import PlotCreator


class StatisticWidget(StatisticWindowUi):
    """Страница статистики"""

    # Переменные для хранения данных для реализации графов

    __thread_load_statistic = Signal()
    __thread_previous_chart = Signal()
    __thread_next_chart = Signal()
    __thread_clear_statistic = Signal()

    def __init__(self) -> None:
        """Инициализация объекта"""

        super().__init__()

        self._refresh_button.clicked.connect(self.__refresh_detections)
        self._button_previous.clicked.connect(self.__load_previous_chart)
        self._button_next.clicked.connect(self.__load_next_chart)
        self._button_clear.clicked.connect(self.__clear_statistic)

        self.__plotter = PlotCreator()
        self.__worker_thread = QThread()

        self.__thread_load_statistic.connect(self.__plotter.load_statistic)
        self.__thread_previous_chart.connect(self.__plotter.previous_chart)
        self.__thread_next_chart.connect(self.__plotter.next_chart)
        self.__thread_clear_statistic.connect(self.__plotter.clear_statistic)

        self.__plotter.graph_existed.connect(self.__graph_existed)
        self.__plotter.no_graph.connect(self.__no_graph)
        self.__plotter.previous.connect(self.__set_previous_button_state)
        self.__plotter.next.connect(self.__set_next_button_state)
        self.__plotter.plot.connect(self.__set_plot)
        self.__plotter.clear_error.connect(self.__inform_error_deleting)

        self.__worker_thread.start()

        self.__plotter.load_statistic()

    def __load_previous_chart(self) -> None:
        """Переход к предыдущему графу"""

        self.__thread_previous_chart.emit()

    def __load_next_chart(self) -> None:
        """Переход к следующему графу"""

        self.__thread_next_chart.emit()

    def __refresh_detections(self) -> None:
        """Обновление статистики из файла"""

        self.__thread_load_statistic.emit()

    def __clear_statistic(self) -> None:
        """Удаление файла статистики"""

        self.__thread_clear_statistic.emit()

    @Slot(QPixmap)
    def __set_plot(self, pixmap: QPixmap) -> None:
        """Установка графа"""

        self._chart.setPixmap(pixmap)

    @Slot()
    def __graph_existed(self) -> None:
        """Обновление интерфейса. График присутствует"""

        self._chart_text.setVisible(False)
        self._button_clear.setVisible(True)
        self._chart.setVisible(True)

    @Slot()
    def __no_graph(self) -> None:
        """Обновление интерфейса. График отсутствует"""

        self._chart.setVisible(False)
        self._chart_text.setVisible(True)
        self._button_clear.setVisible(False)
        self._button_previous.setVisible(False)
        self._button_next.setVisible(False)

    @Slot(bool)
    def __set_previous_button_state(self, visibility: bool) -> None:
        """
        Обновление видимости кнопки перехода к предыдущему графу

        Args:
            visibility - видимость кнопки
        """

        self._button_previous.setVisible(visibility)

    @Slot(bool)
    def __set_next_button_state(self, visibility: bool) -> None:
        """
        Обновление видимости кнопки перехода к следующему графу

        Args:
            visibility - видимость кнопки
        """

        self._button_next.setVisible(visibility)

    @Slot()
    def __inform_error_deleting(self) -> None:
        """Информирование пользователя об ошибки сброса статистики"""

        dialog = QMessageBox(self)
        dialog.warning(
            self,
            "Статистика используется",
            "Сброс статистики невозможен,так как файл статистики используется",
            QMessageBox.StandardButton.Ok,
        )

    def close_worker(self) -> None:
        """Закрытие потока"""

        self.__worker_thread.quit()
        self.__worker_thread.wait()
