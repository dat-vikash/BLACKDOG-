import sys
import Pyro.core
import Pyro.util
from math import *

import time
from Waypoint import Waypoint
from MapViewer import MapViewer
from MapDialog import MapDialog
from WayTableWin import WayTableWin
from WayWin import WayWin
from CircleWin import CircleWin
from LineWin import LineWin
from RemoveWin import RemoveWin

from UpdateThread import UpdateThread

from GUI import Ui_GUI
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore
from PyQt4 import QtGui

from threading import Lock

class MainWindow(QMainWindow, Ui_GUI):

    def __init__(self, parent = None):   
        QMainWindow.__init__(self, parent)

        self.setupUi(self)
        self.center()                            #Centers GUI
        
        #Declares the additional Windows
        self.mapView = MapViewer()
        
        self.waypointWindow = WayWin()       
        self.waypointTable = WayTableWin()
        self.lineWindow = LineWin()
        self.removeWindow = RemoveWin()
        self.circleWindow = CircleWin()
            
        #the dialog for Cordinates
        self.mapDlg = MapDialog(self)
        
        #information from The lower layers of the system (object)
        self.object = None
        self.updateThread = None
        self.way = None
        self.wayList = None
        
        self.statusOn = QPixmap.fromImage(QImage("on.gif"))
        self.statusOff = QPixmap.fromImage(QImage("off.gif"))
        
        self.navPicture.setPixmap(self.statusOff)
        self.gpsPicture.setPixmap(self.statusOff)
        self.commPicture.setPixmap(self.statusOff)
        self.wayPicture.setPixmap(self.statusOff)
               
        self.scene = None
        self.mapLat = 0
        self.mapLong = 0
        self.mapTopLeftLat = 0
        self.mapTopLeftLong = 0
        self.mapPixelLat = 0
        self.mapPixelLong = 0
        self.mapLatNegFlag = 1
        self.mapLongNegFlag = 1
        self.mapBRLatNegFlag = 1
        self.mapBRLongNegFlag = 1
        self.pixelSizeLat = 0
        self.pixelSizeLong = 0
        
        self.filename = ""
        
        self.groundCount = 0
        self.guiKey = None
        self.updateLock = Lock()
        self.actionType = 0
        
        #declares the Things stores in the map       
        self.point = None
        self.circleObj = None
        self.linePoint = None
        self.lineObj = None
        self.removePoint = None
        self.removeObj = None
        self.points = []
        self.lines = []
        self.obstacles= []
        self.vehicle = None
        self.plane = None
        self.selectedID = -1

        #the menu checkable parts in the WINDOW menu
        self.actionMap.setCheckable(True)
        self.actionTable.setCheckable(True)
        self.actionMetric.setCheckable(True)
        self.actionEnglish.setCheckable(True)
        
        self.actionMetric.setChecked(True)
        self.actionEnglish.setChecked(False)
        self.actionMap.setChecked(False)
        self.actionTable.setChecked(False)        

        #connects all the signals 
        
        self.connect(self.mapView, QtCore.SIGNAL('mouseClick'),self.mapClick)
        self.connect(self.mapDlg, QtCore.SIGNAL('mapInput'),self.mapDialog)
        self.connect(self.actionSave_Waypoints, QtCore.SIGNAL('triggered()'), self.saveWaypoints)
        self.connect(self.actionLoad_Waypoints, QtCore.SIGNAL('triggered()'), self.loadWaypoints)
        self.connect(self.actionOpen_Map, QtCore.SIGNAL('triggered()'), self.openFile)
        self.connect(self.actionOpen_Vehicle, QtCore.SIGNAL('triggered()'), self.openVehicle)
        self.connect(self.actionMap, QtCore.SIGNAL('triggered()'), self.showMap)
        self.connect(self.actionTable, QtCore.SIGNAL('triggered()'), self.showTable)
        self.connect(self.actionMetric, QtCore.SIGNAL('triggered()'), self.setMetricUnits)
        self.connect(self.actionEnglish, QtCore.SIGNAL('triggered()'), self.setEnglishUnits)
        self.connect(self.actionAdd_Circle, QtCore.SIGNAL('triggered()'), self.addCircle)
        self.connect(self.actionAdd_Line, QtCore.SIGNAL('triggered()'), self.addLine)
        self.connect(self.actionRemove_Obstacles, QtCore.SIGNAL('triggered()'), self.removeObstacles)
        
        
        self.connect(self.waypointTable, QtCore.SIGNAL('changeWay'), self.changeWaypoint)
        self.connect(self.waypointTable, QtCore.SIGNAL('insertWay'), self.insertWaypoint)
        self.connect(self.waypointTable, QtCore.SIGNAL('goToWay'), self.goToWaypoint)
        self.connect(self.waypointTable, QtCore.SIGNAL('appendWay'), self.appendWaypoint)
        self.connect(self.waypointTable, QtCore.SIGNAL('removeWay'), self.removeWaypoint)
        
        self.connect(self.waypointWindow, QtCore.SIGNAL('commit'), self.commit)
        self.connect(self.circleWindow, QtCore.SIGNAL('commitCircle'), self.commitCircle)
        self.connect(self.lineWindow, QtCore.SIGNAL('commitLine'), self.commitLine)
        self.connect(self.removeWindow, QtCore.SIGNAL('removeObstacles'), self.commitRemove)
        
        self.connect(self.circleWindow, QtCore.SIGNAL('previewCircle'), self.previewCircle)
        
        self.connect(self.waypointWindow, QtCore.SIGNAL('cancel'), self.cancel)
        self.connect(self.lineWindow, QtCore.SIGNAL('cancel'), self.cancel)
        self.connect(self.circleWindow, QtCore.SIGNAL('cancel'), self.cancel)
        self.connect(self.removeWindow, QtCore.SIGNAL('cancel'), self.cancel)
        
        self.connect(self.mapView, QtCore.SIGNAL('closed'), self.mapClosed)
        self.connect(self.waypointTable, QtCore.SIGNAL('closed'), self.tableClosed)
        
        self.connect(self.setButton, QtCore.SIGNAL('clicked()'), self.setMode)
        self.connect(self.updateGSButton, QtCore.SIGNAL('clicked()'), self.updateGSPacket)
        self.connect(self.haltButton, QtCore.SIGNAL('clicked()'), self.haltCommit)
        self.connect(self.resumeButton, QtCore.SIGNAL('clicked()'), self.resumeCommit)
        self.connect(self.waypointWindow.typeBox, SIGNAL('currentIndexChanged(QString)'), self.typeChange)
        
        self.connect(self.returnCheckBox, QtCore.SIGNAL('clicked()'), self.preflightReturnCommit)
        self.connect(self.haltCheckBox, QtCore.SIGNAL('clicked()'), self.preflightHaltCommit)
        self.connect(self.ignoreErrorCheckBox, QtCore.SIGNAL('clicked()'), self.preflightIgnoreCommit)
        
        self.connect(self.haltGPSCheckBox, QtCore.SIGNAL('clicked()'), self.preflightHaltGPSCommit)
        self.connect(self.ignoreGPSCheckBox, QtCore.SIGNAL('clicked()'), self.preflightIgnoreGPSCommit)
    #Opens the vehicle and connect through pyro, also starts the update thread    
    def openVehicle(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Vehicle Input Dialog', 'Enter vehicle name:')


        objID = "PYRONAME://"+str(text)
        if ok:
            try:    
                self.object = Pyro.core.getProxyForURI(objID)
                self.guiKey = self.object.setHandshake()
                if self.scene != None:
                    self.object.checkArea(self.mapLatNegFlag*self.mapTopLeftLat, self.mapLongNegFlag*self.mapTopLeftLong, self.mapLatNegFlag*self.mapTopLeftLat-self.mapLat, self.mapLongNegFlag*self.mapTopLeftLong+self.mapLong, self.guiKey)
                if self.object.getHandshake():
                    self.updateThread = UpdateThread()
                    self.connect(self.updateThread, QtCore.SIGNAL('update'),self.update, QtCore.Qt.QueuedConnection)
                    self.updateThread.start()
                
                if self.mapView != None:
                    i = 0    
                    for QGraphicsItem in self.points:
                        self.mapView.scene().removeItem(self.points[i])
                        i+=1
                    self.points = []
                    i = 0
                    for QGraphicsItem in self.obstacles:
                        self.mapView.scene().removeItem(self.obstacles[i])
                        i+=1
                    self.obstacles = []    
                    i = 0
                    for QGraphicsItem in self.lines:
                        self.mapView.scene().removeItem(self.lines[i])
                        i+=1
                    self.lines = []
                    self.waypointTable.show()                
            except Exception, x:
                print ''.join(Pyro.util.getPyroTraceback(x))
                error = QErrorMessage(self)
                error.showMessage("Invalid Vehicle ID")
    #Opens the mapfile and loads it into the gui, also gets the map cordinates
    def openFile(self):
        self.filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home', 'Images (*.png *.tif *.jpg)')
        
        if self.filename != "":    
            pixmap = QPixmap.fromImage(QImage(self.filename))
            self.scene = QGraphicsScene()
            self.scene.addPixmap(pixmap)
            self.mapView.setScene(self.scene)
            self.mapPixelLat = self.scene.sceneRect().height()
            self.mapPixelLong = self.scene.sceneRect().width()
    
            rect= QRectF()
            rect.setWidth(self.scene.sceneRect().width()+self.mapView.verticalScrollBar().sizeHint().width())
            rect.setHeight(self.scene.sceneRect().height()+self.mapView.horizontalScrollBar().sizeHint().height())        
            
            self.mapView.setSceneRect(rect)
            #self.mapView.scene().setItemIndexMethod (QGraphicsScene.NoIndex)
            
            try:
                target = self.filename.split(".")[0]
                corners = []
                f = open(target+".txt","r")
                lines = f.readlines()
                for i in lines:
                    corners.append(float(i))
                topLeftLat = corners[0]
                topLeftLong =  corners[1]
                bottemRightLat =  corners[2]
                bottemRightLong =  corners[3]
                f.close()
 
                self.mapLong = abs(topLeftLong)-abs(bottemRightLong)
                self.mapLat = abs(topLeftLat)-abs(bottemRightLat)
                self.mapTopLeftLong = abs(topLeftLong)
                self.mapTopLeftLat = abs(topLeftLat)
                if topLeftLat<0:
                    self.mapLatNegFlag = -1
                if topLeftLong<0:
                    self.mapLongNegFlag = -1
                if bottemRightLat:
                    self.mapBRLatNegFlag = -1
                if bottemRightLong:
                    self.mapBRLongNegFlag = -1
                self.pixelSizeLat = self.mapLat/self.mapPixelLat       #ratio of pixels to lat
                self.pixelSizeLong = self.mapLong/self.mapPixelLong    #ratio of pixels to long
                
            except:
                self.mapDlg.exec_()    #Gets the top left and bottem right cordinates

            
            if(self.object != None):
                self.object.checkArea(self.mapLatNegFlag*self.mapTopLeftLat, self.mapLongNegFlag*self.mapTopLeftLong, self.mapBRLatNegFlag*(self.mapTopLeftLat+self.mapLat), self.mapBRLongNegFlag*(self.mapTopLeftLong+self.mapLong), self.guiKey)
            self.mapView.centerOn(self.scene.sceneRect().width()/2,self.scene.sceneRect().height()/2)    #Centers the map
            self.mapView.show()
    #The logic behind the Get cordinates window
    def mapDialog(self):
        result = self.mapDlg.getResult()
        topLeftLat = abs(result[0])+(result[1]/60)+(result[2]/3600)
        topLeftLong =  abs(result[3])+(result[4]/60)+(result[5]/3600)
        bottemRightLat =  abs(result[6])+(result[7]/60)+(result[8]/3600)
        bottemRightLong =  abs(result[9])+(result[10]/60)+(result[11]/3600)
                
        if result[0]<0:
            self.mapLatNegFlag = -1
        if result[3]<0:
            self.mapLongNegFlag = -1
        if result[6]<0:
            self.mapBRLatNegFlag = -1
        if result[9]<0:
            self.mapBRLongNegFlag = -1
        target = self.filename.split(".")[0]
        f = open(target+".txt","w")

        f.write(str(topLeftLat*self.mapLatNegFlag)+"\n")
        f.write(str(topLeftLong*self.mapLongNegFlag )+"\n")
        f.write(str(bottemRightLat*self.mapBRLatNegFlag)+"\n")
        f.write(str(bottemRightLong*self.mapBRLongNegFlag)+"\n")
        f.close()
        
        self.mapLong = topLeftLong-bottemRightLong
        self.mapLat = topLeftLat-bottemRightLat
        self.mapTopLeftLong = topLeftLong
        self.mapTopLeftLat = topLeftLat
        
        self.pixelSizeLat = self.mapLat/self.mapPixelLat       #ratio of pixels to lat
        self.pixelSizeLong = self.mapLong/self.mapPixelLong    #ratio of pixels to long
        print "Map Longitude: " + str(self.mapLong)
        print "Map Latitude: " + str(self.mapLat)
    
    
    def typeChange(self, index):
        if(index == 'Go to'):
            self.waypointWindow.stopTimeEdit.setEnabled(False)
        elif (index == 'Stop'):
            self.waypointWindow.stopTimeEdit.setEnabled(True)
        
    #Edits button logic in the waypoint table
    def changeWaypoint(self):
        if (self.object!=None)&(self.waypointTable.isSelected()):
            self.actionType = 1
            latitude = self.waypointTable.receivedTable.item(self.waypointTable.getCurrentIndex(), 0).text()
            longitude = self.waypointTable.receivedTable.item(self.waypointTable.getCurrentIndex(), 1).text()
            type = self.waypointTable.receivedTable.item(self.waypointTable.getCurrentIndex(), 2) .text()
            
            latTarget = float(latitude)
            longTarget = float(longitude)
            
            latTargetD = int(latTarget)
            latTargetM = int((abs(latTarget)-abs(latTargetD)) *60)
            latTargetS = (((abs(latTarget)-abs(latTargetD)) *60) - abs(latTargetM)) * 60
                
            longTargetD = int(longTarget)
            longTargetM = int((abs(longTarget)-abs(longTargetD)) *60)
            longTargetS = (((abs(longTarget)-abs(longTargetD)) *60) - abs(longTargetM)) * 60
            latitude = [float(latTargetD), float(latTargetM), float(latTargetS)]
            longitude = [float(longTargetD), float(longTargetM), float(longTargetS)]
            
            
            #Sets the window fields    
            self.waypointWindow.latDEdit.setText(str(latTargetD))
            self.waypointWindow.latMEdit.setText(str(latTargetM))
            self.waypointWindow.latSEdit.setText(str(latTargetS))
                
            self.waypointWindow.longDEdit.setText(str(longTargetD))
            self.waypointWindow.longMEdit.setText(str(longTargetM))
            self.waypointWindow.longSEdit.setText(str(longTargetS))
            
            self.waypointWindow.typeBox.setCurrentIndex(self.waypointWindow.typeBox.findText(type))
            
            self.waypointWindow.show()

    #Update Groundstation Packet
    def updateGSPacket(self):
        if (self.object!=None):
            self.object.getPacketA()
            self.object.getPacketB()
    #Go to waypoint Button in the waypoint table
    def goToWaypoint(self):
        if (self.object!=None)&(self.waypointTable.isSelected()):
            self.object.setGoTo(int(self.waypointTable.getCurrentIndex()))  
            
    #Append waypoint Button in the waypoint table
    def appendWaypoint(self):
        self.actionType = 2
        self.waypointWindow.show()
        
    #Insert waypoint Button in the waypoint table
    def insertWaypoint(self):
        if self.waypointTable.isSelected():
            self.actionType = 3
            self.waypointWindow.show()
            
    #Remove waypoint Button in the waypoint table
    def removeWaypoint(self):
        if (self.object!=None)&(self.wayList.__len__()!=0)&(self.waypointTable.isSelected()):
            self.object.deleteWaypoint(self.waypointTable.getCurrentIndex())

    #Commits the waypoints to the object
    def commit(self):
        if self.object!= None:
            latitude = self.waypointWindow.getLatitude()
            longitude = self.waypointWindow.getLongitude()
            type = None
            stopTime = self.waypointWindow.getStopTime()
            if stopTime == "":
                stopTime = 0
            if self.waypointWindow.getType() == "Go to":
                    type = 0
            #elif self.waypointWindow.getType() == "Control":
            #        type = 1
            elif self.waypointWindow.getType() == "Stop":
                    type = 2
            #elif self.waypointWindow.getType() == "Orbit":
            #        type = 3
            
            
            if self.actionType == 1:
                self.object.modifyWaypoint(Waypoint(float(latitude), float(longitude),  float(type), float(stopTime)), self.waypointTable.getCurrentIndex())
            if self.actionType == 2:
                self.object.addWaypoint(Waypoint(float(latitude), float(longitude), float(type), float(stopTime)))       
            if self.actionType == 3:
                self.object.insertWaypoint(Waypoint(float(latitude), float(longitude), float(type), float(stopTime)), self.waypointTable.getCurrentIndex())
            
            if self.point!=None:
                self.mapView.scene().removeItem(self.point)
                self.point = None
            self.waypointWindow.hide()
    
    
    #PREFLIGHT Methods
    def preflightIgnoreGPSCommit(self):
         if self.object != None:         
                if(self.ignoreGPSCheckBox.checkState() == Qt.Checked):
                    self.object.setPreflight("IGNORE")
                    self.haltGPSCheckBox.setCheckState(Qt.Unchecked)
                else:
                    self.object.setPreflight("IGNORE")
                    self.ignoreGPSCheckBox.setCheckState(Qt.Checked)
                    self.haltGPSCheckBox.setCheckState(Qt.Unchecked)

    def preflightHaltGPSCommit(self):
        if self.object != None:
                if(self.haltGPSCheckBox.checkState() == Qt.Checked):  
                    self.object.setGPSError("HALT")                  
                    self.ignoreGPSCheckBox.setCheckState(Qt.Unchecked)
                else:
                    self.object.setGPSError("IGNORE")
                    self.ignoreGPSCheckBox.setCheckState(Qt.Checked)
                    self.haltGPSCheckBox.setCheckState(Qt.Unchecked)

                
                
    def preflightIgnoreCommit(self):
        if self.object != None:
            if (self.errorRateEdit.text()!=""):                    
                if(self.ignoreErrorCheckBox.checkState() == Qt.Checked):
                    self.object.setPreflight("IGNORE", int(self.errorRateEdit.text()))
                    self.returnCheckBox.setCheckState(Qt.Unchecked)
                    self.haltCheckBox.setCheckState(Qt.Unchecked)
                else:
                    self.object.setPreflight("IGNORE", int(self.errorRateEdit.text()))
                    self.ignoreErrorCheckBox.setCheckState(Qt.Checked)
                    self.returnCheckBox.setCheckState(Qt.Unchecked)
                    self.haltCheckBox.setCheckState(Qt.Unchecked)

            else:
                self.ignoreErrorCheckBox.setCheckState(Qt.Checked)
                self.returnCheckBox.setCheckState(Qt.Unchecked)
                self.haltCheckBox.setCheckState(Qt.Unchecked)
                error = QErrorMessage(self)
                error.showMessage("Error Rate Not Set")
    def preflightHaltCommit(self):
        if self.object != None:
            if (self.errorRateEdit.text()!=""):
                if(self.haltCheckBox.checkState() == Qt.Checked):  
                    self.object.setPreflight("HALT", int(self.errorRateEdit.text()))                  
                    self.ignoreErrorCheckBox.setCheckState(Qt.Unchecked)
                    self.returnCheckBox.setCheckState(Qt.Unchecked)
                else:
                    self.object.setPreflight("IGNORE", int(self.errorRateEdit.text()))
                    self.ignoreErrorCheckBox.setCheckState(Qt.Checked)
                    self.returnCheckBox.setCheckState(Qt.Unchecked)
                    self.haltCheckBox.setCheckState(Qt.Unchecked)
            else:
                self.ignoreErrorCheckBox.setCheckState(Qt.Checked)
                self.returnCheckBox.setCheckState(Qt.Unchecked)
                self.haltCheckBox.setCheckState(Qt.Unchecked)
                error = QErrorMessage(self)
                error.showMessage("Error Rate Not Set")
    def preflightReturnCommit(self):
        if self.object != None:
            if (self.errorRateEdit.text()!=""):

                if(self.returnCheckBox.checkState() == Qt.Checked):
                    self.object.setPreflight("RETURN", int(self.errorRateEdit.text()))
                    self.ignoreErrorCheckBox.setCheckState(Qt.Unchecked)
                    self.haltCheckBox.setCheckState(Qt.Unchecked)                    
                else:
                    self.object.setPreflight("IGNORE", int(self.errorRateEdit.text()))
                    self.ignoreErrorCheckBox.setCheckState(Qt.Checked)
                    self.returnCheckBox.setCheckState(Qt.Unchecked)
                    self.haltCheckBox.setCheckState(Qt.Unchecked)
            else:
                self.ignoreErrorCheckBox.setCheckState(Qt.Checked)
                self.returnCheckBox.setCheckState(Qt.Unchecked)
                self.haltCheckBox.setCheckState(Qt.Unchecked)
                error = QErrorMessage(self)
                error.showMessage("Error Rate Not Set")
   
    #Commits the circle obstecale to the Object
    def commitCircle(self):
        if self.object!= None:
            latitude = self.circleWindow.getLatitude()
            longitude = self.circleWindow.getLongitude()
            longRadius = abs((self.circleWindow.getRadius()/2)*self.pixelSizeLong)
            latRadius = abs((self.circleWindow.getRadius()/2)*self.pixelSizeLat)
            
            self.object.addCircleObject(latitude, longitude, longRadius, latRadius)

            #FIXME
            #time.sleep(0.1)
            if self.circleObj!=None:
                self.mapView.scene().removeItem(self.circleObj)
                self.circleObj = None
            self.circleWindow.hide()
    
    #Commits the Line obstecale to the Object        
    def commitLine(self):
        if self.object!= None:
            latitude1 = self.lineWindow.getLatitude1()
            longitude1 = self.lineWindow.getLongitude1()
            latitude2 = self.lineWindow.getLatitude2()
            longitude2 = self.lineWindow.getLongitude2()
           
            self.object.addLineObject(latitude1, longitude1, latitude2, longitude2)
            
            if self.lineObj!=None:
                self.mapView.scene().removeItem(self.lineObj)
                self.linePoint = None
                self.lineObj = None
            self.lineWindow.hide()

    def commitRemove(self):
        if self.object!= None:
            latitude1 = self.removeWindow.getLatitude1()
            longitude1 = self.removeWindow.getLongitude1()
            latitude2 = self.removeWindow.getLatitude2()
            longitude2 = self.removeWindow.getLongitude2()
        
            self.object.clearArea(latitude1, longitude1, latitude2, longitude2)
            
            for obj in self.obstacles:
                self.mapView.scene().removeItem(obj)
            
            self.obstacles = []
                
            if self.scene != None:
                self.object.checkArea(self.mapLatNegFlag*self.mapTopLeftLat, self.mapLongNegFlag*self.mapTopLeftLong, self.mapLatNegFlag*self.mapTopLeftLat-self.mapLat, self.mapLongNegFlag*self.mapTopLeftLong+self.mapLong, self.guiKey)
    
  
            if self.removeObj!=None:
                self.mapView.scene().removeItem(self.removeObj)
                self.removeObj = None
            self.removeWindow.hide()
    
    def haltCommit(self):
        if self.object!= None:
            self.object.setHaltMode()

    def resumeCommit(self):
        if self.object!= None:
            self.object.setResumeMode() #Jesse Berger SUPER sorry, we had to...
    
    #sets mode
    def setMode(self):
        if self.object!= None:
            if self.plane!=None :
                self.mapView.scene().removeItem(self.plane)
                self.plane = None
            self.object.setMode(str(self.modeBox.currentText()))
    
    
    #Clears the map of temporary objectes if canceled
    def cancel(self):
        if self.waypointWindow.isVisible() == True:           
            if self.point!=None:
                    self.mapView.scene().removeItem(self.point)
                    self.point = None       
            self.waypointWindow.hide()
        if self.circleWindow.isVisible() == True:           
            if self.circleObj!=None:
                    self.mapView.scene().removeItem(self.circleObj)
                    self.circleObj = None  
            self.circleWindow.hide()
        if self.removeWindow.isVisible() == True:           
            if self.removeObj!=None:
                    self.mapView.scene().removeItem(self.removeObj)
                    self.removeObj = None
            elif  self.removePoint!=None:
                    self.mapView.scene().removeItem(self.removePoint)
                    self.removePoint = None   
            self.removeWindow.hide()
        if self.lineWindow.isVisible() == True:           
            if self.lineObj!=None:
                    self.mapView.scene().removeItem(self.lineObj)
                    self.lineObj = None
            elif  self.linePoint!=None:
                    self.mapView.scene().removeItem(self.linePoint)
                    self.linePoint = None
            self.lineWindow.hide() 
        
    
    #Logic if a mapclick happens only Available if the proper windows are open and the map is declared with real values
    def mapClick(self):
        
        #if ((self.waypointWindow.isVisible() == True)|(self.circleWindow.isVisible() == True)|(self.lineWindow.isVisible() == True))&(self.pixelSizeLat!=0)&(self.pixelSizeLong!=0):
        if  (self.pixelSizeLat!=0)&(self.pixelSizeLong!=0): 
            point = None
            topLeftLat = self.mapTopLeftLat
            topLeftLong = self.mapTopLeftLong
            ev = self.mapView.getCurrentEV()
            posy=ev.y()+self.mapView.verticalScrollBar().sliderPosition()        #possition clicked + slider
            posx=ev.x()+self.mapView.horizontalScrollBar().sliderPosition()      
            
                       
            #Math for where the Accual x and y pixel clicked is
            y = (self.mapView.height()-(self.mapView.sceneRect().height()*self.mapView.matrix().m22()))
            x = (self.mapView.width()-(self.mapView.sceneRect().width()*self.mapView.matrix().m11()))
            
            
            
            #The zoom logic and the -5 pixels to change it drawing in the top left corner to draw in the center because circle size is 10
            targetx = (posx/self.mapView.matrix().m11())-5
            targety = (posy/self.mapView.matrix().m22())-5
            
            
            #Logic for the zoom out
            if (self.mapView.width()-(self.mapView.sceneRect().width()*self.mapView.matrix().m11()))>1:
                targetx = (((posx)/self.mapView.matrix().m11()) - ((x/2 - 2.5)/self.mapView.matrix().m11()))
            if (self.mapView.height()-(self.mapView.sceneRect().height()*self.mapView.matrix().m22()))>1:
                targety = (((posy)/self.mapView.matrix().m22()) - ((y/2 - 2.5)/self.mapView.matrix().m22()))
            
            
            
            item = None
           
            if (self.mapView.width()-(self.mapView.sceneRect().width()*self.mapView.matrix().m11()))>1:
                item = self.mapView.scene().itemAt(targetx, targety+5)
            elif (self.mapView.height()-(self.mapView.sceneRect().height()*self.mapView.matrix().m22()))>1:
                item = self.mapView.scene().itemAt(targetx+5, targety)
            elif ((self.mapView.width()-(self.mapView.sceneRect().width()*self.mapView.matrix().m11()))>1)&((self.mapView.height()-(self.mapView.sceneRect().height()*self.mapView.matrix().m22()))>1):     
                item = self.mapView.scene().itemAt(targetx, targety)
            else:
                item = self.mapView.scene().itemAt(targetx+5, targety+5)
            
            target = 0    
            for i in range(0,self.points.__len__()):
                if item ==self.points[i]:
                    self.waypointTable.selectRow(target)
                    break
                if self.points[i].brush().isOpaque():
                    target+=1
                
            
            #these ifs change the type of object drawn and how to redraw with clicks bases on which windows visible
            if self.waypointWindow.isVisible() == True:    
                if self.point == None:
                    self.point = self.mapView.scene().addEllipse(QRectF(targetx,targety,10,10), QPen(QColor(0, 0, 255)), QBrush(QColor(255, 255, 255)))
                else:
                    self.mapView.scene().removeItem(self.point)
                    self.point = self.mapView.scene().addEllipse(QRectF(targetx,targety,10,10), QPen(QColor(0, 0, 255)), QBrush(QColor(255, 255, 255)))
            
            elif self.circleWindow.isVisible() == True:   
                if self.circleObj == None:
                    if self.circleWindow.radiusEdit.text()=='':
                        self.circleObj = self.mapView.scene().addEllipse(QRectF(targetx,targety,10,10), QPen(QColor(0, 0, 255)), QBrush(QColor(0, 255, 0, 128)))
                    else:
                        radius = self.circleWindow.getRadius()
                        self.circleObj = self.mapView.scene().addEllipse(QRectF((targetx+5)-(radius/2),(targety+5)-(radius/2),radius,radius), QPen(QColor(0, 0, 255)), QBrush(QColor(0, 255, 0, 128)))
                else:
                    self.mapView.scene().removeItem(self.circleObj)
                    if self.circleWindow.radiusEdit.text()=='':
                        self.circleObj = self.mapView.scene().addEllipse(QRectF(targetx,targety,10,10), QPen(QColor(0, 0, 255)), QBrush(QColor(0, 255, 0, 128)))
                    else:
                        radius = self.circleWindow.getRadius()
                        self.circleObj = self.mapView.scene().addEllipse(QRectF((targetx+5)-(radius/2),(targety+5)-(radius/2),radius,radius), QPen(QColor(0, 0, 255)), QBrush(QColor(0, 255, 0, 128)))
            elif self.lineWindow.isVisible() == True:   
                if self.linePoint == None:
                    self.linePoint = self.mapView.scene().addEllipse(QRectF(targetx+3,targety+3,4,4), QPen(QColor(0, 0, 255)), QBrush(QColor(255, 0, 0)))
                elif self.lineObj == None:
                    self.mapView.scene().removeItem(self.linePoint)
                    self.lineObj = self.mapView.scene().addLine(QLineF(self.linePoint.rect().x(), self.linePoint.rect().y(), targetx+5, targety+5), QPen(QColor(255, 0, 0)))    
                else:
                    self.mapView.scene().removeItem(self.lineObj)
                    self.lineObj = None
                    self.linePoint = self.mapView.scene().addEllipse(QRectF(targetx+3,targety+3,4,4), QPen(QColor(0, 0, 255)), QBrush(QColor(255, 0, 0)))
                    self.lineWindow.brLatDEdit.setText('')
                    self.lineWindow.brLatMEdit.setText('')
                    self.lineWindow.brLatSEdit.setText('')
                    
                    self.lineWindow.brLongDEdit.setText('')
                    self.lineWindow.brLongMEdit.setText('')
                    self.lineWindow.brLongSEdit.setText('')                   
            elif self.removeWindow.isVisible() == True:   
                if self.removePoint == None:
                    self.removePoint = self.mapView.scene().addEllipse(QRectF(targetx+3,targety+3,4,4), QPen(QColor(0, 0, 255)), QBrush(QColor(255, 0, 0)))
                elif self.removeObj == None:
                    self.mapView.scene().removeItem(self.removePoint)
                    self.removeObj = self.mapView.scene().addRect(QRectF(self.removePoint.rect().x(), self.removePoint.rect().y(), targetx+5-self.removePoint.rect().x(), targety+5-self.removePoint.rect().y()), QPen(QColor(255, 0, 0)))    
                else:
                    self.mapView.scene().removeItem(self.removeObj)
                    self.removeObj = None
                    self.removePoint = self.mapView.scene().addEllipse(QRectF(targetx+3,targety+3,4,4), QPen(QColor(0, 0, 255)), QBrush(QColor(255, 0, 0)))
                    self.removeWindow.brLatDEdit.setText('')
                    self.removeWindow.brLatMEdit.setText('')
                    self.removeWindow.brLatSEdit.setText('')
                    
                    self.removeWindow.brLongDEdit.setText('')
                    self.removeWindow.brLongMEdit.setText('')
                    self.removeWindow.brLongSEdit.setText('')      
            #adds the objects to the map
            items = self.mapView.scene().items()
    
            for i in range(1,items.__len__()):
                items[i].setParentItem(items[0])
            
            #updates the map
            items[0].update()                
            
            
            #math to change pixles into Lat Long
            if (self.mapView.height()-(self.mapView.sceneRect().height()*self.mapView.matrix().m22()))>1:
                topLeftLat = self.mapTopLeftLat+(((y/2)-2.5)*(self.pixelSizeLat/self.mapView.matrix().m22()))            
            else:
                topLeftLat = self.mapTopLeftLat
            
            if (self.mapView.width()-(self.mapView.sceneRect().width()*self.mapView.matrix().m11()))>1:
                topLeftLong = self.mapTopLeftLong+(((x/2)-2.5)*(self.pixelSizeLong/self.mapView.matrix().m11()))
            else:
                topLeftLong = self.mapTopLeftLong               
            #if self.mapView.matrix().m22()>0:
            latTarget = self.mapLatNegFlag*(topLeftLat-(posy*(self.pixelSizeLat/self.mapView.matrix().m22())))
            longTarget = self.mapLongNegFlag*(topLeftLong-(posx*(self.pixelSizeLong/self.mapView.matrix().m11())))
                   
            #sets the windows values
            latTargetD = int(latTarget)
            latTargetM = int((abs(latTarget)-abs(latTargetD)) *60)
            latTargetS = (((abs(latTarget)-abs(latTargetD)) *60) - abs(latTargetM)) * 60
            
            longTargetD = int(longTarget)
            longTargetM = int((abs(longTarget)-abs(longTargetD)) *60)
            longTargetS = (((abs(longTarget)-abs(longTargetD)) *60) - abs(longTargetM)) * 60
            
            latitude = [float(latTargetD), float(latTargetM), float(latTargetS)]
            longitude = [float(longTargetD), float(longTargetM), float(longTargetS)]
            
            if self.waypointWindow.isVisible():
                self.waypointWindow.latDEdit.setText(str(latTargetD))
                self.waypointWindow.latMEdit.setText(str(latTargetM))
                self.waypointWindow.latSEdit.setText(str(latTargetS))
                
                self.waypointWindow.longDEdit.setText(str(longTargetD))
                self.waypointWindow.longMEdit.setText(str(longTargetM))
                self.waypointWindow.longSEdit.setText(str(longTargetS))
                
            elif self.circleWindow.isVisible():
                self.circleWindow.latDEdit.setText(str(latTargetD))
                self.circleWindow.latMEdit.setText(str(latTargetM))
                self.circleWindow.latSEdit.setText(str(latTargetS))
                
                self.circleWindow.longDEdit.setText(str(longTargetD))
                self.circleWindow.longMEdit.setText(str(longTargetM))
                self.circleWindow.longSEdit.setText(str(longTargetS))
                if self.circleWindow.radiusEdit.text()=='':
                    self.circleWindow.radiusEdit.setText(str(10))
            elif self.lineWindow.isVisible():
                if self.lineObj == None:
                    self.lineWindow.tlLatDEdit.setText(str(latTargetD))
                    self.lineWindow.tlLatMEdit.setText(str(latTargetM))
                    self.lineWindow.tlLatSEdit.setText(str(latTargetS))
                    
                    self.lineWindow.tlLongDEdit.setText(str(longTargetD))
                    self.lineWindow.tlLongMEdit.setText(str(longTargetM))
                    self.lineWindow.tlLongSEdit.setText(str(longTargetS))
                else: 
                    self.lineWindow.brLatDEdit.setText(str(latTargetD))
                    self.lineWindow.brLatMEdit.setText(str(latTargetM))
                    self.lineWindow.brLatSEdit.setText(str(latTargetS))
                    
                    self.lineWindow.brLongDEdit.setText(str(longTargetD))
                    self.lineWindow.brLongMEdit.setText(str(longTargetM))
                    self.lineWindow.brLongSEdit.setText(str(longTargetS))
            elif self.removeWindow.isVisible():
                if self.removeObj == None:
                    self.removeWindow.tlLatDEdit.setText(str(latTargetD))
                    self.removeWindow.tlLatMEdit.setText(str(latTargetM))
                    self.removeWindow.tlLatSEdit.setText(str(latTargetS))
                    
                    self.removeWindow.tlLongDEdit.setText(str(longTargetD))
                    self.removeWindow.tlLongMEdit.setText(str(longTargetM))
                    self.removeWindow.tlLongSEdit.setText(str(longTargetS))
                else: 
                    self.removeWindow.brLatDEdit.setText(str(latTargetD))
                    self.removeWindow.brLatMEdit.setText(str(latTargetM))
                    self.removeWindow.brLatSEdit.setText(str(latTargetS))
                    
                    self.removeWindow.brLongDEdit.setText(str(longTargetD))
                    self.removeWindow.brLongMEdit.setText(str(longTargetM))
                    self.removeWindow.brLongSEdit.setText(str(longTargetS))
        #try:
        #    waypoint = Waypoint(latitude, longitude, "nav")
        #    self.object.addWaypoint(waypoint)
        #except Exception, x:
        #    print ''.join(Pyro.util.getPyroTraceback(x))
        #elif self.mapView.matrix().m22()<0:
        #self.clickedLatEdit.setText(str(self.mapTopLeftLat-(posy*(self.pixelSizeLat*self.mapView.matrix().m22()))))
        #self.clickedLongEdit.setText(str(self.mapTopLeftLong-(posx*(self.pixelSizeLong*self.mapView.matrix().m11()))))
    
    
    def addLine(self):
        self.lineWindow.show()
          
    def addCircle(self):
        self.circleWindow.show()
        
    def removeObstacles(self):
        self.removeWindow.show()
        
    def previewCircle(self):
        if self.circleObj != None:
            radius = self.circleWindow.getRadius()
            self.mapView.scene().removeItem(self.circleObj)
            self.circleObj = self.mapView.scene().addEllipse(QRectF((self.circleObj.rect().x()+(self.circleObj.rect().width()/2))-(radius/2),(self.circleObj.rect().y()+(self.circleObj.rect().height()/2))-(radius/2),radius,radius), QPen(QColor(0, 0, 255)), QBrush(QColor(0, 255, 0, 128)))
          
            items = self.mapView.scene().items()
    
            for i in range(1,items.__len__()):
                items[i].setParentItem(items[0])
            
            items[0].update()
    
    #Pools the object for information    
    def update(self):
        #only tries to read information if the object exists
        if self.object != None:
            wayList = []
            changed = False
            i = 0
            try:
                if self.updateLock.acquire(False):
                    wayList = self.object.getWaypointList()
                    self.updateLock.release()
           
                obstacles = self.object.getObstacleUpdateList(self.guiKey)
                
                
                if self.object.getMode() == "follow":
                    #removes old vehicle
                    if self.plane!=None:
                        self.mapView.scene().removeItem(self.plane)
                    #Draws the Vehicle uses the same math as mapclick just solves for pixel instead of lat long  
                    if((self.pixelSizeLat!=0)&(self.pixelSizeLong!=0)):
                        
                        latitude = float(self.object.getPlanePositionLat())
                        longitude = float(self.object.getPlanePositionLong())
                        heading = float(self.object.getPlaneHeading())
                        if latitude <0:
                            latitude*=-1                   
                        if longitude <0:
                            longitude*=-1
            
                                
                        topLeftLat = self.mapTopLeftLat
                        topLeftLong = self.mapTopLeftLong   
                                                    
                        y = (self.mapView.height()-(self.mapView.sceneRect().height()*self.mapView.matrix().m22()))
                        x = (self.mapView.width()-(self.mapView.sceneRect().width()*self.mapView.matrix().m11()))
                                
                                
                        if (self.mapView.height()-(self.mapView.sceneRect().height()*self.mapView.matrix().m22()))>1:
                            topLeftLat = self.mapTopLeftLat+(((y/2)-2.5)*(self.pixelSizeLat/self.mapView.matrix().m22()))  
                                #print "set Lat"          
                        else:
                            topLeftLat = self.mapTopLeftLat
                                
                        if (self.mapView.width()-(self.mapView.sceneRect().width()*self.mapView.matrix().m11()))>1:
                            topLeftLong = self.mapTopLeftLong+(((x/2)-2.5)*(self.pixelSizeLong/self.mapView.matrix().m11()))
                                #print "set Long"
                        else:
                            topLeftLong = self.mapTopLeftLong   
                                
                        posy = -1*((latitude-topLeftLat)/(self.pixelSizeLat/self.mapView.matrix().m22()))
                        posx = -1*((longitude-topLeftLong)/(self.pixelSizeLong/self.mapView.matrix().m11()))
                        
                                                      
                        targetx = (posx/self.mapView.matrix().m11()) - 16
                        targety = (posy/self.mapView.matrix().m22()) - 16
                                
                                
                                    
                        if (self.mapView.width()-(self.mapView.sceneRect().width()*self.mapView.matrix().m11()))>1:
                            targetx = (((posx)/self.mapView.matrix().m11()) - ((x/2 - 2.5)/self.mapView.matrix().m11()))
                        if (self.mapView.height()-(self.mapView.sceneRect().height()*self.mapView.matrix().m22()))>1:
                            targety = (((posy)/self.mapView.matrix().m22()) - ((y/2 - 2.5)/self.mapView.matrix().m22()))
                        
                        #math to rotat the trucks picture to the headings
                        PI = 3.14159265358979323846
                        myRadiansDouble = (PI/180) * heading
                        
                        xShift = ((-16 * sin(myRadiansDouble)) + (16 * cos(myRadiansDouble))) - 16   
                        yShift = ((16 * cos(myRadiansDouble)) + (16 * sin(myRadiansDouble))) - 16
        
                        self.plane = self.scene.addPixmap(QPixmap.fromImage(QImage("plane.gif")))                     
                        self.plane.setPos(targetx-xShift, targety-yShift)
                        self.plane.rotate(heading)                                    
                        #self.plane = self.mapView.scene().addEllipse(QRectF(targetx,targety,10,10), QPen(QColor(0, 0, 255)), QBrush(QColor(255, 170, 255)))
                        
                        items = self.mapView.scene().items()
                        self.plane.setParentItem(items[0])
                        
                        self.plane.setZValue(5)    #sets the maps 3d typeelevation on the map                
                if(obstacles.__len__()!=0):
                    for element in obstacles:
                        (latitude, longitude, confidence) = element
                        if(confidence>80):
                            #print latitude
                            #print longitude
                            
                            if latitude <0:
                                latitude*=-1                   
                            if longitude <0:
                                longitude*=-1
                
                                    
                            topLeftLat = self.mapTopLeftLat
                            topLeftLong = self.mapTopLeftLong   
                                                        
                            y = (self.mapView.height()-(self.mapView.sceneRect().height()*self.mapView.matrix().m22()))
                            x = (self.mapView.width()-(self.mapView.sceneRect().width()*self.mapView.matrix().m11()))
                                    
                            ratio = (0.00002/self.pixelSizeLat)
                                    
                            if (self.mapView.height()-(self.mapView.sceneRect().height()*self.mapView.matrix().m22()))>1:
                                topLeftLat = self.mapTopLeftLat+(((y/2)-(ratio/4))*(self.pixelSizeLat/self.mapView.matrix().m22()))  
                                    #print "set Lat"          
                            else:
                                topLeftLat = self.mapTopLeftLat
                                    
                            if (self.mapView.width()-(self.mapView.sceneRect().width()*self.mapView.matrix().m11()))>1:
                                topLeftLong = self.mapTopLeftLong+(((x/2)-(ratio/4))*(self.pixelSizeLong/self.mapView.matrix().m11()))
                                    #print "set Long"
                            else:
                                topLeftLong = self.mapTopLeftLong   
                                    
                            posy = -1*((latitude-topLeftLat)/(self.pixelSizeLat/self.mapView.matrix().m22()))
                            posx = -1*((longitude-topLeftLong)/(self.pixelSizeLong/self.mapView.matrix().m11()))
                            
                            
                            
                                                      
                            targetx = (posx/self.mapView.matrix().m11()) - ratio/2
                            targety = (posy/self.mapView.matrix().m22()) - ratio/2
                                    
                                    
                                        
                            if (self.mapView.width()-(self.mapView.sceneRect().width()*self.mapView.matrix().m11()))>1:
                                targetx = (((posx)/self.mapView.matrix().m11()) - ((x/2 + (ratio/4))/self.mapView.matrix().m11()))
                            if (self.mapView.height()-(self.mapView.sceneRect().height()*self.mapView.matrix().m22()))>1:
                                targety = (((posy)/self.mapView.matrix().m22()) - ((y/2 + (ratio/4))/self.mapView.matrix().m22()))
                            
                                                     
                            self.obstacles.append(self.mapView.scene().addRect(QRectF(targetx,targety,ratio,ratio), QPen(QColor(0, 0, 255)), QBrush(QColor(255, 170, 255))))
                    
                    if self.mapView.scene() != None:
                            
                        items = self.mapView.scene().items()
                                
                        for i in range(1,items.__len__()):
                            items[i].setParentItem(items[0])
                        if self.obstacles!= None:        
                            for i in range(0,self.obstacles.__len__()):
                                self.obstacles[i].setZValue(1)               
                        
    

            #self.recEdit.setText("Lat:\n"+str(way.getLatitude()[0]) +"," +str(way.getLatitude()[1]) +"," + str(way.getLatitude()[2])+"\nLong:\n" +str(way.getLongitude()[0]) +"," +str(way.getLongitude()[1]) +"," + str(way.getLongitude()[2]))
         
            #Checks to see if the waypoints have been changed

                if (self.listEquality(wayList)==False):
                    changed = True
                    self.wayList = wayList
                    self.waypointTable.update(wayList)
                    self.waypointTable.receivedTable.setRangeSelected(QTableWidgetSelectionRange(self.selectedID, 0, self.selectedID, 2), True)
                    self.waypointTable.receivedTable.setCurrentCell(self.selectedID, 0)
                    
                if (self.selectedID!= self.waypointTable.receivedTable.currentRow()):
                    changed = True
                    self.selectedID = self.waypointTable.receivedTable.currentRow()
                #removes old vehicle
                if self.vehicle!=None:
                    self.mapView.scene().removeItem(self.vehicle)
                #Draws the Vehicle uses the same math as mapclick just solves for pixel instead of lat long  
                if((self.pixelSizeLat!=0)&(self.pixelSizeLong!=0)):
                
                    latitude = float(self.object.getVehicleLatitude())
                    longitude = float(self.object.getVehicleLongitude())
                    heading = float(self.object.getVehicleHeading())
                    if latitude <0:
                        latitude*=-1                   
                    if longitude <0:
                        longitude*=-1
        
                            
                    topLeftLat = self.mapTopLeftLat
                    topLeftLong = self.mapTopLeftLong   
                                                
                    y = (self.mapView.height()-(self.mapView.sceneRect().height()*self.mapView.matrix().m22()))
                    x = (self.mapView.width()-(self.mapView.sceneRect().width()*self.mapView.matrix().m11()))
                            
                            
                    if (self.mapView.height()-(self.mapView.sceneRect().height()*self.mapView.matrix().m22()))>1:
                        topLeftLat = self.mapTopLeftLat+(((y/2)-2.5)*(self.pixelSizeLat/self.mapView.matrix().m22()))  
                            #print "set Lat"          
                    else:
                        topLeftLat = self.mapTopLeftLat
                            
                    if (self.mapView.width()-(self.mapView.sceneRect().width()*self.mapView.matrix().m11()))>1:
                        topLeftLong = self.mapTopLeftLong+(((x/2)-2.5)*(self.pixelSizeLong/self.mapView.matrix().m11()))
                            #print "set Long"
                    else:
                        topLeftLong = self.mapTopLeftLong   
                            
                    posy = -1*((latitude-topLeftLat)/(self.pixelSizeLat/self.mapView.matrix().m22()))
                    posx = -1*((longitude-topLeftLong)/(self.pixelSizeLong/self.mapView.matrix().m11()))
                    
                                                  
                    targetx = (posx/self.mapView.matrix().m11()) - 11.5
                    targety = (posy/self.mapView.matrix().m22()) - 11.5
                            
                            
                                
                    if (self.mapView.width()-(self.mapView.sceneRect().width()*self.mapView.matrix().m11()))>1:
                        targetx = (((posx)/self.mapView.matrix().m11()) - ((x/2 - 2.5)/self.mapView.matrix().m11()))
                    if (self.mapView.height()-(self.mapView.sceneRect().height()*self.mapView.matrix().m22()))>1:
                        targety = (((posy)/self.mapView.matrix().m22()) - ((y/2 - 2.5)/self.mapView.matrix().m22()))
                    
                    #math to rotat the trucks picture to the headings
                    PI = 3.14159265358979323846
                    myRadiansDouble = (PI/180) * heading
                    
                    xShift = ((-11.5 * sin(myRadiansDouble)) + (11.5 * cos(myRadiansDouble))) - 11.5    
                    yShift = ((11.5 * cos(myRadiansDouble)) + (11.5 * sin(myRadiansDouble))) - 11.5
    
                    self.vehicle = self.scene.addPixmap(QPixmap.fromImage(QImage("truck.gif")))                     
                    self.vehicle.setPos(targetx-xShift, targety-yShift)
                    self.vehicle.rotate(heading)                                    
                    #self.vehicle = self.mapView.scene().addEllipse(QRectF(targetx,targety,10,10), QPen(QColor(0, 0, 255)), QBrush(QColor(255, 170, 255)))
                    
                    items = self.mapView.scene().items()
                    self.vehicle.setParentItem(items[0])

                    self.vehicle.setZValue(4)    #sets the maps 3d elevation on the map
                    
                    #Follows/Centers the map onto the truck
                    if self.followCheck.checkState() == Qt.Checked:
                        self.mapView.centerOn(self.vehicle.x(),self.vehicle.y())
                    
                #Updates the Maps Waypoints And draws the lines
                if((self.pixelSizeLat!=0)&(self.pixelSizeLong!=0)&((self.points.__len__()!=wayList.__len__())|changed)):
                    i = 0
                    for QGraphicsItem in self.points:
                        self.mapView.scene().removeItem(self.points[i])
                        i+=1
                    i = 0                                
    
                    for QGraphicsItem in self.lines:
                        self.mapView.scene().removeItem(self.lines[i])
                        i+=1
                    
    
                    self.points = []
                    self.lines = []
                    i = 0
                    target = 0
                    for Waypoint in wayList: 
                        #if ((wayList[i].getType() != 1) & (wayList[i].getType() != 3)):
                        if (wayList[i].getType() != 3):      
                            latitude = float(wayList[i].getLatitude())
                            longitude = float(wayList[i].getLongitude())
                            
                            #Changes the colors of waypoints
                            if wayList[i].getType() == 0:
                                color = QColor(0, 255, 255)
                            elif wayList[i].getType() == 1:
                                color = QColor(255, 0, 0, 0)
                            elif wayList[i].getType() == 2:
                                color = QColor(255, 0, 0)
                                
         
                            if latitude <0:
                                latitude*=-1                   
                            if longitude <0:
                                longitude*=-1
        
                            #The math to change lat long into pixles
                            topLeftLat = self.mapTopLeftLat
                            topLeftLong = self.mapTopLeftLong   
                                                
                            y = (self.mapView.height()-(self.mapView.sceneRect().height()*self.mapView.matrix().m22()))
                            x = (self.mapView.width()-(self.mapView.sceneRect().width()*self.mapView.matrix().m11()))
                            
                            
                            if (self.mapView.height()-(self.mapView.sceneRect().height()*self.mapView.matrix().m22()))>1:
                                topLeftLat = self.mapTopLeftLat+(((y/2)-2.5)*(self.pixelSizeLat/self.mapView.matrix().m22()))  
                                #print "set Lat"          
                            else:
                                topLeftLat = self.mapTopLeftLat
                            
                            if (self.mapView.width()-(self.mapView.sceneRect().width()*self.mapView.matrix().m11()))>1:
                                topLeftLong = self.mapTopLeftLong+(((x/2)-2.5)*(self.pixelSizeLong/self.mapView.matrix().m11()))
                                #print "set Long"
                            else:
                                topLeftLong = self.mapTopLeftLong   
                            
                            posy = -1*((latitude-topLeftLat)/(self.pixelSizeLat/self.mapView.matrix().m22()))
                            posx = -1*((longitude-topLeftLong)/(self.pixelSizeLong/self.mapView.matrix().m11()))
                                                  
                            targetx = (posx/self.mapView.matrix().m11())-5
                            targety = (posy/self.mapView.matrix().m22())-5
                                                       
                            if (self.mapView.width()-(self.mapView.sceneRect().width()*self.mapView.matrix().m11()))>1:
                                targetx = (((posx)/self.mapView.matrix().m11()) - ((x/2 - 2.5)/self.mapView.matrix().m11()))
                            if (self.mapView.height()-(self.mapView.sceneRect().height()*self.mapView.matrix().m22()))>1:
                                targety = (((posy)/self.mapView.matrix().m22()) - ((y/2 - 2.5)/self.mapView.matrix().m22()))
                            
                            if((self.selectedID == target)&(wayList[i].getType() != 1) & (wayList[i].getType() != 3)):
            
                                self.points.append(self.mapView.scene().addEllipse(QRectF(targetx,targety,10,10), QPen(QColor(0, 255, 0)), QBrush(color)))
                            else:
                                self.points.append(self.mapView.scene().addEllipse(QRectF(targetx,targety,10,10), QPen(QColor(0, 0, 255)), QBrush(color)))
                        if ((wayList[i].getType() != 1) & (wayList[i].getType() != 3)):
                            target+=1
                        i+=1
                    
                    #draws the lines
                    if self.points.__len__()>1:
                        for i in range(0,self.points.__len__()-1):
                            self.lines.append(self.mapView.scene().addLine(QLineF(float(self.points[i].rect().x())+5, float(self.points[i].rect().y())+5, float(self.points[i+1].rect().x())+5, float(self.points[i+1].rect().y())+5), QPen(QColor(255, 0, 0), 0)))
                    
                    
                    #Adds the items and gives them elevation on the map    
                    items = self.mapView.scene().items()
                    
                    for i in range(1,items.__len__()):
                        items[i].setParentItem(items[0])
                        
                    for i in range(0,self.lines.__len__()):
                        self.points[i].setZValue(2)
                    for i in range(0,self.points.__len__()):
                        self.points[i].setZValue(3)
                                    
                    items[0].update() 
                    
                    
                          
                
                #displays all the Headings 
                self.latDisplay.setText(str(round(float(self.object.getVehicleLatitude()),5)))
                self.longDisplay.setText(str(round(float(self.object.getVehicleLongitude()),5)))
                self.headingDisplay.setText(str(round(float(self.object.getVehicleHeading()),2)))
                self.batteryDisplay.setText(str(round(float(self.object.getVehicleVoltage()),2)))
                
                
                if self.actionMetric.isChecked():
                    self.speedDisplay.setText(str(round(0.3048*float(self.object.getVehicleSpeed()),2))+" m/s")
                    self.temperatureDisplay.setText(str(round((5/9)*(float(self.object.getVehicleTemperature())-32),2))+" c")
                    self.rangeDisplay.setText(str(round(0.3048*0.0833333333*float(self.object.getVehicleRange()),2))+" m") 
                    if(self.groundCount == 10):
                        self.altDisplay.setText(str(round(float(self.object.getGroundAlt()),2))+" kPa")
                else:
                    self.speedDisplay.setText(str(round(float(self.object.getVehicleSpeed()),2))+" f/s")
                    self.temperatureDisplay.setText(str(round(float(self.object.getVehicleTemperature()),2))+" f")
                    self.rangeDisplay.setText(str(round(0.0833333333*float(self.object.getVehicleRange()),2))+" f") 
                    if(self.groundCount == 10):
                        self.altDisplay.setText(str(round(.14503773773020923*float(self.object.getGroundAlt()),2))+" PSI")
    
                
                if(self.groundCount == 10):
                       
                    self.latGSDisplay.setText(str(round(float(self.object.getGroundLat()),5)))
                    self.longGSDisplay.setText(str(round(float(self.object.getGroundLong()),5)))
                    self.antennaXDisplay.setText(str(round(float(self.object.getGroundXpos()),2)))   
                    self.headingDisplay.setText(str(round(float(self.object.getGroundHeading()),2)))
                    self.versionDisplay.setText(str(self.object.getGroundVersion()))
                    self.batteryGSDisplay.setText(str(round(float(self.object.getGroundBat()),2))+" V")
                    self.aliveDisplay.setText(str(round(float(self.object.getGroundTimeAlive()),2))+" min")
                    self.groundCount = 0
                self.groundCount += 1
                
                if(self.object.checkNavStatus()):
                    self.navPicture.setPixmap(self.statusOn)
                else:
                    self.navPicture.setPixmap(self.statusOff)
                if(self.object.checkGPSStatus()):
                    self.gpsPicture.setPixmap(self.statusOn)
                else:
                    self.gpsPicture.setPixmap(self.statusOff)
                if(self.object.checkCOMMStatus()):
                    self.commPicture.setPixmap(self.statusOn)
                else:
                    self.commPicture.setPixmap(self.statusOff)
                if(self.object.checkWaypointModeStatus()):
                    self.wayPicture.setPixmap(self.statusOn)
                else:
                    self.wayPicture.setPixmap(self.statusOff)
            except Exception, x:
                if self.updateLock.acquire(False):
                    self.updateLock.release()
                else:
                    self.updateLock.release()
                print ''.join(Pyro.util.getPyroTraceback(x))
                error = QErrorMessage(self)
                error.showMessage("Vehicle Lost")
                self.updateThread.terminate()
        else:
            print "No Object Initilized"
            
    #function to tell if a list is changed:
    def listEquality(self, wayList):
        if self.wayList == None:
            return False
        if self.wayList.__len__()!=wayList.__len__():
            return False
        i = 0
        for Waypoint in wayList:
            if (self.wayList[i].equals(wayList[i])) == False:
                return False
            i+=1
        return True
    
    #Shows the map
    def showMap(self):
        if self.actionMap.isChecked():
            self.mapView.show()
        else:
            self.mapView.hide()
            
    #Hides the map
    def mapClosed(self):
        if self.actionMap.isChecked():
            self.actionMap.setChecked(False)
            
    #Shows the table
    def showTable(self):
        if self.actionTable.isChecked():
            self.waypointTable.show()
        else:
            self.waypointTable.hide()
    #Prefrences Checks
    def setEnglishUnits(self):
        if self.actionMetric.isChecked():
            self.actionMetric.setChecked(False)
        else: 
            self.actionMetric.setChecked(True)   
    def setMetricUnits(self):
        if self.actionEnglish.isChecked():
            self.actionEnglish.setChecked(False)    
        else:
            self.actionEnglish.setChecked(True)   
    #Hides the table
    def tableClosed(self):
        if self.actionTable.isChecked():
            self.actionTable.setChecked(False)
    
    #how to get the center of the screen       
    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
   
    def saveWaypoints(self):
        if self.object!= None:
            fname = QtGui.QFileDialog.getSaveFileName(self, 'Save Waypoints', '/home')
            wayList = self.object.getWaypointList()
            
            f = open(fname,"w")

            for Waypoint in wayList:
                if (Waypoint.getType()!= 1)&(Waypoint.getType()!=3):
                    f.write(str(Waypoint.getLatitude()) + " " + str(Waypoint.getLongitude()) + " " + str(Waypoint.getType()) + " " + str(Waypoint.getStopTime()) + "\n")
            f.close()
    def loadWaypoints(self):
        if self.object!= None: 
            self.object.clearWaylist()
            fname = QtGui.QFileDialog.getOpenFileName(self, 'Load Waypoints', '/home')
                
            f = open(fname,"r")
            lines = f.readlines()
            for i in lines:
                waypoint = i.split(" ")
                latitude = waypoint[0]
                longitude =  waypoint[1]
                type =  waypoint[2]
                stopTime =  waypoint[3]
                self.object.addWaypoint(Waypoint(float(latitude), float(longitude), float(type), float(stopTime)))    
            f.close()
        
    #shutdown event
    def closeEvent(self, closeEvent):
        self.updateThread.terminate()
        self.waypointWindow.close()
        self.lineWindow.close()
        self.circleWindow.close()
        self.mapView.close()
        self.waypointTable.close()
        self.removeWindow.close()
        if self.object!= None:
            self.object.guiUnsubscribe(self.guiKey) #support for multiple guis, Frees Navigaytor
#starts the system
app = QApplication(sys.argv)

qb = MainWindow()
qb.show()
sys.exit(app.exec_())
