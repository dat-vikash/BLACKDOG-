#Embry Riddle Aeronautical University
#SE451
#Senior Design, Spring 2008
#Virtual Python Object
#Jimmy Haviland
#havil84d@erau.edu

import Pyro.core
import Pyro.naming
import time

from Communications import Communications
from Pyro.naming import NameServerStarter
from Waypoint import Waypoint
from ControlTeam.Navigator import Navigator
from ControlTeam.ObstacleManager import ObstacleManager


class ObjectGen(Pyro.core.ObjBase):
    
    def __init__ (self, name = "Object", port = 0):
        Pyro.core.ObjBase.__init__(self)
                                   
        #instatiates an instace of communication and starts it        
        self.comm = Communications()
        self.serverName = "ObjectGen"
        self.PORT = port
        
        #if invalid returns 0
        self.status = self.comm.initialize(self, self.PORT)            
        self.comm.start()       
        #instantiate an empty waypoint list
                                        
        #instantiate empty packets
        self.vehiclePacket = []
        self.groundPacket1 = []
        self.groundPacket2 = []
        self.wayListForValidating = []
        
        #instantiate variables to 0 so errors do not occur when GUI calls them
        self.curWaypoint = None
        self.isHandshaken = None
        self.targetLat = 0
        self.targetLong = 0
        self.planeLat = 0
        self.planeLong = 0
        self.planeHeading = 99
        self.mode = "waypoint"
        self.navStat = True
        self.gpsStat = True
        self.commStat = True
        self.GPSErrorType = ""

    navigator = None
    wayList = []
    #sends the handshake to comm
    #sets the flags to true     
    def setHandshake(self):
        self.comm.handshake()      
        self.isHandshaken = True       
        if self.navigator == None:
            self.navigator = Navigator(self)
            self.wayList = self.navigator.waylist 
        return self.navigator.obstacleManager.subscribe() 
           
    def completeHandShake(self):
        self.shakeFlag = False
            
    def getHandshake(self):
        return self.isHandshaken
    
    #returns the lost packet information/status
    def getLostPacketStats(self):
        return self.comm.getLostPacketStats()
    

    def getPacketB(self):
        self.comm.getPacketB()
        
    def getPacketA(self):
        self.comm.getPacketA()   

    def setTelError(self,error):
        self.packetError = error;

    def getTelError(self):
        return self.packetError
        
    #Method called by comm to push a packet to the object 
    #packetNum determines which packet it is
    #Then it copys that packet list to be stored by the object   
    def pushPacket(self, packetNum, dataList):
        if(packetNum == 1):
            self.groundPacket1 = dataList 
            #print "packet A stuff:" + str(dataList['battery_voltage'])                      
        if(packetNum == 2):
            self.groundPacket2 = dataList            
            
        if(packetNum == 3):            
            self.vehiclePacket = dataList
            #print "packet B stuff: " + str(dataList['latitude'])
        
        if(packetNum == 4):    #waylist for validating
            self.wayListForValidating = dataList
        #pushes information to navigator every time a packet is pushed
        try:
            self.navigator.obstacleManager.interpretTruckSensors(self.vehiclePacket['latitude'], self.vehiclePacket['longitude'], self.vehiclePacket['heading'], self.vehiclePacket['range'])
        except Exception, e:
            print e
            
    #method to validate waylists   
    def ValidateWaylist(self):
        self.tmpSystemList = self.getWaypointList()        #get system waylist
        self.tmpCorrectCount = 0                            #count of correct waylists
        self.tmpTruckCount =  (self.wayListForValidating).__len__()  #size of truck list
        for w in tmpSystemList:                                    #test if waypoints are equal
            if(w.equals(self.wayListForValidating.pop(tmpTruckCount=tmpTruckCount - 1))):
                self.tmpCorrectCount = self.tmpCorrectCount +1
                
        if(self.tmpCorrectCount!=(self.getWaypointList()).__len__()  ):    #if correct waypoints match size of list
            return False
        else:
            return True   
            
        
            
            
#####Getter methods for GROUND STATION#########   

    #if the packet is empty we return dummy variables
    #when the packet is filled by comm we return the actual numbers     
    def getGroundVersion(self):
        if self.groundPacket1 == []:
            return 0
        return str(self.groundPacket1['version'])    
    def getGroundTimeAlive(self):        
        if self.groundPacket1 == []:
            return 0
        return str(self.groundPacket1['alive'])
    def getGroundBat(self):
        if self.groundPacket1 == []:
            return 0
        return str(self.groundPacket1['battery_voltage'])
    def getGroundLat(self):
        if self.groundPacket2 == []:
            return 0
        return str(self.groundPacket2['latitude'])
    def getGroundLong(self):
        if self.groundPacket2 == []:
            return 0
        return str(self.groundPacket2['longitude'])
    def getGroundAlt(self):
        if self.groundPacket2 == []:
            return 0
        return str(self.groundPacket2['air_pressure'])
    def getGroundXpos(self):
        if self.groundPacket2 == []:
            return 0
        return 0
        #return str(self.groundPacket2['xpos'])
        #hardware has not yet finished this functionality       
    def getGroundYpos(self):
        if self.groundPacket2 == []:
            return 0
        return 0
        #return str(self.groundPacket2['ypos'])
        #hardware has not yet finished this functionality
    def getGroundHeading(self):
        if self.groundPacket2 == []:
            return 0
        return (str(self.groundPacket2['heading']))
                    
        
######Getter methods for VEHICLE###########

    #if the packet is empty we return 0
    #when the packet is filled by comm we return the actual numbers         
    def getVehicleLatitude(self):
        if self.vehiclePacket == []:
            return 0
        if str(self.vehiclePacket['latitude']) == '^':
            return 00
        return str(self.vehiclePacket['latitude'])         
    def getVehicleLongitude(self):
        if self.vehiclePacket == []:
            return 0 
        if str(self.vehiclePacket['longitude']) == '^':
            return 00       
        return str(self.vehiclePacket['longitude']) 
    def getVehicleSpeed(self):
        if self.vehiclePacket == []:
            return 0
        return str(self.vehiclePacket['speed'])  
    def getVehicleHeading(self):
        if self.vehiclePacket == []:
            return 0
        return str(self.vehiclePacket['heading'])  
    def getVehicleMode(self):
        if self.vehiclePacket == []:
            return 0
        return str(self.vehiclePacket['mode'])
    def getVehicleTemperature(self):
        if self.vehiclePacket == []:
            return 0
        return str(self.vehiclePacket['temperature'])  
    def getVehicleVoltage(self): 
        if self.vehiclePacket == []:
            return 0
        return str(self.vehiclePacket['battery_voltage'])  
    def getVehicleRange(self): 
        if self.vehiclePacket == []:
            return 0
        return str(self.vehiclePacket['range'])     
    
        
        
###################iteration5##################### 
 #Adds the waypoint to the list
    #Sets the current waypoint to the latest  
    #Validates the waypoint with Control
    #Sends the updated waypoint list to comm
    def addWaypoint(self, waypoint):                  
        self.curWaypoint = waypoint
        self.wayList.append(self.curWaypoint)
              
        #self.comm.getPacketB()        
        #print self.groundPacket2['latitude']               
                          
     #returns the current waypoint   
    def getWaypoint(self): 
        return self.curWaypoint    
     
    #sends the entire waypoint list to comm to be updated to truck
    def sendWaylist(self, list = None):
        if list == None: list = self.wayList[:]
        #HOTFIX FOR TRUCK ISSUE
        #if (len(list)>0 and list[0].getLatitude()!=0):
        #    list.append(list[-1])
        self.comm.addWaypoint(list)
        
    #deletes a waypoint by index number    
    def deleteWaypoint(self,index):
        print "deleting waypoint"
        print len(self.wayList)
        self.wayList.remove(index)        
    
    #clears the entire waylist
    def clearWaylist(self):        
        self.wayList.clear()    
        
    #modifys a waypoint by deleteing the old vale
    #and reinserting the new given value into the olds place
    def modifyWaypoint(self,waypoint,index):
        print "modify waypoint"
        print len(self.wayList)
        self.wayList.update(index,waypoint)  
    
    #inserts a waypoint AFTER the index 
    #moves all other waypoints down the waypoint list
    def insertWaypoint(self, waypoint, index):
        print "inserting waypoint"
        print len(self.wayList)        
        self.wayList.insert(index, waypoint)
        
###################iteration6#####################
    
    #sets the mode
    #calls the method to set the mode in control
    def setMode(self,string):
        self.mode = string
        self.navigator.mode = string      
    
    #returns the mode from control 
    def getMode(self):
        return self.navigator.mode
        #return self.mode

    #returns the current waypoint list
    def getWaypointList(self):        
        return self.wayList[:]    
       
    #return the Obstacle Manager
    def getObstacleManager(self):
        return self.navigator.getObstacleManager()
    
    #returns the Obstacle grid 
    def getObjectGrid(self,lat,long,lat2,long2):
        return self.navigator.getObsManager().getGrid(lat,long,lat2,long2)
   
    
    #allows to add a Line to the ObstacleManager
    def addLineObject(self,lat,long,lat2,long2):
        self.navigator.obstacleManager.addLine(lat, long, lat2, long2)
        #Calls controls method to add line object
        
    #allows to add a Circle to the ObstacleManager
    def addCircleObject(self,lat,long, radiusLong, radiusLat):
        self.navigator.obstacleManager.addCircle(lat, long, radiusLat, radiusLong)        
        #Calls controls method to add circle object
        
    #returns the update queue from control to the caller
    def getObstacleUpdateList(self, key):        
        return self.navigator.obstacleManager.getUpdates(key)
    
    def checkArea(self, degreesLat, degreesLong, degreesLat2, degreesLong2, key):
        self.navigator.obstacleManager.checkArea(degreesLat, degreesLong, degreesLat2, degreesLong2, key)
        
    def clearArea(self, degreesLat, degreesLong, degreesLat2, degreesLong2):
        self.navigator.obstacleManager.clearArea(degreesLat, degreesLong, degreesLat2, degreesLong2)

    def unsubscribe(self, key):
        self.navigator.obstacleManager.unsubscribe(key) 
        
    def setHaltMode(self):   
        self.comm.setHaltMode()
        
    def setResumeMode(self):
        self.navigator.resume()
        print "Dmitri called me"
        self.comm.setWaypointMode()
    
    #sends the truck to the waypoint index    
    def setGoTo(self, index):
        print index
        self.navigator.goToUserWaypoint(index)
    
     
    
#########  BLACKBIRD METHODS  ########### 
    
#sets the plane position
    def setPlanePosition(self,lat,long, heading):
        self.planeLat = lat
        self.planeLong = long
        self.planeHeading = heading 
    
#returns the plane's position to whoever calls it
    def getPlanePositionLat(self):       
        return self.planeLat
           
    def getPlanePositionLong(self):
        return self.planeLong
        
    def getPlaneHeading(self):
        return self.planeHeading
        

#BLACKBIRD add Waypoints and Obstacles 
    def BBaddWaypoint(self,waypoint):
        print "BB has added a waypoint"
        self.addWaypoint(waypoint) 
        
    def BBaddLineObstacle(self,lat,long,lat2,long2):
        print "BB has added a LINE obstacle"
        self.navigator.obstacleManager.addLine(lat, long, lat2, long2)
        
    def BBaddCircleObstacle(self,lat,long, radiusLong, radiusLat):
        print "BB has added a CIRCLE obstacle"
        self.navigator.obstacleManager.addCircle(lat, long, radiusLat, radiusLong)        
    
    def getStatus(self):
        return self.status
        
    def setPreflight(self,type,errorRate=100):
        
        self.comm.setPreFlight(type,errorRate)
        self.error = self.comm.checkErrorRate()
        self.errorType = type
        print "ERROR IS: " 
        print self.error
        if(self.error):
            if(self.errorType=="HALT"):
                self.setHaltMode()
            elif(self.errorType=="IGNORE"):
                pass
            elif(self.errorType=="RETURN"):               
                #self.HOME = Waypoint(self.groundPacket2['latitude'], self.groundPacket2['longitude'],1,0)       
                self.HOME = self.wayList[0]    
                self.clearWaylist()
                self.addWaypoint(self.HOME)
    
    #Similiar to Preflight, but for GPS ERROR
    #Error Types: HALT, IGNORE
    def setGPSError(self, type):
        self.GPSErrorType = type
        print "GPS Error Type Set: " + str(self.GPSErrorType)
        
    #Acknowledges that there was a GPS error and takes correct action
    #Action is determined by GUI
    def AckGPSError(self):        
        if(self.GPSErrorType == "HALT"):
            self.setHaltMode()
        elif(self.GPSErrorType=="IGNORE"):
            pass        
        
  
    #set by other layers for the status lights
    def setNavError(self,error):        
        self.navStat = not error  
    def setCOMMStatus(self,status):
        self.commStat = status   
    def setGPSStatus(self,status):
        self.gpsStat = status  
        if(status):
           # print "----GPS ERROR is---- "
           # print self.gpsStat     
           pass        
#methods for GUI status lights
    def checkNavStatus(self):
        #method by navigator team to check status        
        return self.navStat
       
    def checkGPSStatus(self):
        #method by comm to check gps status
        return self.gpsStat
    def checkCOMMStatus(self):
        #method by comm to check COMM status
        return self.commStat 
        
    def checkWaypointModeStatus(self):
        if(self.comm.getCurrentTruckMode() == "%1"):
            return True
        else:
            return False    
        
    def guiUnsubscribe(self, key):
        self.navigator.obstacleManager.unsubscribe(key) 
             

