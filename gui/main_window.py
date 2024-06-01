from PySide6.QtWidgets import QMainWindow, QListWidgetItem, QMessageBox
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QCloseEvent

from gui.main_window_ui import UiMainWindow
from gui.detection_window import DetectionWidget
from gui.statistic_window import StatisticWidget
from gui.info_window import InfoWidget


# Окно
class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        # Инициализация контейнера для UI
        self.ui = UiMainWindow(self)

        # Создание графического интерфейса
        self.title_label = self.ui.title_label
        self.title_label.hide()

        self.title_icon = self.ui.title_icon
        self.title_icon.hide()

        self.side_menu = self.ui.listWidget
        self.side_menu.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.side_menu.hide()
        self.side_menu_collapsed = self.ui.listWidget_collapsed
        self.side_menu_collapsed.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.menu_btn = self.ui.menu_btn
        self.menu_btn.setCheckable(True)
        self.menu_btn.setChecked(True)

        self.main_content = self.ui.stackedWidget

        # Страницы приложения
        self.menu_list = [
            {
                'name': 'Главная страница',
                'icon': './resources/icons/camera.svg',
                'widget': DetectionWidget()
            },
            {
                'name': 'Статистика',
                'icon': './resources/icons/clock.svg',
                'widget': StatisticWidget()
            },
            {
                'name': 'Информация',
                'icon': './resources/icons/info.svg',
                'widget': InfoWidget()
            }
        ]

        self.init_list_widget()
        self.init_stackwidget()
        self.init_single_slot()

    # Настройка бокового меню
    def init_single_slot(self) -> None:
        self.menu_btn.toggled['bool'].connect(self.side_menu.setHidden)
        self.menu_btn.toggled['bool'].connect(self.title_label.setHidden)
        self.menu_btn.toggled['bool'].connect(self.side_menu_collapsed.setVisible)
        self.menu_btn.toggled['bool'].connect(self.title_icon.setHidden)

        self.side_menu_collapsed.currentRowChanged['int'].connect(self.side_menu.setCurrentRow)
        self.side_menu.currentRowChanged['int'].connect(self.side_menu_collapsed.setCurrentRow)

        self.side_menu.currentRowChanged['int'].connect(self.main_content.setCurrentIndex)
        self.side_menu_collapsed.currentRowChanged['int'].connect(self.main_content.setCurrentIndex)

        self.side_menu.setIconSize(QSize(24, 24))
        self.side_menu_collapsed.setIconSize(QSize(24, 24))

    # Создание элементов бокового меню
    def init_list_widget(self) -> None:

        for menu in self.menu_list:
            item = QListWidgetItem()
            item.setIcon(QIcon(menu.get("icon")))
            item.setSizeHint(QSize(40, 40))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.side_menu_collapsed.addItem(item)
            self.side_menu_collapsed.setCurrentRow(0)

            item_new = QListWidgetItem()
            item_new.setIcon(QIcon(menu.get("icon")))
            item_new.setSizeHint(QSize(40, 40))
            item_new.setText(menu.get("name"))
            item_new.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.side_menu.addItem(item_new)
            self.side_menu.setCurrentRow(0)

    # Создание страниц
    def init_stackwidget(self) -> None:
        for menu in self.menu_list:
            new_page = menu.get('widget')
            self.main_content.addWidget(new_page)

    # Закрытие приложения
    def closeEvent(self, event: QCloseEvent) -> None:
        # Если активна детекция
        if self.menu_list[0]['widget'].worker.is_working:
            # Сообщение о работающей детекции
            button = QMessageBox.question(self, "Закрытие приложения", "Вы действительно хотите прервать обработку?")

            # Завершение работы потока и закрытие приложения
            if button == QMessageBox.StandardButton.Yes:
                self.menu_list[0]['widget'].worker.is_working = False
                self.menu_list[0]['widget'].worker_thread.quit()
                self.menu_list[0]['widget'].worker_thread.wait()
                event.accept()
            # Не закрывать приложение
            else:
                event.ignore()

        # Завершение работы потока и закрытие приложения
        else:
            self.menu_list[0]['widget'].worker_thread.quit()
            self.menu_list[0]['widget'].worker_thread.wait()
            event.accept()
