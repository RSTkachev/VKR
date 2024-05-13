from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QStackedWidget, QWidget


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.title_frame = QFrame(self.centralwidget)
        self.title_frame.setObjectName(u"title_frame")
        self.title_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.title_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.title_frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.title_icon = QLabel(self.title_frame)
        self.title_icon.setObjectName(u"title_icon")

        self.horizontalLayout.addWidget(self.title_icon)

        self.title_label = QLabel(self.title_frame)
        self.title_label.setObjectName(u"title_label")

        self.horizontalLayout.addWidget(self.title_label)

        self.menu_btn = QPushButton(self.title_frame)
        self.menu_btn.setObjectName(u"menu_btn")

        self.horizontalLayout.addWidget(self.menu_btn, alignment=Qt.AlignmentFlag.AlignRight)


        self.gridLayout.addWidget(self.title_frame, 0, 0, 1, 2)

        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.stackedWidget.addWidget(self.page_2)

        self.gridLayout.addWidget(self.stackedWidget, 0, 2, 2, 1)

        self.listWidget_collapsed = QListWidget(self.centralwidget)
        self.listWidget_collapsed.setObjectName(u"listWidget_collapsed")
        self.listWidget_collapsed.setMaximumSize(QSize(55, 16777215))

        self.gridLayout.addWidget(self.listWidget_collapsed, 1, 0, 1, 1)

        self.listWidget = QListWidget(self.centralwidget)
        self.listWidget.setObjectName(u"listWidget")
        self.listWidget.setMaximumSize(QSize(200, 16777215))

        self.gridLayout.addWidget(self.listWidget, 1, 1, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)


        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.title_icon.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.title_label.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.menu_btn.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
