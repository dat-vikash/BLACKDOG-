
from PyQt4 import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *



from RemoveDialog import Ui_RemoveDialog



class RemoveWin(QWidget, Ui_RemoveDialog):

    def __init__(self, parent = None):   
        QWidget.__init__(self, parent)
        self.setupUi(self)        
        
        self.latitude1 = 0
        self.longitude1 = 0
        self.latitude2 = 0
        self.longitude2 = 0
        
        self.connect(self.commitButton, QtCore.SIGNAL('clicked()'), self.commit)
        self.connect(self.cancelButton, QtCore.SIGNAL('clicked()'), self.cancel)
        
    def commit(self):
        try:
            self.latitude1 = abs(int(self.tlLatDEdit.text()))+(float(self.tlLatMEdit.text())/60)+(float(self.tlLatSEdit.text())/3600)
            self.longitude1 = abs(int(self.tlLongDEdit.text()))+(float(self.tlLongMEdit.text())/60)+(float(self.tlLongSEdit.text())/3600)
            
            self.latitude2 = abs(int(self.brLatDEdit.text()))+(float(self.brLatMEdit.text())/60)+(float(self.brLatSEdit.text())/3600)
            self.longitude2 = abs(int(self.brLongDEdit.text()))+(float(self.brLongMEdit.text())/60)+(float(self.brLongSEdit.text())/3600)
            
            if int(self.tlLatDEdit.text())<0:
                self.latitude1 *=-1
            if int(self.tlLongDEdit.text())<0:
                self.longitude1 *=-1
            if int(self.brLatDEdit.text())<0:
                self.latitude2 *=-1
            if int(self.brLongDEdit.text())<0:
                self.longitude2 *=-1

            self.emit(SIGNAL('removeObstacles'))
        except Exception, x:
            error = QErrorMessage(self)
            error.showMessage("Invalid Field Input")
        
    def cancel(self):
        self.emit(SIGNAL('cancel'))      
    def getLatitude1(self):
        return self.latitude1
    def getLongitude1(self):
        return self.longitude1
    def getLatitude2(self):
        return self.latitude2
    def getLongitude2(self):
        return self.longitude2
