# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RemoveDialog.ui'
#
# Created: Tue Feb 19 14:03:47 2008
#      by: PyQt4 UI code generator 4.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_RemoveDialog(object):
    def setupUi(self, RemoveDialog):
        RemoveDialog.setObjectName("RemoveDialog")
        RemoveDialog.resize(QtCore.QSize(QtCore.QRect(0,0,291,294).size()).expandedTo(RemoveDialog.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(RemoveDialog.sizePolicy().hasHeightForWidth())
        RemoveDialog.setSizePolicy(sizePolicy)

        self.gridlayout = QtGui.QGridLayout(RemoveDialog)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.cancelButton = QtGui.QPushButton(RemoveDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cancelButton.sizePolicy().hasHeightForWidth())
        self.cancelButton.setSizePolicy(sizePolicy)
        self.cancelButton.setObjectName("cancelButton")
        self.gridlayout.addWidget(self.cancelButton,8,1,1,2)

        self.commitButton = QtGui.QPushButton(RemoveDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.commitButton.sizePolicy().hasHeightForWidth())
        self.commitButton.setSizePolicy(sizePolicy)
        self.commitButton.setObjectName("commitButton")
        self.gridlayout.addWidget(self.commitButton,8,3,1,2)

        self.brLongMEdit = QtGui.QLineEdit(RemoveDialog)
        self.brLongMEdit.setObjectName("brLongMEdit")
        self.gridlayout.addWidget(self.brLongMEdit,7,2,1,2)

        self.brLatMEdit = QtGui.QLineEdit(RemoveDialog)
        self.brLatMEdit.setObjectName("brLatMEdit")
        self.gridlayout.addWidget(self.brLatMEdit,6,2,1,2)

        self.brLongSEdit = QtGui.QLineEdit(RemoveDialog)
        self.brLongSEdit.setObjectName("brLongSEdit")
        self.gridlayout.addWidget(self.brLongSEdit,7,4,1,1)

        self.brLatSEdit = QtGui.QLineEdit(RemoveDialog)
        self.brLatSEdit.setObjectName("brLatSEdit")
        self.gridlayout.addWidget(self.brLatSEdit,6,4,1,1)

        self.tlLatSEdit = QtGui.QLineEdit(RemoveDialog)
        self.tlLatSEdit.setObjectName("tlLatSEdit")
        self.gridlayout.addWidget(self.tlLatSEdit,2,4,1,1)

        self.brLatDEdit = QtGui.QLineEdit(RemoveDialog)
        self.brLatDEdit.setObjectName("brLatDEdit")
        self.gridlayout.addWidget(self.brLatDEdit,6,1,1,1)

        self.brLongDEdit = QtGui.QLineEdit(RemoveDialog)
        self.brLongDEdit.setObjectName("brLongDEdit")
        self.gridlayout.addWidget(self.brLongDEdit,7,1,1,1)

        self.sLabel = QtGui.QLabel(RemoveDialog)
        self.sLabel.setObjectName("sLabel")
        self.gridlayout.addWidget(self.sLabel,1,4,1,1)

        self.mLabel = QtGui.QLabel(RemoveDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mLabel.sizePolicy().hasHeightForWidth())
        self.mLabel.setSizePolicy(sizePolicy)
        self.mLabel.setObjectName("mLabel")
        self.gridlayout.addWidget(self.mLabel,1,3,1,1)

        self.tlLongSEdit = QtGui.QLineEdit(RemoveDialog)
        self.tlLongSEdit.setObjectName("tlLongSEdit")
        self.gridlayout.addWidget(self.tlLongSEdit,3,4,1,1)

        self.tlLongMEdit = QtGui.QLineEdit(RemoveDialog)
        self.tlLongMEdit.setObjectName("tlLongMEdit")
        self.gridlayout.addWidget(self.tlLongMEdit,3,2,1,2)

        self.tlLatMEdit = QtGui.QLineEdit(RemoveDialog)
        self.tlLatMEdit.setObjectName("tlLatMEdit")
        self.gridlayout.addWidget(self.tlLatMEdit,2,2,1,2)

        self.tlLongDEdit = QtGui.QLineEdit(RemoveDialog)
        self.tlLongDEdit.setObjectName("tlLongDEdit")
        self.gridlayout.addWidget(self.tlLongDEdit,3,1,1,1)

        self.tlLatDEdit = QtGui.QLineEdit(RemoveDialog)
        self.tlLatDEdit.setObjectName("tlLatDEdit")
        self.gridlayout.addWidget(self.tlLatDEdit,2,1,1,1)

        self.latLabel_2 = QtGui.QLabel(RemoveDialog)
        self.latLabel_2.setObjectName("latLabel_2")
        self.gridlayout.addWidget(self.latLabel_2,6,0,1,1)

        self.longLabel_2 = QtGui.QLabel(RemoveDialog)
        self.longLabel_2.setObjectName("longLabel_2")
        self.gridlayout.addWidget(self.longLabel_2,7,0,1,1)

        self.latLabel = QtGui.QLabel(RemoveDialog)
        self.latLabel.setObjectName("latLabel")
        self.gridlayout.addWidget(self.latLabel,2,0,1,1)

        self.longLabel = QtGui.QLabel(RemoveDialog)
        self.longLabel.setObjectName("longLabel")
        self.gridlayout.addWidget(self.longLabel,3,0,1,1)

        self.mLabel_2 = QtGui.QLabel(RemoveDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mLabel_2.sizePolicy().hasHeightForWidth())
        self.mLabel_2.setSizePolicy(sizePolicy)
        self.mLabel_2.setObjectName("mLabel_2")
        self.gridlayout.addWidget(self.mLabel_2,5,3,1,1)

        self.sLabel_2 = QtGui.QLabel(RemoveDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sLabel_2.sizePolicy().hasHeightForWidth())
        self.sLabel_2.setSizePolicy(sizePolicy)
        self.sLabel_2.setObjectName("sLabel_2")
        self.gridlayout.addWidget(self.sLabel_2,5,4,1,1)

        self.dLabel = QtGui.QLabel(RemoveDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dLabel.sizePolicy().hasHeightForWidth())
        self.dLabel.setSizePolicy(sizePolicy)
        self.dLabel.setObjectName("dLabel")
        self.gridlayout.addWidget(self.dLabel,1,1,1,1)

        self.tlLabel = QtGui.QLabel(RemoveDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tlLabel.sizePolicy().hasHeightForWidth())
        self.tlLabel.setSizePolicy(sizePolicy)
        self.tlLabel.setObjectName("tlLabel")
        self.gridlayout.addWidget(self.tlLabel,0,0,1,1)

        self.dLabel_2 = QtGui.QLabel(RemoveDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dLabel_2.sizePolicy().hasHeightForWidth())
        self.dLabel_2.setSizePolicy(sizePolicy)
        self.dLabel_2.setObjectName("dLabel_2")
        self.gridlayout.addWidget(self.dLabel_2,5,1,1,1)

        self.tlLabel_2 = QtGui.QLabel(RemoveDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tlLabel_2.sizePolicy().hasHeightForWidth())
        self.tlLabel_2.setSizePolicy(sizePolicy)
        self.tlLabel_2.setObjectName("tlLabel_2")
        self.gridlayout.addWidget(self.tlLabel_2,4,0,1,1)

        self.retranslateUi(RemoveDialog)
        QtCore.QMetaObject.connectSlotsByName(RemoveDialog)
        RemoveDialog.setTabOrder(self.tlLatDEdit,self.tlLatMEdit)
        RemoveDialog.setTabOrder(self.tlLatMEdit,self.tlLatSEdit)
        RemoveDialog.setTabOrder(self.tlLatSEdit,self.tlLongDEdit)
        RemoveDialog.setTabOrder(self.tlLongDEdit,self.tlLongMEdit)
        RemoveDialog.setTabOrder(self.tlLongMEdit,self.tlLongSEdit)
        RemoveDialog.setTabOrder(self.tlLongSEdit,self.brLatDEdit)
        RemoveDialog.setTabOrder(self.brLatDEdit,self.brLatMEdit)
        RemoveDialog.setTabOrder(self.brLatMEdit,self.brLatSEdit)
        RemoveDialog.setTabOrder(self.brLatSEdit,self.brLongDEdit)
        RemoveDialog.setTabOrder(self.brLongDEdit,self.brLongMEdit)
        RemoveDialog.setTabOrder(self.brLongMEdit,self.brLongSEdit)

    def retranslateUi(self, RemoveDialog):
        RemoveDialog.setWindowTitle(QtGui.QApplication.translate("RemoveDialog", "Remove Obstacles", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("RemoveDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.commitButton.setText(QtGui.QApplication.translate("RemoveDialog", "Commit", None, QtGui.QApplication.UnicodeUTF8))
        self.sLabel.setText(QtGui.QApplication.translate("RemoveDialog", "Seconds", None, QtGui.QApplication.UnicodeUTF8))
        self.mLabel.setText(QtGui.QApplication.translate("RemoveDialog", "Minutes", None, QtGui.QApplication.UnicodeUTF8))
        self.latLabel_2.setText(QtGui.QApplication.translate("RemoveDialog", "Latitude", None, QtGui.QApplication.UnicodeUTF8))
        self.longLabel_2.setText(QtGui.QApplication.translate("RemoveDialog", "Longitude", None, QtGui.QApplication.UnicodeUTF8))
        self.latLabel.setText(QtGui.QApplication.translate("RemoveDialog", "Latitude", None, QtGui.QApplication.UnicodeUTF8))
        self.longLabel.setText(QtGui.QApplication.translate("RemoveDialog", "Longitude", None, QtGui.QApplication.UnicodeUTF8))
        self.mLabel_2.setText(QtGui.QApplication.translate("RemoveDialog", "Minutes", None, QtGui.QApplication.UnicodeUTF8))
        self.sLabel_2.setText(QtGui.QApplication.translate("RemoveDialog", "Seconds", None, QtGui.QApplication.UnicodeUTF8))
        self.dLabel.setText(QtGui.QApplication.translate("RemoveDialog", "Degrees", None, QtGui.QApplication.UnicodeUTF8))
        self.tlLabel.setText(QtGui.QApplication.translate("RemoveDialog", "Point One:", None, QtGui.QApplication.UnicodeUTF8))
        self.dLabel_2.setText(QtGui.QApplication.translate("RemoveDialog", "Degrees", None, QtGui.QApplication.UnicodeUTF8))
        self.tlLabel_2.setText(QtGui.QApplication.translate("RemoveDialog", "Point Two:", None, QtGui.QApplication.UnicodeUTF8))

