#Embry Riddle Aeronautical University
#SE451
#Senior Design, Spring 2008
#Initialize the Object on the PYRO nameserver
#Jimmy Haviland
#havil84d@erau.edu

import Pyro.core
import Pyro.naming
import time 
from Waypoint import Waypoint 
import thread,os,sys
from Pyro.naming import NameServerStarter
from threading import Thread
#!!! Switch import statement for Control
#from VGO.ObjectGenNOc import ObjectGenNOc
from VGO.ObjectGen import ObjectGen
from time import sleep
import serial

import sys
from PyQt4 import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Console import Ui_Console


class PyroNS(Thread):
    #Starts a NameServer
    def __init__(self):
        Thread.__init__(self)
        self.nsStarter = NameServerStarter()
    def run(self):
        self.nsStarter.start()
        
    def waitUntilStarted(self):
        return self.nsStarter.waitUntilStarted()
    
    def stop(self):
        self.nsStarter.shutdown()
        pass
    
class PyroObjectServer(Thread):
    #starts the object
    def __init__(self,object,pyroName):
        Thread.__init__(self, name = "Pyro Daemon for " + pyroName)
        Pyro.core.initServer()
        self.setDaemon(True)
        self.nameServer = Pyro.naming.NameServerLocator().getNS()
        self.daemon = Pyro.core.Daemon()
        self.daemon.useNameServer(self.nameServer)
        self.uri=self.daemon.connect(object, pyroName)
        print 'VGO hosted on Pyro as "' + pyroName + '"'
        self.start()
    def run(self):
        self.daemon.requestLoop()
        
class MainWindow(QMainWindow, Ui_Console):

    def __init__(self, parent = None):   
        QWidget.__init__(self, parent)
        self.setupUi(self)        
        self.object = None
        
        self.serialBox.addItems([str(x+1) for x in filter(self.testPort, range(9))])       
        
        self.connect(self.startButton, SIGNAL('clicked()'), self.start)
        self.connect(self.exitButton, SIGNAL('clicked()'), self.quit)

        
    def start(self):
        if (self.nameEdit.text()!=""):                   
            selectedPort = int(self.serialBox.currentText())-1
            self.object = ObjectGen(port = selectedPort)
            if self.object.status == 0:
                print "Cannot start VGO instance: COM" + str(selectedPort+1) + " is not available"
                return
            pyroNS.waitUntilStarted()
            self.myServer = PyroObjectServer(self.object, str(self.nameEdit.text()))
            self.startButton.hide()
        else:
            print "Cannot host VGO instance on Pyro with a blank name"


    def quit(self):
        try:
            self.object.navigator.close()
            
        except AttributeError:
            pass
        sys.exit(app.exec_())        
        
    def testPort(self, portNumber):
        try:
            self.ser = serial.Serial(portNumber)     #reference to serial port object
            self.ser.close()
            return True
        except serial.serialutil.SerialException:
            return False                                       

        
        
pyroNS = PyroNS()
pyroNS.start()

app = QApplication(sys.argv)
qb = MainWindow()
qb.show()
   
sys.exit(app.exec_())

