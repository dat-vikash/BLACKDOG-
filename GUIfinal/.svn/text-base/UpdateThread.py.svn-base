from PyQt4.QtCore import *
from PyQt4.QtGui import *

class UpdateThread(QThread):
    def __init__ (self):
        QThread.__init__(self)
       
       #updates ever 1/2 second
    def run(self):
        while 1:           
            self.emit(SIGNAL('update'))
            self.msleep(500)
            
