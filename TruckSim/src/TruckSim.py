# -*- coding: cp1252 -*-
import serial
import time
import threading
from math import *
from threading import Thread
import random
debug=1

###API Defined Variables (global, for ease)
#
range=255
mode=5
speed=0.000001
direction=0
temperature=0          #in Celsius (varies +/-)
batteryVoltage=255.0   #Simulated Volts (only decreases)

#middle of Lehmann building
latitude=-81.0466
longitude=29.18888

badComms = False

#For sending back good or bad gps data
badLatitude=1
badLongitude=1
gpsMode='i'

#Sensor data stuff
tempVar=0.5            #in percent
maxTemp=34.0
avgTemp=0.7*maxTemp
minTemp=0.5*maxTemp
temperature = avgTemp        #temp is in celsius

speedVar=0.1            #in percent
#Circumference of the earth at the equator = 24,901.55 miles (40,075.16 kilometers).
maxSpeed=.0001  #20mph 
avgSpeed=0.5*maxSpeed  
minSpeed=0.25*maxSpeed
speed = avgSpeed        #speed is in degrees per second

#
###End of Sensor data stuff

shakeEstablished=0

#misc
GPS_UPDATE_RATE = 1.0
HARDCODE_TO_NORTH_AMERICA = True
degree_symbol = unichr(176).encode("latin-1")
#################

class SerPort:
    def __init__ (self, debug = False):
        self.debug = debug
        self.listeners = []
      #  self.inval = raw_input("comm: ")
        self.ser = serial.Serial(0) #get first avail serial port (COM1)
        self.ser.baudrate = 9600
        self.ser.open()

    def test(self):
        if(self.debug): print "Serial Port object started"

    def sendChar(self, line): 
        if  self.ser.isOpen():
             self.ser.write(line)
             if(self.debug): print "char sent"
        
    def getChar(self):            #need to modify how lines are read
        if(self.debug): print "get char" 
        tmpLine = self.ser.read();   # tmp variable for holding line items
        if(self.debug): print "tmp: " + tmpLine             
        if (tmpLine !='?' and tmpLine !='~'):
            self.currentLine += str(tmpLine)


def main():

    comm = SerPort()    
    truck = Truck(latitude, longitude)
    
    getkeys = getKeyboard()
    getkeys.giveTruckRef(truck)
    getkeys.start()
    waypointStr =""
    speedStr = ""
    headingStr= ""
    
    #Thread instances
    dataReturner = TruckDataReturn(comm, truck)
    dataReturner.giveTruckRef(truck)
    truckMover = TruckMove()
    truckMover.giveTruckRef(truck)

    startThreads = True

    truck.setSpeed(speed)

    #API Step 1: Wait for '~' over serial
    #API Step 2: Acknowledge by returning '~'
    #API Step 3: Receive many waypoints until a '?' is received
    #API Step 4: Receive mode
    
    # start initialization sequence.........

    truck.waypointList[:]=[]
    
    print "TruckSim Started"
    
    while True:
        
        while True:
            if comm.ser.inWaiting():    # receive handshake to begin initialization
                char = comm.ser.read()
                if (char == '~'):
                    shakeEstablished=1
                    print "received " + char
                    comm.sendChar("~")        # return handshake
                    break            
            time.sleep(0.1)    
        
        while True:
            if comm.ser.inWaiting():
                char = comm.ser.read()
                if (char == '~'):     # handle multiple handshake
                    print "received " + char
                    comm.sendChar("~")
                    continue
                else:
                    waypointStr += str(char)
                    break
#                if (char == '^'): 
#                    truck.waypointList[:]=[]    # clear waypoint list       
#                    break
            time.sleep(0.1)

        #get waypoints        
        while True:
            if comm.ser.inWaiting():
                char = comm.ser.read()
                if (char != '?'):
                    waypointStr += str(char)
                    
                else:    
                    # parse waypoints, build list
                    list = waypointStr.split(";")
                    if(list[-1] == ""):
                        list.remove("")
                    i=2  #i is the list index where new waypoints are added
                         #i=2 to bypass l0;g0; per the api - spr
                    if (debug): print list.__len__()
                    while i < list.__len__():
                        truck.addWaypoint(Waypoint(float(list[i][1:]),float(list[i+1][1:])))
                        if (debug): print "LAT: " + list[i][1:] + "LONG: " + list[i+1][1:]
                        i+=2
                    
                    if (debug): print "Waypoint String: " + waypointStr
                    break
    
        while True:
            
            
            if comm.ser.inWaiting():          # strip leading %
                char = comm.ser.read()
                if comm.ser.inWaiting():
                    char = comm.ser.read()
                
               # if (debug): print "loop c: " + char
                    globals()["mode"] = char
                    if (debug): print "Mode: "  + str(globals()["mode"])
                    break

        #    if comm.ser.inWaiting():
        #        char = comm.ser.read()
               # if (debug): print "loop c: " + char
        #        globals()["mode"] = char
        #        if (debug): print "Mode: "  + str(globals()["mode"])
        #        break
    
        #API Step 5: Looped running:
            #Return every 1 Hz the commented stuff below
            #Can receive from truck:
                #new mode in form "%n" where n is 1, 3, or 5
                #waypoints
                #reboot: '-', where it will go back to step 1 and wait for a '~'
    
        if (startThreads):        # starts threads first pass only, then use go()
                dataReturner.start()
                truckMover.start()
                startThreads = False
        else:
              dataReturner.go()
              truckMover.go()
              
        del list[:]        # clear buffer and temp list
        waypointStr=""

       ###### 
       ### MAIN GET LOOP    
       #loop to take stuff in (GPS waypoints, mode, termination '-')
    
        while True:
    
            time.sleep(1.0/globals()["GPS_UPDATE_RATE"])
               
            if comm.ser.inWaiting():
                char = comm.ser.read()
                if (char == '%'):                    # SET MODE
                    char = comm.ser.read()
                    globals()["mode"] = char
                    if (debug): print "Mode: "  + str(globals()["mode"])
                    dataReturner.go()
                    truckMover.go()  ###
                    ##### MANUAL MODE 
                    if (mode == '3'):
                        if (debug): print "*IN MANUAL MODE"                        
                        truck.setSpeed(0);
                        
                        #truck.waypointList[:]=[]    # clear waypoint list
                        
                        if comm.ser.inWaiting():    # leading semi col
                            char = comm.ser.read()
                        
                        while True:    #main manual mode loop
                            if comm.ser.inWaiting():
                                char = comm.ser.read()
                                if (char == '['):
                                    if (debug): print "MANUAL: change speed"
                                    while True:
                                        char = comm.ser.read()
                                        if (char != ','):                            
                                            speedval = int(char)
                                        else: 
                                            if (debug): print "speed: " + str(speedval)
                                            
                                            # manipulate speed
                                            if (speedval >= 4):
                                                speedval -= 4    # baseline speed
                                                val = globals()["maxSpeed"] * (speedval/5.0)
                                                #truck.setSpeed(val)
                                                truck.setManSpeed(val)
                                                print "Speed: " + str(val)
                                            elif (speedval !=0):
                                                val = globals()["minSpeed"] * (0.8/speedval) * (-1)
                                                 # minSpeed is max reverse speed
                                                #truck.setSpeed(val)
                                                truck.setManSpeed(val)
                                                print "Speed: " + str(val)
                                            else:
                                                val = globals()["minSpeed"] * (-1)
                                                #truck.setSpeed(val)
                                                truck.setManSpeed(val)
                                            speedStr = ""
                                            break
                                        
                                if (char == ']'):
                                    if (debug): print "MANUAL: change dir"
                                    while True:
                                        char = comm.ser.read()
                                        if (char != ','):                            
                                            dirval = int(char)
                                        else: 
                                            newHeading = 0
                                            if (debug): print "head: " + str(dirval)
                                            # manipulate heading
                                            if (dirval > 4): #check 5-9
                                                dirval -= 4    # baseline speed
                                                #val = ((pi/4) * (dirval/5) * -1)  #turning wrong way
                                                val = ((pi/4) * (dirval/5))
                                            else:
                                                #val = ((pi/4) * (1.0/(dirval+1.0)))    #turning wrong way
                                                val = ((pi/4) * (1.0/(dirval+1.0))*(-1))  
                                                if (dirval==4):
                                                    val=0;
                                                
                                            if (debug): print "Dir val: " + str(val)       
                                            newHeading = truck.direction + val    # apply degree of turn to new heading
                                            if (newHeading > (2*pi)): # make sure 0-360
                                                newHeading -= (2*pi)
                                            if (newHeading < 0):
                                                newHeading += (2*pi)
                                            if (debug): print "newHeading: " + str(newHeading)
                                            #truck.turnTowardDirection(newHeading) # turn to new heading
                                            truck.setManDirection(newHeading)
                                            char = "" 
                                            break
                                
                                if (char == '%'):                    # SET MODE
                                    char = comm.ser.read()
                                    globals()["mode"] = char
                                    if (debug): print "Mode: "  + str(globals()["mode"])
                                    #set normal speed here
                                    truck.setSpeed(globals()["avgSpeed"])
                                    break
                    ### END MANUAL MODE
                    
                    if (mode == '5'):
                        dataReturner.stop()
                        truckMover.stop()
                        if (debug): print "HALT!!"
                    
                if (char == '{'):                    # REBOOT
                    if (debug): print "REBOOT!!!"
                    dataReturner.stop()
                    truckMover.stop()
                    break
                    
                if (char == '^'):
                    truckMover.stop()
                    del list[:]
                    truck.waypointList[:]=[]    # clear waypoint list
                    while True:
                        if comm.ser.inWaiting():
                            char = comm.ser.read()
                            if (char != '?'):
                                if (char != '^'): waypointStr += str(char)    # to prevent ^ from being added
                                
                            else:
                                list = waypointStr.split(";")
                                if(list[-1] == ""):
                                    list.remove("")
                                    
                                i=0
                                #if (debug): print list.__len__()
                                while i < list.__len__():
                                    truck.addWaypoint(Waypoint(float(list[i][1:]),float(list[i+1][1:])))
                                    if (debug): print "LAT: " + list[i][1:] + "LONG: " + list[i+1][1:]
                                    i+=2
                
                                if (debug): print "Waypoint String: " + waypointStr
                                
                                waypointStr=""
                                if (truck.currentWaypointIndex > (len(truck.waypointList) - 1)):
                                    if (debug): print "true"
                                    truck.currentWaypointIndex = truck.currentWaypointIndex - 1 # go to last known waypoint
                                truckMover.go()
                                break
                            
                if (char == 'w'): 
                    i=0
                    
                    nulist = truck.waypointList[:]
                    waypointString = ""
                    for waypoint in truck.waypointList:
                        waypointString+="l"+str(waypoint.getLatitude())+";g"+str(waypoint.getLongitude())+";"
                    waypointString+="?"
                    comm.sendChar("CURRENT WAYPOINTSIndex: " + str(nulist.__len__())  + " " + waypointString  + "  END WAYPOINTS")
                
        ### END MAIN LOOP
 
class Truck:
    def __init__(self, long, lat):
        self.long = long  #x
        self.lat = lat    #y
        self.direction = 0.0 #direction is from due east and counter-clockwise in radians
        self.waypointList= []
        self.currentWaypointIndex = 0

        self.speed = .1 #speed is in degrees per second
        
        #manual movement values
        self.manSpeed = 0.1; #manual mode speed            
        self.manDirection=0;
                
    #method for waypoint moving                
    def move(self):

        self.changeSensorData();

        if(len(self.waypointList)>0):
            xDestination = self.waypointList[self.currentWaypointIndex].longitude
            yDestination = self.waypointList[self.currentWaypointIndex].latitude
            xDelta = xDestination - self.long
            yDelta = yDestination - self.lat
            totalDistance = sqrt(pow(xDelta,2)+pow(yDelta,2))
            if xDelta == 0:
                if yDelta<0:
                    self.turnTowardDirection((3.0/2.0)*pi)
                else:
                    self.turnTowardDirection(pi/2.0)
            else:
                if xDelta < 0:
                    self.turnTowardDirection(atan(yDelta/xDelta) + pi)
                else:
                    self.turnTowardDirection(atan(yDelta/xDelta))
            #self.setDirection(self.direction)
            distanceToBeTraveled = self.speed * (1.0/GPS_UPDATE_RATE)
            if distanceToBeTraveled < totalDistance:
                co = cos(self.direction)
                self.long = self.long + distanceToBeTraveled * cos(self.direction)
                self.lat = self.lat + distanceToBeTraveled * sin(self.direction)
            else:
                self.long = xDestination
                self.lat = yDestination
                self.currentWaypointIndex = (self.currentWaypointIndex+1)%len(self.waypointList)

    #method for manual moving
    def manualMove(self):

        self.changeSensorData();        

        self.direction=self.manDirection;

        self.long=self.long+self.manSpeed*cos(self.direction)
        self.lat=self.lat+self.manSpeed*sin(self.direction)

    def turnTowardDirection(self,newDirection):
        turningSpeed = (pi/4.0)/globals()["GPS_UPDATE_RATE"]
        if abs((newDirection% (2*pi)) - (self.direction% (2*pi))) < turningSpeed:
            self.direction = ( newDirection ) % (2*pi)
        else:
            if((newDirection - self.direction) % (2*pi) <= pi ):
                self.direction = ( self.direction + turningSpeed ) % (2*pi)
            else:
                if((newDirection - self.direction) % (2*pi) > pi ):
                    self.direction = ( self.direction - turningSpeed ) % (2*pi)

    def getDirection(self):
        return self.direction;        

    def setManSpeed(self,s):
        self.manSpeed=s;
    def setManDirection(self,d):
        self.manDirection=d;

    def setSpeed(self,speed):
        self.speed = speed
    def getSpeed(self):
        return self.speed

    def getGPS(self):
        return "Lat: " + str(self.lat) + " Long: " + str(self.long)

    def getLatitude(self):
        return self.lat
        
    def getLongitude(self):
        return self.long

    def addWaypoint(self,waypoint):
        self.waypointList.append(waypoint)

    def radiansToDegrees(self, rad):
        self.directionD=rad*(180.0/pi)
        
        #handle coordinate system conversion
        self.heading = 90.0 - self.directionD
        
        #HARDCODE TO NORTH AMERICA
        #if (bool(globals()["HARDCODE_TO_NORTH_AMERICA"])): self.heading = 0.0 - self.heading

        if (self.heading < 0): self.heading = self.heading + 360.0
        if (self.heading>360): self.heading = self.heading - 360.0
        #end heading
        
        return self.heading

    def changeSensorData(self):
        
        #SENSOR DATA CHANGING
        #Battery
        globals()["batteryVoltage"] = globals()["batteryVoltage"]*.99999

        #Temperature Data Changing
        tempPosNeg=0;

        tempPosNeg=random.randrange(0,2)
        if tempPosNeg==0:
            tempPosNeg=-1
        globals()["temperature"]=globals()["temperature"]+(random.random()*tempVar)*tempPosNeg
        if globals()["temperature"]>maxTemp:
            globals()["temperature"]=maxTemp
        if globals()["temperature"]<minTemp:
            globals()["temperature"]=minTemp

        #Speed Data Changing
        speedPosNeg=0;

        speedPosNeg=random.randrange(0,2)
        if speedPosNeg==0:
            speedPosNeg=-1
        globals()["speed"]=globals()["speed"]+(random.random()*speedVar)*speedPosNeg
        if globals()["speed"]>maxSpeed:
            globals()["speed"]=maxSpeed
        if globals()["speed"]<minSpeed:
            globals()["speed"]=minSpeed
        #END OF SENSOR DATA CHANGE

#Class that periodically sends data back through serial to whoever wants it
class TruckDataReturn (Thread):
    def __init__ (self, rec, truck):
        Thread.__init__(self)
        self.rec = rec
        self.truck = truck
        
    def giveTruckRef(self,tr):
        self.truck=tr
        
    def run (self):
        self.running=True
        while True:
            while not self.running:
                time.sleep(1.0/globals()["GPS_UPDATE_RATE"])
            #send data
            #outstring = '%' + str(mode) + ';#' + str(self.truck.speed) + ';*' + str(self.truck.direction) + ';!' + str(temperature) + ';&' + str(batteryVoltage) + ';l' + str(self.truck.lat) + ';g' + str(self.truck.long) + ';@'

            #Send correct GPS Data
            if (globals()["gpsMode"] == 'i' and globals()["badComms"]==False):
                outstring = '%' + str(mode) + ';#' + str(self.truck.speed) + ';*' + str(self.truck.radiansToDegrees(self.truck.direction)) + ';!' + str(temperature) + ';r' + str(globals()["range"]) + ';&' + str(batteryVoltage) + ';l' + str(self.truck.lat) + ';g' + str(self.truck.long) + ';@'
                print "Data returned in normal GPS mode"
            #Send GPS = (0,0)
            elif (globals()["gpsMode"] == 'o'):
                outstring = '%' + str(mode) + ';#' + str(self.truck.speed) + ';*' + str(self.truck.radiansToDegrees(self.truck.direction)) + ';!' + str(temperature) + ';r' + str(globals()["range"]) + ';&' + str(batteryVoltage) + ';l' + str(0) + ';g' + str(0) + ';@'
                print "Data returned in Zero/Zero GPS mode"
            #Send an unchanging point, regardless of the truck driving or not
            elif (globals()["gpsMode"] == 'p'):
                outstring = '%' + str(mode) + ';#' + str(self.truck.speed) + ';*' + str(self.truck.radiansToDegrees(self.truck.direction)) + ';!' + str(temperature) + ';r' + str(globals()["range"]) + ';&' + str(batteryVoltage) + ';l' + str(globals()["badLatitude"]) + ';g' + str(globals()["badLongitude"]) + ';@'
                print "Data returned in Point GPS mode"

            elif (globals()["badComms"]==True):
                outstring = '%' + str(mode) + ';#' + str(self.truck.speed) + ';*' + str(self.truck.radiansToDegrees(self.truck.direction)) + ';!;r' + str(globals()["range"]) + ';&' + str(batteryVoltage) + ';l' + str(globals()["badLatitude"]) + ';g' + str(globals()["badLongitude"]) + ';@'
                print "Data returned bad comms mode"    

            if (debug): print outstring
            self.rec.sendChar(outstring)
            
            print self.truck.getGPS() #sr.write(Truck.getGPS())
            print 'at Direction:',self.truck.getDirection()
            print 'at Heading:',self.truck.radiansToDegrees(self.truck.getDirection()), degree_symbol
            print 'at Speed', self.truck.getSpeed(), "spherical degrees / second"
            
            time.sleep(1.0/globals()["GPS_UPDATE_RATE"])

    def stop(self):
        self.running = False
    
    def go(self):
        self.running = True    

#Class that "moves" the truck
class TruckMove (threading.Thread):

    def giveTruckRef(self,tr):
        self.truck=tr

    def run (self):
        self.running=True
        while True:
            while not self.running: #for paused operation
                time.sleep(1.0/globals()["GPS_UPDATE_RATE"])
            
            if (globals()["mode"]=='1'): #wp mode
                self.truck.move()
            elif (globals()["mode"]=='3'): #manual
                self.truck.manualMove()
            elif (globals()["mode"]=='5'): #halt mode)
                print "its not moving."
            else:
                pass # do nothing
            
            time.sleep(1.0/globals()["GPS_UPDATE_RATE"])
            
    def stop(self):
        self.running = False
            
    def go(self):
        self.running = True  

class getKeyboard (Thread):
    
    def giveTruckRef(self,tr):
        self.truck=tr
    
    def run(self):
        k=''
        rangeCount=0
        changeRange=False
        while(1):
            if(rangeCount==8 and changeRange==True):
                globals()["range"] = 255
                changeRange=False
                rangeCount=0
            elif(rangeCount<8 and changeRange==True):
                rangeCount+=1            
            
            k = raw_input()
            if k.startswith('r'):
                globals()["range"] = 25
                changeRange=True
                print "~Range: 25"
                time.sleep(1.5)
            if k.startswith('i'):
                globals()["gpsMode"] = 'i'
                print "~New GPS Mode: Correct Function Mode"
                time.sleep(1.5)
            if k.startswith('o'):
                globals()["gpsMode"] = 'o'
                print "~New GPS Mode: Zero/Zero Mode"
                time.sleep(1.5)
            if k.startswith('p'):
                globals()["gpsMode"] = 'p'
                print "~New GPS Mode: Single Point Mode"
                globals()["badLongitude"] = self.truck.getLongitude()
                globals()["badLatitude"] = self.truck.getLatitude()
                time.sleep(1.3)
                
            if k.startswith('c'):
                globals()["badComms"] = True
            
            if k.startswith('n'):
                globals()["badComms"] = False

class Waypoint:    
    def __init__(self, latitude, longitude):
        self.longitude = longitude      
        self.latitude = latitude
    def getLongitude(self):
        return self.longitude          
    def getLatitude(self):
        return self.latitude

if __name__ == '__main__':
    main()
