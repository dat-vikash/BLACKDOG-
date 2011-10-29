
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from GpsDialog import Ui_GpsDialog

class MapDialog(QDialog, Ui_GpsDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.result = None
        
        #FOR TESTING PURPOSES PRESETS THE VALUES:
#        self.tlLatDEdit.setText('29')
#        self.tlLatMEdit.setText('11')
#        self.tlLatSEdit.setText('23.29')
#        self.tlLongDEdit.setText('-81')
#        self.tlLongMEdit.setText('02')
#        self.tlLongSEdit.setText('51.72')
#        
#        self.brLatDEdit.setText('29')
#        self.brLatMEdit.setText('11')
#        self.brLatSEdit.setText('17.31')
#        self.brLongDEdit.setText('-81')
#        self.brLongMEdit.setText('02')
#        self.brLongSEdit.setText('43.82')

#
#
#        self.tlLatDEdit.setText('29')
#        self.tlLatMEdit.setText('11')
#        self.tlLatSEdit.setText('34.0116')
#        self.tlLongDEdit.setText('-81')
#        self.tlLongMEdit.setText('03')
#        self.tlLongSEdit.setText('13.122')
#        
#        self.brLatDEdit.setText('29')
#        self.brLatMEdit.setText('11')
#        self.brLatSEdit.setText('10.2768')
#        self.brLongDEdit.setText('-81')
#        self.brLongMEdit.setText('02')
#        self.brLongSEdit.setText('33.3564')

    def accept(self):
        try:
            self.result = [float(self.tlLatDEdit.text()), float(self.tlLatMEdit.text()), float(self.tlLatSEdit.text()), float(self.tlLongDEdit.text()), float(self.tlLongMEdit.text()), float(self.tlLongSEdit.text()),float(self.brLatDEdit.text()), float(self.brLatMEdit.text()), float(self.brLatSEdit.text()), float(self.brLongDEdit.text()), float(self.brLongMEdit.text()), float(self.brLongSEdit.text())]
            self.emit(SIGNAL('mapInput'))      
            QDialog.accept(self)
        except Exception, x:
            error = QErrorMessage(self)
            error.showMessage("Invalid Field Input")
        
    def reject(self):
        QDialog.reject(self)
        
    def getResult(self):       
        return self.result


