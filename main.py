from sys import exit

from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QApplication, QSplashScreen

from gui.main_window import MainWindow

if __name__ == "__main__":

    # Создание приложения
    app = QApplication([])

    # Установка и показ splash screen
    splash = QSplashScreen(QPixmap("./resources/icons/deer.svg"))
    splash.show()

    # Установка стиля элементов
    with open("resources/style.qss") as f:
        style_str = f.read()

    app.setStyleSheet(style_str)
    # Запуск цикла обработки
    app.processEvents()

    # Создание графического интерфейса
    window = MainWindow()

    # Установка параметров
    window.setWindowIcon(QIcon("./resources/icons/deer.svg"))
    window.setWindowTitle("Wild Life Detection")
    window.setMinimumSize(QSize(1280, 760))

    # Открытие приложения и завершение показа splash screen
    window.showMaximized()
    splash.finish(window)

    # Запуск выполнения
    exit(app.exec())
