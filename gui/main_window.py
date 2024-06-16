from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QCloseEvent, QPixmap
from PySide6.QtWidgets import QListWidgetItem, QMessageBox

import resources.strings
from gui.detection_window import DetectionWidget
from gui.info_window import InfoWidget
from gui.main_window_ui import UiMainWindow
from gui.statistic_window import StatisticWidget


class MainWindow(UiMainWindow):
    """Класс основного окна"""

    def __init__(self) -> None:
        super().__init__()

        # Инициализация контейнера для UI

        self._title_icon.setPixmap(QPixmap(resources.strings.label_path))
        self._title_label.setText(resources.strings.app_name_short)
        self._menu_btn.setIcon(QIcon("./resources/icons/menu.svg"))

        self._title_label.hide()

        self._title_icon.hide()

        self._side_menu.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._side_menu.hide()
        self._side_menu_collapsed.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self._menu_btn.setCheckable(True)
        self._menu_btn.setChecked(True)

        # Страницы приложения
        self.__menu_list = [
            {
                "name": "Главная страница",
                "icon": "./resources/icons/camera.svg",
                "widget": DetectionWidget(),
            },
            {
                "name": "Статистика",
                "icon": "./resources/icons/clock.svg",
                "widget": StatisticWidget(),
            },
            {
                "name": "Информация",
                "icon": "./resources/icons/info.svg",
                "widget": InfoWidget(),
            },
        ]

        self.__init_side_menu()
        self.__init_main_content()
        self.__init_single_slot()

    def __init_single_slot(self) -> None:
        """Настройка бокового меню"""

        self._menu_btn.toggled["bool"].connect(self._side_menu.setHidden)
        self._menu_btn.toggled["bool"].connect(self._title_label.setHidden)
        self._menu_btn.toggled["bool"].connect(self._side_menu_collapsed.setVisible)
        self._menu_btn.toggled["bool"].connect(self._title_icon.setHidden)

        self._side_menu_collapsed.currentRowChanged["int"].connect(
            self._side_menu.setCurrentRow
        )

        self._side_menu.currentRowChanged["int"].connect(
            self._side_menu_collapsed.setCurrentRow
        )

        self._side_menu.currentRowChanged["int"].connect(
            self._main_content.setCurrentIndex
        )

        self._side_menu_collapsed.currentRowChanged["int"].connect(
            self._main_content.setCurrentIndex
        )

        self._side_menu.setIconSize(QSize(24, 24))
        self._side_menu_collapsed.setIconSize(QSize(24, 24))

    def __init_side_menu(self) -> None:
        """Создание элементов бокового меню"""

        for menu in self.__menu_list:
            item = QListWidgetItem()
            item.setIcon(QIcon(menu.get("icon")))
            item.setSizeHint(QSize(40, 40))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._side_menu_collapsed.addItem(item)
            self._side_menu_collapsed.setCurrentRow(0)

            item_new = QListWidgetItem()
            item_new.setIcon(QIcon(menu.get("icon")))
            item_new.setSizeHint(QSize(40, 40))
            item_new.setText(menu.get("name"))
            item_new.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._side_menu.addItem(item_new)
            self._side_menu.setCurrentRow(0)

    def __init_main_content(self) -> None:
        """Создание страниц"""

        for menu in self.__menu_list:
            self._main_content.addWidget(menu.get("widget"))

    def closeEvent(self, event: QCloseEvent) -> None:
        """Закрытие приложения"""

        # Если активна детекция
        if self.__menu_list[0]["widget"].check_worker_state():
            # Сообщение о работающей детекции
            button = QMessageBox.question(
                self,
                "Закрытие приложения",
                "Вы действительно хотите прервать обработку?",
            )

            # Завершение работы потока и закрытие приложения
            if button == QMessageBox.StandardButton.Yes:
                self.__menu_list[0]["widget"].stop_worker()
                self.__menu_list[0]["widget"].close_worker()
                self.__menu_list[1]["widget"].close_worker()
                event.accept()
            # Не закрывать приложение
            else:
                event.ignore()

        # Завершение работы потока и закрытие приложения
        else:
            self.__menu_list[0]["widget"].close_worker()
            self.__menu_list[1]["widget"].close_worker()
            event.accept()
