# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QTabWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(640, 780)
        self.layoutWidget = QWidget(Widget)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(30, 20, 191, 176))
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_4 = QLabel(self.layoutWidget)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_4.addWidget(self.label_4)

        self.comboBox_freq = QComboBox(self.layoutWidget)
        self.comboBox_freq.setObjectName(u"comboBox_freq")

        self.horizontalLayout_4.addWidget(self.comboBox_freq)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.comboBox_amp = QComboBox(self.layoutWidget)
        self.comboBox_amp.setObjectName(u"comboBox_amp")

        self.horizontalLayout.addWidget(self.comboBox_amp)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_5 = QLabel(self.layoutWidget)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_5.addWidget(self.label_5)

        self.comboBox_cycles = QComboBox(self.layoutWidget)
        self.comboBox_cycles.setObjectName(u"comboBox_cycles")

        self.horizontalLayout_5.addWidget(self.comboBox_cycles)


        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_3 = QLabel(self.layoutWidget)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_3.addWidget(self.label_3)

        self.comboBox_avg = QComboBox(self.layoutWidget)
        self.comboBox_avg.setObjectName(u"comboBox_avg")

        self.horizontalLayout_3.addWidget(self.comboBox_avg)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.comboBox_txgain = QComboBox(self.layoutWidget)
        self.comboBox_txgain.setObjectName(u"comboBox_txgain")

        self.horizontalLayout_2.addWidget(self.comboBox_txgain)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_6 = QLabel(self.layoutWidget)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_6.addWidget(self.label_6)

        self.comboBox_rxgain = QComboBox(self.layoutWidget)
        self.comboBox_rxgain.setObjectName(u"comboBox_rxgain")

        self.horizontalLayout_6.addWidget(self.comboBox_rxgain)


        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.tabWidget = QTabWidget(Widget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(20, 220, 601, 521))
        self.tabSignal = QWidget()
        self.tabSignal.setObjectName(u"tabSignal")
        self.tabWidget.addTab(self.tabSignal, "")
        self.tabData = QWidget()
        self.tabData.setObjectName(u"tabData")
        self.tableData = QTableWidget(self.tabData)
        self.tableData.setObjectName(u"tableData")
        self.tableData.setGeometry(QRect(10, 10, 571, 471))
        self.tabWidget.addTab(self.tabData, "")
        self.label_Status = QLabel(Widget)
        self.label_Status.setObjectName(u"label_Status")
        self.label_Status.setGeometry(QRect(30, 750, 141, 22))
        self.widget = QWidget(Widget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(280, 140, 279, 56))
        self.gridLayout = QGridLayout(self.widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 0, 1, 1)

        self.pushButtonRun = QPushButton(self.widget)
        self.pushButtonRun.setObjectName(u"pushButtonRun")

        self.gridLayout.addWidget(self.pushButtonRun, 0, 1, 1, 1)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_7 = QLabel(self.widget)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_7.addWidget(self.label_7)

        self.lineEditDataLabel = QLineEdit(self.widget)
        self.lineEditDataLabel.setObjectName(u"lineEditDataLabel")

        self.horizontalLayout_7.addWidget(self.lineEditDataLabel)


        self.gridLayout.addLayout(self.horizontalLayout_7, 1, 0, 1, 1)

        self.pushButtonRecord = QPushButton(self.widget)
        self.pushButtonRecord.setObjectName(u"pushButtonRecord")

        self.gridLayout.addWidget(self.pushButtonRecord, 1, 1, 1, 1)

        self.widget1 = QWidget(Widget)
        self.widget1.setObjectName(u"widget1")
        self.widget1.setGeometry(QRect(280, 20, 71, 51))
        self.verticalLayout_2 = QVBoxLayout(self.widget1)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.checkBoxFilter = QCheckBox(self.widget1)
        self.checkBoxFilter.setObjectName(u"checkBoxFilter")

        self.verticalLayout_2.addWidget(self.checkBoxFilter)

        self.checkBoxSweep = QCheckBox(self.widget1)
        self.checkBoxSweep.setObjectName(u"checkBoxSweep")

        self.verticalLayout_2.addWidget(self.checkBoxSweep)


        self.retranslateUi(Widget)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"Widget", None))
        self.label_4.setText(QCoreApplication.translate("Widget", u"Frequency", None))
        self.label.setText(QCoreApplication.translate("Widget", u"Amplitude", None))
        self.label_5.setText(QCoreApplication.translate("Widget", u"Cycles", None))
        self.label_3.setText(QCoreApplication.translate("Widget", u"Averages", None))
        self.label_2.setText(QCoreApplication.translate("Widget", u"Tx Gain", None))
        self.label_6.setText(QCoreApplication.translate("Widget", u"Rx Gain", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSignal), QCoreApplication.translate("Widget", u"Signal", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabData), QCoreApplication.translate("Widget", u"Data", None))
        self.label_Status.setText(QCoreApplication.translate("Widget", u"Status: Not Connected...", None))
        self.pushButtonRun.setText(QCoreApplication.translate("Widget", u"Run", None))
        self.label_7.setText(QCoreApplication.translate("Widget", u"Data Label", None))
        self.pushButtonRecord.setText(QCoreApplication.translate("Widget", u"Record", None))
        self.checkBoxFilter.setText(QCoreApplication.translate("Widget", u"Filter", None))
        self.checkBoxSweep.setText(QCoreApplication.translate("Widget", u"Sweep", None))
    # retranslateUi

