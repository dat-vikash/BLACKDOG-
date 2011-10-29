
import Pyro.core
import Pyro.naming        



class Waypoint:    
    def __init__(self, latitude, longitude, type, stopTime=None):
        self.latitude = latitude
        self.longitude = longitude        
        self.type = type
        self.stopTime = stopTime        

    #getter to get the information about a certain waypoint            
    def getLatitude(self):
        return self.latitude
    def getLongitude(self):
        return self.longitude
    def getType(self):
        return self.type
    def getStopTime(self):
        return self.stopTime
    def equals(self, test):
         if (self.latitude == test.latitude)&(self.longitude == test.longitude)&(self.type == test.type)&(self.stopTime == test.stopTime):
             return True
         else:
             return False

