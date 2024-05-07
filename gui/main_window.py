import sys
from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QListWidgetItem, QWidget, QGridLayout
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QFont

from resources.main_window_ui import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize the UI from the generated 'main_ui' class
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set window properties
        self.setWindowIcon(QIcon("./resources/icons/deer.svg"))
        self.setWindowTitle("Wild Life Detection")

        # Initialize UI elements
        self.title_label = self.ui.title_label
        self.title_label.setText("WLD")

        self.title_icon = self.ui.title_icon
        self.title_icon.setText("")
        self.title_icon.setPixmap(QPixmap("./resources/icons/deer.svg"))
        self.setIconSize(QSize(30, 30))
        self.title_icon.setScaledContents(True)

        self.side_menu = self.ui.listWidget
        self.side_menu.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.side_menu_collapsed = self.ui.listWidget_collapsed
        self.side_menu_collapsed.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.side_menu_collapsed.hide()

        self.menu_btn = self.ui.menu_btn
        self.menu_btn.setText("")
        self.menu_btn.setIcon(QIcon("./resources/icons/menu.svg"))
        self.menu_btn.setIconSize(QSize(30, 30))
        self.menu_btn.setCheckable(True)
        self.menu_btn.setChecked(False)

        self.main_content = self.ui.stackedWidget

        self.menu_list = [
            {
                'name': 'Главная страница',
                'icon': './resources/icons/camera.svg'
            },
            {
                'name': 'Статистика',
                'icon': './resources/icons/clock.svg'
            },
            {
                'name': 'Настройки',
                'icon': './resources/icons/settings.svg'
            },
            {
                'name': 'Информация',
                'icon': './resources/icons/info.svg'
            }
        ]

        self.init_list_widget()
        self.init_stackwidget()
        self.init_single_slot()

    def init_single_slot(self):
        self.menu_btn.toggled['bool'].connect(self.side_menu.setHidden)
        self.menu_btn.toggled['bool'].connect(self.title_label.setHidden)
        self.menu_btn.toggled['bool'].connect(self.side_menu_collapsed.setVisible)
        self.menu_btn.toggled['bool'].connect(self.title_icon.setHidden)

        self.side_menu.currentRowChanged['int'].connect(self.main_content.setCurrentIndex)
        self.side_menu_collapsed.currentRowChanged['int'].connect(self.main_content.setCurrentIndex)
        self.side_menu.currentRowChanged['int'].connect(self.side_menu_collapsed.setCurrentRow)
        self.side_menu_collapsed.currentRowChanged['int'].connect(self.side_menu.setCurrentRow)

    def init_list_widget(self):
        self.side_menu_collapsed.clear()
        self.side_menu.clear()

        for menu in self.menu_list:
            item = QListWidgetItem()
            item.setIcon(QIcon(menu.get("icon")))
            item.setSizeHint(QSize(40, 40))
            self.side_menu_collapsed.addItem(item)
            self.side_menu_collapsed.setCurrentRow(0)

            item_new = QListWidgetItem()
            item_new.setIcon(QIcon(menu.get("icon")))
            item.setSizeHint(QSize(40, 40))
            item_new.setText(menu.get("name"))
            self.side_menu.addItem(item_new)
            self.side_menu.setCurrentRow(0)

    def init_stackwidget(self):
        widget_list = self.main_content.findChildren(QWidget)
        for widget in widget_list:
            self.main_content.removeWidget(widget)

        for menu in self.menu_list:
            text = menu.get("name")
            layout = QGridLayout()
            label = QLabel(text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = QFont()
            font.setPixelSize(20)
            label.setFont(font)
            layout.addWidget(label)
            new_page = QWidget()
            new_page.setLayout(layout)
            self.main_content.addWidget(new_page)
