#Embry Riddle Aeronautical University
#SE451
#Senior Design, Spring 2008
#Packet.py : creates and decodes packet information
#Vikash dat
#datcc1@erau.edu

from Waypoint import Waypoint
import Conversion

mode = ""

def createWaypointPacket(wayList, firstWaypoint=False):
    
    #ugv string lDDD.dddddddddddddddd;gDDD.dddddddddddddddd;
    asciiString = ""

    #append the carrot if this is not the first waypoint, otherwise
    #don't send the carrot. KDE - 2/24/08
    if(not firstWaypoint):
        asciiString = "^"  
    else:
        asciiString = "l0;g0;"      
    for waypoint in wayList:
        asciiString += "l" + str(waypoint.getLatitude()) + ";g" + str(waypoint.getLongitude()) + ";"        
    
    
    	
    return asciiString + "?"
    

def setWaypointMode():
    #waypoint mode is 1
    globals()["mode"] = "%1" #Because of how packet.py is implemented, this is a global
                            #variable to store the current mode.  Kenny crys because having 
                            #to use globals is a bad programming pracice.  2/28/08
    return globals()["mode"]

def setInitalMode():
    globals()["mode"] = "%1"
    return globals()["mode"]

def setManualMode():
    globals()["mode"] = "%3"
    #manual mode: gives control of the vehicle to furtaba
    return "%3"
    
def setHaltMode():
    #halt mode: unknown right now
    globals()["mode"] = "%5"
    return "%5"

def getCurrentMode():
    return globals()["mode"]
    
#decode packet information
#packet types include:
#
#Hardware Ground station packets:
#Packet A:                G;0.00; time Alive in ms
#Packet B:                G; Lat; Lon; Alt; x-pos; y-pos
#
#Vechile packets:
#All Packets:            V;mode;speed; heading; temperature;voltage;latitude;longitude
#Initializatoin:        ~
#
def decodePacket(line, wayPointCount):
    ret = 1                    #returns the the type of Packet, 0 for bad packet
    package= {}
    wayList = []                #storage for waypoints from truck
    
    line.replace(" ","")        #gets rids of leading spaces in truck output
    tmpByteCount = len(line)
    
    dline = line.split(';')
    
    if (dline[0] == '~'):     #handshake
        ret = 1    
    elif(dline[0] == 'G'):    #ground station packets
        
        if(tmpByteCount == 14 ):    #Packet A
            
            ret = 2
            package['version'] = float(dline[1])                #Version #
            if(str(package['version']).__len__() <= 0):
                ret = 0                #bad packet
            package['alive'] = float(Conversion.timeAliveConvert(line[9:11]))
            if(str(package['alive']).__len__() <= 0):
                ret = 0                #bad packet             #time alive in ms
            package['battery_voltage'] = float(Conversion.voltageConversion(line[12:]))
            if(str(package['battery_voltage']).__len__() <= 0):
                ret = 0                #bad packet  
            
        if(tmpByteCount==22):    #Packet B
            ret = 3
            
            tmp = Conversion.string2gps(dline[1]).split(',')        #seperate direction
            package['latitude'] = tmp[0]                #Latitude
                        
            if(str(package['latitude']).__len__() <= 0):
                ret = 0                #bad packet
            tmp = Conversion.string2gps(dline[2]).split(',')    #seperate direction
            package['longitude'] = tmp[0]                #Longitude
            if(str(package['longitude']).__len__() <= 0):
                ret = 0                #bad packet
            package['altitude'] = Conversion.string2gps(dline[3])                #Altitude
            if(str(package['altitude']).__len__() <= 0):
                ret = 0                #bad packet
            package['heading'] = Conversion.string2gps(dline[4])                #Heading
            if(str(package['heading']).__len__() <= 0):
                ret = 0                #bad packet
                
            package['air_pressure'] =((float(Conversion.string2gps(dline[5]))/1023) + .095)/.009                #Heading
            if(str(package['air_pressure']).__len__() <= 0):
                ret = 0                #bad packet
            
            #package['xpos'] = dline[4]                #X-Position
            #package['ypos'] = dline[5]                #Y-position
            
        if(dline[1]=='c'):  #antenna packet
            ret =6
        
    else:    #vehicle packets

        try:
            if(len(dline)==9):
                
                ret = 4
                package['mode'] = int((dline[0])[1])
                if(str(package['mode']).__len__() <= 0):
                    ret = 0                #bad packet
                package['speed'] = float((dline[1])[1:len(dline[1])])
                if(str(package['speed']).__len__() <= 0):
                    ret = 0                #bad packet
                package['heading'] = float((dline[2])[1:len(dline[2])])
                if(str(package['heading']).__len__() <= 0):
                    ret = 0                #bad packet      
                package['temperature'] = float((dline[3])[1:len(dline[3])])
                if(str(package['temperature']).__len__() <= 0):
                    ret = 0                #bad packet
                package['range'] = float((dline[4])[1:len(dline[4])])
                if(str(package['range']).__len__() <= 0):
                    ret = 0                #bad packet                      
                package['battery_voltage'] = float((dline[5])[1:len(dline[5])])
                if(str(package['battery_voltage']).__len__() <= 0):
                    ret = 0                #bad packet
                package['latitude'] = float((dline[6])[1:len(dline[6])])
                if(str(package['latitude']).__len__() <= 0):
                    ret = 0                #bad packet
                package['longitude'] = float((dline[7])[1:len(dline[7])])
                if(str(package['longitude']).__len__() <= 0):
                    ret = 0                #bad packet
        except Exception:
            ret = 0        #bad packet
        
            if(str(dline[0]).rfind("CURRENT WAYPOINTSIndex:")!=-1):
                ret=5                #waypoints
                tmpWayPointCount = str(((dline[0])[24:25])).rstrip()  #get waypoint count return from vechile  
                if ((tmpWayPointCount+1) !=wayPointCount):            #test for consistency between variables
                    print "Error: Waypoint counts do not match!"
                    wayPointCount= int(tmpWayPointCount+1)            #correct inconsistencies
                (dline[0]).replace ( 'CURRENT WAYPOINTSIndex: 0', '' ) #remove misc. characters
                (dline[0]).lstrip()
                for w in range(0,wayPointCount):                         #create test waylist
                    wayList.append(Waypoint((dline[w])[1:], (dline[w+1])[1:],None))
                
                return(ret,wayList)            
    return (ret,package)
    