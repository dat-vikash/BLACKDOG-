# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GpsDialog.ui'
#
# Created: Thu Jan 10 15:38:00 2008
#      by: PyQt4 UI code generator 4.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_GpsDialog(object):
    def setupUi(self, GpsDialog):
        GpsDialog.setObjectName("GpsDialog")
        GpsDialog.resize(QtCore.QSize(QtCore.QRect(0,0,291,294).size()).expandedTo(GpsDialog.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(GpsDialog.sizePolicy().hasHeightForWidth())
        GpsDialog.setSizePolicy(sizePolicy)

        self.gridlayout = QtGui.QGridLayout(GpsDialog)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.tlLabel_2 = QtGui.QLabel(GpsDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tlLabel_2.sizePolicy().hasHeightForWidth())
        self.tlLabel_2.setSizePolicy(sizePolicy)
        self.tlLabel_2.setObjectName("tlLabel_2")
        self.gridlayout.addWidget(self.tlLabel_2,4,0,1,4)

        self.dLabel_2 = QtGui.QLabel(GpsDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dLabel_2.sizePolicy().hasHeightForWidth())
        self.dLabel_2.setSizePolicy(sizePolicy)
        self.dLabel_2.setObjectName("dLabel_2")
        self.gridlayout.addWidget(self.dLabel_2,5,1,1,2)

        self.tlLabel = QtGui.QLabel(GpsDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tlLabel.sizePolicy().hasHeightForWidth())
        self.tlLabel.setSizePolicy(sizePolicy)
        self.tlLabel.setObjectName("tlLabel")
        self.gridlayout.addWidget(self.tlLabel,0,0,1,4)

        self.dLabel = QtGui.QLabel(GpsDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dLabel.sizePolicy().hasHeightForWidth())
        self.dLabel.setSizePolicy(sizePolicy)
        self.dLabel.setObjectName("dLabel")
        self.gridlayout.addWidget(self.dLabel,1,1,1,1)

        self.sLabel_2 = QtGui.QLabel(GpsDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sLabel_2.sizePolicy().hasHeightForWidth())
        self.sLabel_2.setSizePolicy(sizePolicy)
        self.sLabel_2.setObjectName("sLabel_2")
        self.gridlayout.addWidget(self.sLabel_2,5,4,1,1)

        self.mLabel_2 = QtGui.QLabel(GpsDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mLabel_2.sizePolicy().hasHeightForWidth())
        self.mLabel_2.setSizePolicy(sizePolicy)
        self.mLabel_2.setObjectName("mLabel_2")
        self.gridlayout.addWidget(self.mLabel_2,5,3,1,1)

        self.longLabel = QtGui.QLabel(GpsDialog)
        self.longLabel.setObjectName("longLabel")
        self.gridlayout.addWidget(self.longLabel,3,0,1,1)

        self.latLabel = QtGui.QLabel(GpsDialog)
        self.latLabel.setObjectName("latLabel")
        self.gridlayout.addWidget(self.latLabel,2,0,1,1)

        self.buttonBox = QtGui.QDialogButtonBox(GpsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridlayout.addWidget(self.buttonBox,8,1,1,4)

        self.longLabel_2 = QtGui.QLabel(GpsDialog)
        self.longLabel_2.setObjectName("longLabel_2")
        self.gridlayout.addWidget(self.longLabel_2,7,0,1,1)

        self.latLabel_2 = QtGui.QLabel(GpsDialog)
        self.latLabel_2.setObjectName("latLabel_2")
        self.gridlayout.addWidget(self.latLabel_2,6,0,1,1)

        self.tlLatDEdit = QtGui.QLineEdit(GpsDialog)
        self.tlLatDEdit.setObjectName("tlLatDEdit")
        self.gridlayout.addWidget(self.tlLatDEdit,2,1,1,1)

        self.tlLongDEdit = QtGui.QLineEdit(GpsDialog)
        self.tlLongDEdit.setObjectName("tlLongDEdit")
        self.gridlayout.addWidget(self.tlLongDEdit,3,1,1,1)

        self.tlLatMEdit = QtGui.QLineEdit(GpsDialog)
        self.tlLatMEdit.setObjectName("tlLatMEdit")
        self.gridlayout.addWidget(self.tlLatMEdit,2,2,1,2)

        self.tlLongMEdit = QtGui.QLineEdit(GpsDialog)
        self.tlLongMEdit.setObjectName("tlLongMEdit")
        self.gridlayout.addWidget(self.tlLongMEdit,3,2,1,2)

        self.tlLongSEdit = QtGui.QLineEdit(GpsDialog)
        self.tlLongSEdit.setObjectName("tlLongSEdit")
        self.gridlayout.addWidget(self.tlLongSEdit,3,4,1,1)

        self.mLabel = QtGui.QLabel(GpsDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mLabel.sizePolicy().hasHeightForWidth())
        self.mLabel.setSizePolicy(sizePolicy)
        self.mLabel.setObjectName("mLabel")
        self.gridlayout.addWidget(self.mLabel,1,3,1,1)

        self.sLabel = QtGui.QLabel(GpsDialog)
        self.sLabel.setObjectName("sLabel")
        self.gridlayout.addWidget(self.sLabel,1,4,1,1)

        self.brLongDEdit = QtGui.QLineEdit(GpsDialog)
        self.brLongDEdit.setObjectName("brLongDEdit")
        self.gridlayout.addWidget(self.brLongDEdit,7,1,1,1)

        self.brLatDEdit = QtGui.QLineEdit(GpsDialog)
        self.brLatDEdit.setObjectName("brLatDEdit")
        self.gridlayout.addWidget(self.brLatDEdit,6,1,1,1)

        self.tlLatSEdit = QtGui.QLineEdit(GpsDialog)
        self.tlLatSEdit.setObjectName("tlLatSEdit")
        self.gridlayout.addWidget(self.tlLatSEdit,2,4,1,1)

        self.brLatSEdit = QtGui.QLineEdit(GpsDialog)
        self.brLatSEdit.setObjectName("brLatSEdit")
        self.gridlayout.addWidget(self.brLatSEdit,6,4,1,1)

        self.brLongSEdit = QtGui.QLineEdit(GpsDialog)
        self.brLongSEdit.setObjectName("brLongSEdit")
        self.gridlayout.addWidget(self.brLongSEdit,7,4,1,1)

        self.brLatMEdit = QtGui.QLineEdit(GpsDialog)
        self.brLatMEdit.setObjectName("brLatMEdit")
        self.gridlayout.addWidget(self.brLatMEdit,6,2,1,2)

        self.brLongMEdit = QtGui.QLineEdit(GpsDialog)
        self.brLongMEdit.setObjectName("brLongMEdit")
        self.gridlayout.addWidget(self.brLongMEdit,7,2,1,2)

        self.retranslateUi(GpsDialog)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),GpsDialog.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),GpsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(GpsDialog)
        GpsDialog.setTabOrder(self.tlLatDEdit,self.tlLatMEdit)
        GpsDialog.setTabOrder(self.tlLatMEdit,self.tlLatSEdit)
        GpsDialog.setTabOrder(self.tlLatSEdit,self.tlLongDEdit)
        GpsDialog.setTabOrder(self.tlLongDEdit,self.tlLongMEdit)
        GpsDialog.setTabOrder(self.tlLongMEdit,self.tlLongSEdit)
        GpsDialog.setTabOrder(self.tlLongSEdit,self.brLatDEdit)
        GpsDialog.setTabOrder(self.brLatDEdit,self.brLatMEdit)
        GpsDialog.setTabOrder(self.brLatMEdit,self.brLatSEdit)
        GpsDialog.setTabOrder(self.brLatSEdit,self.brLongDEdit)
        GpsDialog.setTabOrder(self.brLongDEdit,self.brLongMEdit)
        GpsDialog.setTabOrder(self.brLongMEdit,self.brLongSEdit)
        GpsDialog.setTabOrder(self.brLongSEdit,self.buttonBox)

    def retranslateUi(self, GpsDialog):
        GpsDialog.setWindowTitle(QtGui.QApplication.translate("GpsDialog", "Gps Input", None, QtGui.QApplication.UnicodeUTF8))
        self.tlLabel_2.setText(QtGui.QApplication.translate("GpsDialog", "Bottem Right Corner GPS:", None, QtGui.QApplication.UnicodeUTF8))
        self.dLabel_2.setText(QtGui.QApplication.translate("GpsDialog", "Degrees", None, QtGui.QApplication.UnicodeUTF8))
        self.tlLabel.setText(QtGui.QApplication.translate("GpsDialog", "Top Left Corner GPS:", None, QtGui.QApplication.UnicodeUTF8))
        self.dLabel.setText(QtGui.QApplication.translate("GpsDialog", "Degrees", None, QtGui.QApplication.UnicodeUTF8))
        self.sLabel_2.setText(QtGui.QApplication.translate("GpsDialog", "Seconds", None, QtGui.QApplication.UnicodeUTF8))
        self.mLabel_2.setText(QtGui.QApplication.translate("GpsDialog", "Minutes", None, QtGui.QApplication.UnicodeUTF8))
        self.longLabel.setText(QtGui.QApplication.translate("GpsDialog", "Longitude", None, QtGui.QApplication.UnicodeUTF8))
        self.latLabel.setText(QtGui.QApplication.translate("GpsDialog", "Latitude", None, QtGui.QApplication.UnicodeUTF8))
        self.longLabel_2.setText(QtGui.QApplication.translate("GpsDialog", "Longitude", None, QtGui.QApplication.UnicodeUTF8))
        self.latLabel_2.setText(QtGui.QApplication.translate("GpsDialog", "Latitude", None, QtGui.QApplication.UnicodeUTF8))
        self.mLabel.setText(QtGui.QApplication.translate("GpsDialog", "Minutes", None, QtGui.QApplication.UnicodeUTF8))
        self.sLabel.setText(QtGui.QApplication.translate("GpsDialog", "Seconds", None, QtGui.QApplication.UnicodeUTF8))

