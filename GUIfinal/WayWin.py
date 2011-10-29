
from PyQt4 import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *



from WaypointWindow import Ui_WaypointWindow



class WayWin(QWidget, Ui_WaypointWindow):

    def __init__(self, parent = None):   
        QWidget.__init__(self, parent)
        self.setupUi(self)        
        
        self.stopTimeEdit.setEnabled(False)
        
        self.latitude = 0
        self.longitude = 0
        self.type = None
        self.stopTime = 0
        
        self.connect(self.commitButton, QtCore.SIGNAL('clicked()'), self.commit)
        self.connect(self.cancelButton, QtCore.SIGNAL('clicked()'), self.cancel)
        
    def commit(self):
        try:
            self.latitude = abs(int(self.latDEdit.text()))+(float(self.latMEdit.text())/60)+(float(self.latSEdit.text())/3600)
            self.longitude = abs(int(self.longDEdit.text()))+(float(self.longMEdit.text())/60)+(float(self.longSEdit.text())/3600)
        
            if int(self.latDEdit.text())<0:
                self.latitude *=-1
            if int(self.longDEdit.text())<0:
                self.longitude *=-1
            
            self.type = self.typeBox.currentText()
            self.stopTime = self.stopTimeEdit.text()
            self.emit(SIGNAL('commit'))
        except Exception, x:
            error = QErrorMessage(self)
            error.showMessage("Invalid Field Input")
        
    def cancel(self):
        self.emit(SIGNAL('cancel'))        
    def getLatitude(self):
        return self.latitude
    def getLongitude(self):
        return self.longitude
    def getType(self):
        return self.type
    def getStopTime(self):
        return self.stopTime
   