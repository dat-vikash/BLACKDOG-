from PyQt4.QtCore import *
from PyQt4.QtGui import *


class MapViewer(QGraphicsView):
    def __init__(self, parent=None):
        QGraphicsView.__init__(self, parent)
        
        self.resize(QSize(QRect(0,0,445,445).size()).expandedTo(self.minimumSizeHint()))
        
        self.setWindowTitle('Map View')
        
        self.gridlayout = QGridLayout()
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        self.gridlayout.addWidget(self,0,0,1,1)
        self.move(10,300)

        self.currentEV = None
        self.zoomScale = 0.05


    def mousePressEvent(self, ev):
        self.currentEV = ev
        self.emit(SIGNAL('mouseClick'))
        
    def wheelEvent (self, ev):
        #120 is the value to divide the ammount of mouse wheels to get the accual ammount of "clicks" of the wheel
        #120 is the mousewheel scroll constant
        self.scale(1+(self.zoomScale*ev.delta()/120), 1+(self.zoomScale*ev.delta()/120))

    
    def getCurrentEV(self):
        return self.currentEV

    def closeEvent(self, closeEvent):
        self.emit(SIGNAL('closed'))
