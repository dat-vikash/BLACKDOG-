
from PyQt4 import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *



from WaypointTableWindow import Ui_WaypointTableWindow





class WayTableWin(QWidget, Ui_WaypointTableWindow):

    def __init__(self, parent = None):          
        QWidget.__init__(self)
        self.setupUi(self)
        self.currentIndex = 0
        #parent.test()
        
        
        #self.waypointWindow.show()
         
        
        self.connect(self.modifyButton, QtCore.SIGNAL('clicked()'), self.changeWaypoint)
        self.connect(self.insertButton, QtCore.SIGNAL('clicked()'), self.insertWaypoint)
        self.connect(self.goToButton, QtCore.SIGNAL('clicked()'), self.goToWaypoint)
        self.connect(self.appendButton, QtCore.SIGNAL('clicked()'), self.appendWaypoint)
        self.connect(self.removeButton, QtCore.SIGNAL('clicked()'), self.removeWaypoint)
 
    def changeWaypoint(self):
        self.currentIndex = self.receivedTable.currentRow()
        self.emit(SIGNAL('changeWay'))
    def appendWaypoint(self):
        self.currentIndex = self.receivedTable.currentRow()
        self.emit(SIGNAL('appendWay'))
    def insertWaypoint(self):
        self.currentIndex = self.receivedTable.currentRow()
        self.emit(SIGNAL('insertWay'))
    def removeWaypoint(self):
        self.currentIndex = self.receivedTable.currentRow()
        self.emit(SIGNAL('removeWay'))
    def goToWaypoint(self):
        self.currentIndex = self.receivedTable.currentRow()
        self.emit(SIGNAL('goToWay'))
    def getCurrentIndex(self):
        return self.currentIndex
    def isSelected(self):
        if(self.receivedTable.selectedItems()!=[]):
            return True
        else:
            return False
    def selectRow(self, row):
        items = self.receivedTable.selectedItems()
        for widget in items:
            widget.setSelected(False)
        self.receivedTable.setCurrentCell(row, 0)
        self.receivedTable.setRangeSelected(QTableWidgetSelectionRange(row, 0, row, 2), True)
    def update(self, wayList):
    
        self.clearTable()
        i = 0
        for Waypoint in wayList:
            #print str(i) +": " +str(wayList[i].getType())
            if ((wayList[i].getType() != 1) & (wayList[i].getType() != 3)):  
                where = self.receivedTable.rowCount()
                if i>= where:          
                    self.receivedTable.insertRow(where)
                type = None
                
                if wayList[i].getType() == 0:
                    type = "Go to"     
                elif wayList[i].getType() == 2:
                    type = "Stop"
                #elif wayList[i].getType() == 3:
                #    type = "Orbit"
                
                
                
                item = QtGui.QTableWidgetItem()
                item.setText(QtGui.QApplication.translate("GUI", str(wayList[i].getLatitude()), None, QtGui.QApplication.UnicodeUTF8))
                self.receivedTable.setItem(where,0,item)
                item = QtGui.QTableWidgetItem()
                item.setText(QtGui.QApplication.translate("GUI", str(wayList[i].getLongitude()), None, QtGui.QApplication.UnicodeUTF8))
                self.receivedTable.setItem(where,1,item) 
                item = QtGui.QTableWidgetItem()
                item.setText(QtGui.QApplication.translate("GUI", str(type), None, QtGui.QApplication.UnicodeUTF8))
                self.receivedTable.setItem(where,2,item) 
            i+=1  
        print ""
    def closeEvent(self, closeEvent):
        self.emit(SIGNAL('closed'))
    def clearTable(self):
        i = self.receivedTable.rowCount()
        while i != -1:
            self.receivedTable.removeRow(i)
            i-=1
    
                    
                

            
        