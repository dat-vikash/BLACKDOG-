#KDE - 3/26/08  Added a method to get the status of handshake
#Embry Riddle Aeronautical University
#SE451
#Senior Design, Spring 2008
#Communications Layer between hardware and software
#Vikash dat
#datcc1@erau.edu

import serial, time, math, logging
from threading import Thread 
from Waypoint import Waypoint
import Packet

class Communications(Thread): 
       
   def __init__ (self, mode="REAL", debug=False): 
       Thread.__init__(self, name="Communications Thread") 
       self.debug = debug                     #set debug mode
       self.initialized = False               #initial status of communications thread
       self.mode = mode                       #indicates mode 
       self.log = logging.getLogger("CommLogger")
       self.log.addHandler(logging.FileHandler("Blackdog_com.log"))
       self.serPort = SerPort(self.log)       #start and acquire a serial port
       self.firstWaypoint = True
       self.orginWaypoint = None
        
   def initialize(self, vgo, portNumber=0 ): 
       self.VGO = vgo                         #reference to VGO
       
       if(self.serPort.setPort(portNumber)):            
           
           
           self.running = True            #set state of thread 
           self.waitingList = []                    #queue of requests from software 
           self.hardwareLink = HardwareLink()
           self.systemLink = SystemLink()
           self.hardwareLink.initialize(self.serPort, self)    #acquire hardware
           self.systemLink.initialize(self.serPort, self)        #acquire link to software system 
           self.serPort.start()            #start port 
           self.shake_flag = False        # no initialization handshake 
           self.handShakeComplete = False  
           self.packetInfo   = []             # String of packet information 
        
           self.initialized = True         #set state of thread to READY
           self.waypointCount = 0         #initial count of waypoints sent
           self.badPacketCount = 0        #number of bad packets recieved
           self.packetRate= 0                # rate set by Control/GUI
           self.wayListCount=0                # keeps count of waypoints in waylist
           self.errorRateType = ""            #type of action to be taken on set error rate
           self.definedErrorRate = 0        # defined error rate from gui
           self.status_varLat = 0            #list of status variables for GPS
           self.status_varLong = 0
          # self.old_stats = {}            #previous list of status variables for GPS
           self.old_statsLat = 1        #initialize status variables
           self.old_statsLong =1
           self.timeCounter = time.clock()            #timer for polling
           self.varAntennaSide = 0            #indicator for left/right antenna position
           self.theta = 0                    #angle to face antenna
       else:
           #print "Invalid Port Number"
           return 0
        
            
   def run(self): 
       while(not self.initialized): 
           time.sleep(0.1) 
       #self.hardwareLink.start()        #start hardware thread
       self.systemLink.start()         # start software thread
       
       while self.running:
           
           #update antenna information
           
           self.varRun = float(self.VGO.getVehicleLatitude()) - float(self.VGO.getGroundLat())    #get horizontal component
           if(self.varRun<0):    #right side
               self.varAntennaSide=1
               
           self.varRise = float(self.VGO.getVehicleLongitude()) - float(self.VGO.getGroundLong()) #get vertical component
           try:
               self.theta = math.atan(self.varRise/self.varRun)/10            #calculate angle between antenna and truck
           except ZeroDivisionError:
               pass
           if (self.theta > 1):
               self.setLine('c')          #alert hardware groundstation for antenna change
           
           #update timer
           if((time.clock() - self.timeCounter)>90):
               #self.getPacketA()
               #self.getPacketB()
               #not complete
               self.timeCounter = time.clock()
                          
           
           #GPS FAILURE#######
           if(self.waypointCount>0):
               self.VGO.setGPSStatus(True)
                #check for lat/long = 0
               if self.status_varLat == 0:
                   #error
                   self.VGO.setGPSStatus(False)
                   self.VGO.AckGPSError()
               else:
                   self.VGO.setGPSStatus(True)
               if self.status_varLong == 0:
                   #error
                   self.VGO.setGPSStatus(False)
                   self.VGO.AckGPSError()
               else:
                   self.VGO.setGPSStatus(True)
               if (float(self.status_varLat) - float(self.old_statsLat)) == 0.00:
                   #error
                   self.VGO.setGPSStatus(False)
                   self.VGO.AckGPSError()
               else:
                   self.VGO.setGPSStatus(True)
               if (float(self.status_varLong) - float(self.old_statsLong)) ==0.00:
                   #error
                   self.VGO.setGPSStatus(False)
                   self.VGO.AckGPSError()
               else:
                   self.VGO.setGPSStatus(True)
               if self.checkErrorRate():
                   self.VGO.setCOMMStatus(False)
               else:
                   self.VGO.setCOMMStatus(True)
           
           time.sleep(0.1)
            
   def notify(self):
       #initialize variables
       self.choice= None
       self.info = None
       try:
           (self.choice, self.info) = Packet.decodePacket(self.hardwareLink.getLine(), self.wayListCount)   #get packet information
       except Exception:
           pass   
       
       if(self.choice == 0 ):                #check for bad packet
           self.badPacketCount = self.badPacketCount + 1
           self.VGO.setTelError(self.info)                #sends error packet to VGo
           print "BAD PACKET SUCKA!"
           
       while(self.shake_flag):                        #check for handshake 
            
           if(self.choice == 1):    #handshake acknowledged 
               self.shake_flag = False; 
               self.VGO.completeHandShake() 
               self.handShakeComplete = True               
           time.sleep(0.1) 
       
       #after handshake, system will just push to object 
       if(self.choice == 2):                        #Packet A
                    
           self.packetInfo = self.info 
           self.VGO.pushPacket(1,self.info) 
       elif(self.choice ==3):                        #Packet B 
           self.packetInfo = self.info 
           self.VGO.pushPacket(2,self.info)
       elif(self.choice ==4):                    #vehicle packets 
           self.packetInfo = self.info 
           self.setOldstats(self.status_varLat,self.status_varLong)
           self.setNewStats(self.info)
           self.VGO.pushPacket(3,self.info)
       elif(self.choice==5):
           self.VGO.pushPacket(4,self.info)
       elif(self.choice==6):                    #antenna packet
           #update anntena information
           varSide = 0
           self.varRun = float(self.VGO.getVehicleLatitude()) - float(self.VGO.getGroundLat())    #get horizontal component
           if(self.varRun<0):    #right side
               self.varAntennaSide=1
               
           self.varRise = self.VGO.getVehicleLongitude() - self.VGO.getGroundLong() #get vertical component
           try:
               self.theta = math.atan(self.varRise/self.varRun)/10            #calcuate angle between antenna and truck
           except ZeroDivisionError:
               pass

           self.setLine(self.theta)
                  
           
                   
              
   def setLine(self, line):                 #set input to VGS
         self.waitingList.append(line)     
   
   def setNewStats(self,stats):
       self.status_varLat = stats['latitude']
       self.status_varLong = stats['longitude']
       
   def setOldstats(self,lat,long):
       self.old_statsLat = lat
       self.old_statsLong = long
       
   def getList(self):
       return self.waitingList    
       
   def getLostPacketStats(self):
       try:
           ret =  self.badPacketCount/self.serPort.getCurrentPacketCount()
       except ZeroDivisionError:
            ret = 0
       return ret
              
        
   def getLine(self):                     #gets current line from VGS
       self.T_hardwareline.getLine() 
    
   def stop(self):                         #set thread to ready state
       self.running = False    
       self.ser.close()            #close port
       
    
   #gets double version#, timealive     
   def getPacketA(self):                 
       self.waitingList.append("a") 

    #returns PacketB information from VGS
   def getPacketB(self): 
       self.waitingList.append("b") 
     
       
        
   def handshake(self):        #send a '~' and wait for a '~' 
       self.setLine('~') 
       self.shake_flag = True        #handshake started
              
   def getIsHandshaken(self):
   	   return self.handShakeComplete 
             
   def addWaypoint(self, wayList):        #add waypoint list
       self.wayListCount=0
        #If this is the first waypoint we send, do not send a carrot.
       string = Packet.createWaypointPacket(wayList, self.firstWaypoint)
       #for waypoints in wayList:
       self.wayListCount = len(wayList)
           
       self.firstWaypoint=False
        
       
      
       
       if(self.waypointCount > 0): 
           string += Packet.getCurrentMode()
       else: 
           string += Packet.setInitalMode()
       self.setLine(string) 
     
       self.waypointCount=self.waypointCount + 1 
       
   def setWaypointMode(self):    #sets the truck to waypoint mode %1 
       return (Packet.setWaypointMode()) 
   
   def setHaltMode(self):        #sets the truck to halt mode
       self.setLine(Packet.setHaltMode())
    
   def getWayListTruck(self):
       self.setLine('w')
       
   def setPreFlight(self,type,errorRate):
       self.errorRateType = type
       self.definedErrorRate = errorRate
       

   def checkErrorRate(self):
       if (self.getLostPacketStats()<=self.definedErrorRate):
           return False
       else:
           return True
     
   def getCurrentTruckMode(self):
       return Packet.getCurrentMode() 
        
# Thread that listens to the hardware (VGS)  
        
class HardwareLink(Thread): 
    
   def __init__ (self): 
     Thread.__init__(self, name="Comm:Hardware Link") 
 
    
   def initialize(self,  port, comm, debug = False):        
       self.debug = debug             #set debug mode
       self.running = True            #set the state of the thread 
       self.serPort = port            #get reference to port 
       self.serPort.subscribe(self)    #subscribe to serial port events 
       self.currentLine = ""             
       self.comm = comm                 #reference to communications 
        
#   def run(self):             #listen to hardware  and foward data sent from hardware 
#       
#       while self.running: 
#          pass 
#          time.sleep(0.1) 
       
   def notify(self):                 #subscriber method
       self.currentLine =self.serPort.getCurrentLine()    #get line 
       self.comm.notify()                 #notify communications
       
    
   def getLine(self):                 #gets current line
       return self.currentLine     

#Thread that listens for communication up from software        
        
class SystemLink(Thread): 
   def __init__ (self): 
       Thread.__init__(self, name="Comm:SoftwareLink") 
     
       
   def initialize(self, port, comm, debug=False):        
       self.debug = debug 
       self.running = True            #set the state of the thread 
       self.serPort = port            #get reference to port 
       self.currentLine = "" 
       self.comm = comm
       self.waitinglist = self.comm.getList()         #list of waiting instructions to be sent
      
         
    
   #check list and 
   def run(self): 
       while self.running:
           self.waitinglist = self.comm.getList() #refresh list
           
           if self.waitinglist.__len__() > 0:     #while queues are in list
               if (self.waitinglist[0] =='~'):
                   self.setLine(self.waitinglist.pop(0))
               elif(self.comm.getIsHandshaken()):
                    line = self.waitinglist.pop(0) #LIFO caused problems; using FIFO --Cory
                    self.setLine(line) 
           time.sleep(0.1) 
         
    
   def setLine(self, line): 
       self.currentLine = line; 
       self.serPort.setLine(line) 

#Thread that handles duplexed serial port
    
class SerPort(Thread): 
   def __init__ (self,log, debug = False): 
       Thread.__init__(self) 
       self.debug = debug 
       self.running = True         #state of thread
       self.listeners = []         #list of subcribers
       self.log = log        #instance of log
       self.packetCount = 0            #number of total packets recieved
       self.currentLine = ""
       
   
   def setPort(self, portNumber):
       returnValue=1                                #return true by default
       try:
            self.ser = serial.Serial(portNumber)     #reference to serial port object
            self.ser.baudrate = 9600                 #set baud rate
            self.ser.open()                 #open serial port
       except serial.serialutil.SerialException:
           returnValue=0                            #invalid serial port
           print "exception"
       return returnValue
           
        
    
   def subscribe(self, obj):         #subscribe method
       self.listeners.append(obj) 
    
   def getLine(self):           #creates full line from serial inputs
       respond = 0                #boolean variable, indicates if a ? was recieved at the end of line
       tmpLine = self.ser.read()   # tmp variable for holding line items 
             
       if(tmpLine == "~"):                #check for handshake
           self.currentLine = str(tmpLine)
           for obj in self.listeners:
               obj.notify()
           self.flush()
           self.currentLine=""            #flush line
           self.log.error('['+time.ctime()+'] HANDSHAKE RECEIVED') 
          
           self.packetCount+=1
           
       if(self.packetCount>=1):            #assumes the handshake was complete
           
           if(tmpLine !='@'):    #if not end of line
               self.currentLine += str(tmpLine)
               
           elif(tmpLine == '@'):
               if(self.currentLine[0:1] == '~'):
                   self.currentLine = self.currentLine[1:]  
               for obj in self.listeners:
                   obj.notify()
                   self.log.error('['+time.ctime()+'] RECEIVED:'+ self.currentLine) 
                   self.flush()
                   #self.currentLine = ""     #flush line
               self.packetCount+=1               
               
       
#       if (tmpLine !='@' and tmpLine !='~' ):     #if not end of line or initialization
#           self.currentLine += str(tmpLine) 
#           
#            
#       elif(tmpLine == '~'):                 #initialization
#           self.currentLine = str(tmpLine) 
#           for obj in self.listeners:         #notifies subscribers
#               obj.notify() 
#           self.flush()                     #clear line
#           print "~ recieved" 
#       else:
#           #if((tmpLine=='?' or tmpLine=='@') and self.currentLine.__len__() > 1):
#           if((tmpLine=='?' or tmpLine=='@') ):    
#               for obj in self.listeners:
#                   obj.notify()
#                   print "RECIEVED:",self.currentLine
#                   self.flush()        #reset current line 
#           self.packetCount = self.packetCount +1        #increase number of packets recieved
#           if(self.debug): print "full line recieved" 
                         
        
   def flush(self):             #clears currentline
       self.currentLine = "" 
    
   def getCurrentLine(self):     #returns currentline
       return self.currentLine 
   def getCurrentPacketCount(self):
       return self.packetCount
       
   def setLine(self, line):         #set line being sent to VGS
       if  self.ser.isOpen():
                     
           self.log.error('['+time.ctime()+'] TRANSMITTED:'+ line)           
           self.ser.write(line) 
          
        
   def test(self): 
       if(self.debug): print "Comm thread started" 
        
   def run(self):                 
       while self.running:
           self.getLine() 
          
   def stop(self):                 #changes state of thread to ready
       self.running = False 
       self.ser.close()         
