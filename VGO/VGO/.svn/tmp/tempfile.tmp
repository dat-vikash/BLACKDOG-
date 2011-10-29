#-*- coding: latin_1 -*-

#Embry Riddle Aeronautical University
#SE451
#Senior Design, Spring 2008
#Conversion.py: aides in the converting of byte values to their respective values
#Vikash dat
#datcc1@erau.edu

from Waypoint import Waypoint

#conversion table for hex to binary
hex2bin = {'0': '0000', '1': '0001', '2': '0010', '3': '0011', '4': '0100',
 '5': '0101', '6': '0110', '7': '0111', '8': '1000', '9': '1001', 'A': '1010',
 'B': '1011', 'C': '1100', 'D': '1101', 'E': '1110', 'F': '1111'}


#comment

def string2gps(byteString):
    
    #get byte at a time
    tmpByteCount = len(byteString)
    returnString = ""
    
    if(tmpByteCount ==5): #gps information
        
        tmp1 = str(ord(byteString[0:1]))         #degrees
        tmp2 = str(ord(byteString[1:2])) + "."        #minutes
        
        tmp = str(hex(ord(byteString[2:3]))) + str(hex(ord(byteString[3:4])))[2:]    #convert word to hex value
        tmp2 += str(int(tmp,16))                    #fractional byptes, convert from hex to int
        
        tmp2 = float(tmp2)/60                                #convert MM.mmm to decimal degrees
        tmp1 = float(tmp1) + tmp2                            #^
        returnString += str(tmp1) + ","                    #fractional byptes, convert from hex to int
        returnString += str(ord(byteString[4:])) + ";"          #direction
    
    if(tmpByteCount == 2):    #alitiude infomation
        tmp = str(hex(ord(byteString[0:1]))) + str(hex(ord(byteString[1:2])))[2:] 
        returnString += str(int(tmp,16))
    
      
    return returnString
        
    
        

def timeAliveConvert(asciiString):
    tmpString = ""
    #convert ascii to decimal 
    tmp = str(hex(ord(asciiString[0:1]))) + str(hex(ord(asciiString[1:2])))[2:]
    tmpString = str(int(tmp,16)*5.13/60)
    return tmpString
    
def voltageConversion(asciiString):
    tmpString = ""
    #convert ascii to decimal 
    tmp = str(hex(ord(asciiString[0:1]))) + str(hex(ord(asciiString[1:2])))[2:]   
    tmpString = int(tmp,16)
    tmpString = float(tmpString)/1023*15
    return tmpString    
    
    

def convertWaypointToDecimalDegrees(waypoint):  
    degLat = waypoint.getLatitude()[0]
    minLat = waypoint.getLatitude()[1]
    secLat = waypoint.getLatitude()[2]
    
    degLon = waypoint.getLongitude()[0]
    minLon = waypoint.getLongitude()[1]
    secLon = waypoint.getLongitude()[2]
    
    lat = degLat + (minLat / 60.0) + (secLat / 3600.0)
    long = degLon + (minLon / 60.0) + (secLon / 3600.0)
    
    return (lat,long)    

