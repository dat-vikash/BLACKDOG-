# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'WaypointTableWindow.ui'
#
# Created: Sun Dec  2 16:25:51 2007
#      by: PyQt4 UI code generator 4.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_WaypointTableWindow(object):
    def setupUi(self, WaypointTableWindow):
        WaypointTableWindow.setObjectName("WaypointTableWindow")
        WaypointTableWindow.resize(QtCore.QSize(QtCore.QRect(0,0,442,223).size()).expandedTo(WaypointTableWindow.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(WaypointTableWindow)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.removeButton = QtGui.QPushButton(WaypointTableWindow)
        self.removeButton.setObjectName("removeButton")
        self.gridlayout.addWidget(self.removeButton,1,4,1,1)

        self.insertButton = QtGui.QPushButton(WaypointTableWindow)
        self.insertButton.setObjectName("insertButton")
        self.gridlayout.addWidget(self.insertButton,1,3,1,1)

        self.appendButton = QtGui.QPushButton(WaypointTableWindow)
        self.appendButton.setObjectName("appendButton")
        self.gridlayout.addWidget(self.appendButton,1,2,1,1)

        self.goToButton = QtGui.QPushButton(WaypointTableWindow)
        self.goToButton.setObjectName("goToButton")
        self.gridlayout.addWidget(self.goToButton,1,1,1,1)

        self.modifyButton = QtGui.QPushButton(WaypointTableWindow)
        self.modifyButton.setObjectName("modifyButton")
        self.gridlayout.addWidget(self.modifyButton,1,0,1,1)

        self.receivedTable = QtGui.QTableWidget(WaypointTableWindow)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.receivedTable.sizePolicy().hasHeightForWidth())
        self.receivedTable.setSizePolicy(sizePolicy)
        self.receivedTable.setObjectName("receivedTable")
        self.gridlayout.addWidget(self.receivedTable,0,0,1,5)

        self.retranslateUi(WaypointTableWindow)
        QtCore.QMetaObject.connectSlotsByName(WaypointTableWindow)

    def retranslateUi(self, WaypointTableWindow):
        WaypointTableWindow.setWindowTitle(QtGui.QApplication.translate("WaypointTableWindow", "Waypoint Table", None, QtGui.QApplication.UnicodeUTF8))
        self.removeButton.setText(QtGui.QApplication.translate("WaypointTableWindow", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.insertButton.setText(QtGui.QApplication.translate("WaypointTableWindow", "Insert", None, QtGui.QApplication.UnicodeUTF8))
        self.appendButton.setText(QtGui.QApplication.translate("WaypointTableWindow", "Append", None, QtGui.QApplication.UnicodeUTF8))
        self.goToButton.setText(QtGui.QApplication.translate("WaypointTableWindow", "Go To", None, QtGui.QApplication.UnicodeUTF8))
        self.modifyButton.setText(QtGui.QApplication.translate("WaypointTableWindow", "Modify", None, QtGui.QApplication.UnicodeUTF8))
        self.receivedTable.clear()
        self.receivedTable.setColumnCount(3)
        self.receivedTable.setRowCount(0)

        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(QtGui.QApplication.translate("WaypointTableWindow", "Latitude", None, QtGui.QApplication.UnicodeUTF8))
        self.receivedTable.setHorizontalHeaderItem(0,headerItem)

        headerItem1 = QtGui.QTableWidgetItem()
        headerItem1.setText(QtGui.QApplication.translate("WaypointTableWindow", "Longitude", None, QtGui.QApplication.UnicodeUTF8))
        self.receivedTable.setHorizontalHeaderItem(1,headerItem1)

        headerItem2 = QtGui.QTableWidgetItem()
        headerItem2.setText(QtGui.QApplication.translate("WaypointTableWindow", "Type", None, QtGui.QApplication.UnicodeUTF8))
        self.receivedTable.setHorizontalHeaderItem(2,headerItem2)

