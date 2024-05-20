import sys
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import QSize
from gui.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication([])

    with open("resources/style.qss") as f:
        style_str = f.read()

    app.setStyleSheet(style_str)

    splash = QSplashScreen(QPixmap('./resources/icons/deer.svg'))
    splash.show()
    app.processEvents()

    window = MainWindow()

    # Установка параметров
    window.setWindowIcon(QIcon("./resources/icons/deer.svg"))
    window.setWindowTitle("Wild Life Detection")
    window.setMinimumSize(QSize(1280, 760))

    # Открытие приложения и завершение показа splash screen
    window.showMaximized()
    splash.finish(window)

    sys.exit(app.exec())
