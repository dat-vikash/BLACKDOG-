#Embry-Riddle Aeronautical University
#SE/CS/CE Senior Project 2007-08
#Control Team
#Jesse Berger, Cory Carson, Janelle Hilliard
#
#This module contains the Obstacle Manager class.
#The Obstacle Manager collects, stores, and provides data on obstacles to interested parties.

from __future__ import with_statement
from util import async
from array import array
from collections import deque
from threading import RLock #http://docs.python.org/lib/rlock-objects.html
from threading import Thread, Event
from time import time
from math import sqrt, cos, sin, atan, pi
import Pyro.core #pyro.sourceforge.net
import logging #http://www.red-dove.com/python_logging.html
import os, zlib

#Inheriting from type 'object' makes this a 'new-style' class.
#This allows new language features, such as properties.
class ObstacleManager(object, Pyro.core.ObjBase):
    """ObstacleManager(string programPath, [int loggingLevel],
    [int sectorPixelWidth], [float degreesPerPixelLong],
    [float degreesPerPixelLat], [int sectorUnloaderPeriod],
    [int sectorAgeThreshold], [string folderName],
    [logging.level loggingLevel])
    
    This class is responsible for recording obstacles in a persistent manner
    and provide obstacle information to others.
    
    This also inherits from Pyro.core.ObjBase, allowing access over
    Pyro. (http://pyro.sourceforge.net/)
    
    Locations are abstracted into pixels; each pixel represents 
    (degreesPerPixelLong) degrees by (degreesPerPixelLat) degrees.
    Obstacles are represented as signed bytes at GPS locations.
    The value denotes the certainty of an obstacle existing at that location.
    
    The maximum value of a pixel, 127, is special in that it denotes an obstacle
    or boundary that may not be otherwise detected by the ground vehicle.
    These obstacles are called Hard obstacles.  Hard obstacles cannot have their
    confidence eroded by the ground vehicle.  Hard obstacles cannot be
    created by the ground vehicle.    
    
    Pixels are addressed by integer values representing longitude and
    latitude.  The addresses (indexes) are obtained by dividing the 
    floating point degrees value by the degreesPerPixelLong or Lat
    and truncating the result.
    
    Pixel address space is virtualized into sectors to save on memory usage.
    Sectors that have not been accessed within (sectorAgeThreshold) seconds
    will be saved to disk and fed to the garbage collector.    
    
    Usage:
     #Host and return the ObstacleManager proxy on your Pyro daemon
    uri = self.getDaemon().connect(obstacleManangerInstance)
    referenceToReturnOverPyro = obstacleManangerInstance.getProxy()
    
    key = obstacleManagerInstance.subscribe()
    obstacleManagerInstance.checkArea(23.5, 52, 23.51, 52.2)
    #Put information about the area on the update deque
    obstalceManagerInstance.checkArea(12,12,12.1,12.1,key)
    #Put information on this area only on a particular update deque
    obstacleManagerInstance.setPoint(23.5001, 52.112, 50)
    #Set the confidence of a particular point to 50
    obstacleManagerInstance.addCircle(23.1, 23.1, 0.002)
    #Add a hollow circle of Hard obstacles at 23.1,23.1 of radius 0.002
    updates = obstacleManagerInstance.getUpdates(key)
    #collections.deque of tuples: (degreesLat, degreesLong, confidenceValue)
    resolutionLong = obstacleManagerInstance.DEGREES_PER_PIXEL_LONG
    resolutionLat = obstacleManagerInstance.DEGREES_PER_PIXEL_LAT
    #Determine how accurate obstacles are.  This may be useful for drawing purposes.
    obstacleManagerInstance.clearArea(23.0,23.0,23.2,23.2)
    #Remove all obstacles (even Hard) in the given area.
    obstacleManagerInstance.interpretRangefinder(30,30,282,0.0003)
    #Interpret rangefinder information from a sensor located at
    #(30,30) pointing at heading 282 with a range of 0.0003 degrees
    
    Limitations:
    Note that the pixel resolutions are only an approximations for a particular
    part of the world.  If this project were to be deployed in multiple 
    geographically different locations at once, a more accurate representation
    would be helpful.  Because the use is out of scope for this year, so is the
    accurate resolution abstraction.  
    This library also does not know about latitudes reversing
    (-89.8, -89.9, -89.9, -89.8) or longitudes wrapping (-179.9, -180, 179.9)
    """
    version = property(lambda self: 0, 
                       doc = "Different versions are not compatible")
    def __init__(self, programPath = os.curdir,
                 sectorPixelWidth = 400, 
                 degreesPerPixelLong = 0.00002,
                 degreesPerPixelLat  = 0.00002,
                 sectorUnloaderPeriod = 120,
                 sectorAgeThreshold = 5*60,
                 folderName = "sectors",
                 loggingLevel = logging.ERROR):
                
        #To prevent a problem with orphan sectors/threads that cannot
        #be garbage collected,
        #call close to attempt to shut down the existing subsystem.
        #This means that calling __init__ again will reset the obstacle manager.
        try: 
            self.close()
        except AttributeError:
            Pyro.core.ObjBase.__init__(self)        
        
        #Enforce integer value
        self.__SECTOR_WIDTH_PIXELCOUNT = int(sectorPixelWidth)

        self.__DEGREES_PER_PIXEL_LONG = degreesPerPixelLong
        self.__DEGREES_PER_PIXEL_LAT = degreesPerPixelLat
        self.__sectorsDict = {}#Dictionary
        #sector keys are str(latIndex)+"-"+str(longIndex)
        
        self.__rlockSectorList = RLock()
        
        self.__updateSubscribers = {} #Dictionary. () != {}
        
        #Future implementation may ask information to be logged to file,
        #and using the logging library allows this to be done with 
        #a configuration command to the log object.
        #http://docs.python.org/lib/module-logging.html
        logging.basicConfig()
        self.__log = logging.getLogger("ObstacleManager")
        self.__log.setLevel(loggingLevel)
        
        #Check if the 'secs' folder exists to store the sector files
        #If the directory does not exist, then try to make it.
        try:
            self.__path = os.path.join(programPath, folderName)
            if not (os.path.isdir(self.__path)):
                os.makedirs(self.__path)
                self.__log.debug("Sector file path created: " + self.__path)
            else:
                self.__log.debug("Sector file path found: " + self.__path)
        except OSError, error:
            self.__log.critical("Unable to access or create sector file directory; " +
                             "sectors cannot be read from or written to disk: " +
                             str(error))

        #Verify constructor parameters
        if self.__DEGREES_PER_PIXEL_LAT <= 0: raise Exception, \
            "ObstacleManager: Degrees of latitude per pixel cannot be <= 0"
        if self.__DEGREES_PER_PIXEL_LONG <= 0: raise Exception, \
            "ObstacleManager: Degrees of longitude per pixel cannot be <= 0"
        if self.__SECTOR_WIDTH_PIXELCOUNT <= 0: raise Exception, \
            "ObstacleManager: Sector width in pixels cannot be <= 0"
            
        #Precalculate this
        self.__MIN_DEGREES_PER_PIXEL = min(self.__DEGREES_PER_PIXEL_LAT, self.__DEGREES_PER_PIXEL_LONG)
        
        self.__sectorUnloader = \
            self.__SectorUnloadThread(self.__rlockSectorList,
                                   self.__sectorsDict,
                                   sectorUnloaderPeriod,
                                   sectorAgeThreshold,
                                   logLevel = loggingLevel)
        self.__log.debug("Initialized")
    
    def __del__(self): self.close()
    def close(self):
        """Stop all active threads owned by this object and write all relevant files to disk
        Note that once the instance is closed, it is no longer functional."""
        self.__log.debug("Closing...")
        self.__sectorUnloader.stop()
        self.saveAllObstacleData()
        del self.__updateSubscribers
        del self.__sectorsDict
        self.__log.debug("Closed")

    __degreesPerInchLat = 0.00000025
    __degreesPerInchLong = 0.00000025
    def interpretTruckSensors(self, locationDegreesLat, 
                             locationDegreesLong, 
                             heading, #degrees
                             range,
                             weight = 10,
                             minRange = 0, maxRange = 255):
        """interpretTruckSensors(float locationDegreesLat, float locationDegreesLong
        float heading, float range, float minRange, float maxRange)
        Interprets and places obstacle information based on the ultrasonic truck sensors"""
        if range == 0: return
        #The types of the incoming variables cannot be guaranteed.
        #Therefore, they must be cast.
        locationDegreesLat = float(locationDegreesLat)
        locationDegreesLong = float(locationDegreesLong)
        heading = float(heading)
        range = float(range)
        
        maxRange = abs(maxRange)
        if range > maxRange:
            self.__log.error("Reported range was greater than maxrange (" + str(maxRange) + "): " + str(range))
            range = maxRange
        range = abs(range); minRange = abs(minRange); weight = abs(weight)
        direction = pi * (90.0 - heading) / 180
        
        lat = locationDegreesLat
        long = locationDegreesLong
        
        pixels = min((range - minRange) * self.__degreesPerInchLat, (range - minRange) * self.__degreesPerInchLong) / self.__MIN_DEGREES_PER_PIXEL
        while pixels > 0:
            self.changePoint(lat, long, -weight)
            lat += self.__MIN_DEGREES_PER_PIXEL * sin(direction)
            long += self.__MIN_DEGREES_PER_PIXEL * cos(direction)
            pixels -= 1
        #254 is an arbitrary threshold
        if range < 254: self.changePoint(lat, long, weight)

    #Allows easy access to the information but enforces read-only access.
    #print someObstacleManagerInstance.SECTOR_WIDTH_PIXELCOUNT  #Succeeds
    #someObstacleManagerInstance.SECTOR_WIDTH_PIXELCOUNT = 6 #raises AttributeError
    #http://users.rcn.com/python/download/Descriptor.htm
    SECTOR_WIDTH_PIXELCOUNT = property(lambda self: self.__SECTOR_WIDTH_PIXELCOUNT,
                                       doc = "The number of pixels wide a sector is")
    
    def getDEGREES_PER_PIXEL_LONG(self):
        """Deprecated.  Use .DEGREES_PER_PIXEL_LONG
        Provided as a workaround for Pyro versions <4"""
        return self.__DEGREES_PER_PIXEL_LONG
    DEGREES_PER_PIXEL_LONG = property(lambda self: self.__DEGREES_PER_PIXEL_LONG,
                                      doc = "The degrees of longitude per pixel")
    
    def getDEGREES_PER_PIXEL_LAT(self): 
        """Deprecated.  Use .DEGREES_PER_PIXEL_LAT
        Provided as a workaround for Pyro versions <4"""
        return self.__DEGREES_PER_PIXEL_LAT
    DEGREES_PER_PIXEL_LAT = property(lambda self: self.__DEGREES_PER_PIXEL_LAT,
                                     doc = "The degrees of latitude per pixel")
    
    MIN_DEGREES_PER_PIXEL = property(lambda self: self.__MIN_DEGREES_PER_PIXEL,
                                    doc = "The average degrees per pixel")

    #@async
    def deleteAllObstacleData(self):
        """Deletes all obstacle information"""
        self.__log.debug("Clearing all obstacle information...")
        with self.__rlockSectorList:
            self.__sectorUnloader.stop()
            #Free the sectors
            self.__sectorsDict.clear()
            #Clear the deques
            [stack.clear() for stack in self.__updateSubscribers.itervalues()]
            self.__log.debug("Obstacle information cleared from memory")
            try:
                #http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/193736
                files = os.listdir(self.__path)
                for file in files:
                    if file.endswith(".sec"):
                        os.remove(file)
                else:
                    self.__log.info("All obstacle information removed")
            except OSError:
                self.__log.error("Unable to delete sector file: " & str(file))
            self.__sectorUnloader.start()
    
    def saveAllObstacleData(self):
        """Attempts to write all obstacle data in memory to secondary storage."""
        #http://mail.python.org/pipermail/python-dev/2003-January/032587.html
        #Apply the 'save' function to every sector in the list.
        with self.__rlockSectorList: 
            map(lambda sector: sector.save(), self.__sectorsDict.itervalues())
        
        
    def subscribe(self):
        """Notifies this subsystem that there is a party interested in
        knowing about changes.  A key for that party is created and returned."""
        key = os.urandom(16)
        self.__updateSubscribers[key] = deque()
        self.__log.info(str(key) + " subscribed")
        return key
    
    def unsubscribe(self, key):
        """unsubscribe(key)
        Notifies this subsystem that a party is no longer interested in
        knowing about changes.  It will no longer keep track of changes
        for that party."""
        try:
            del self.__updateSubscribers[key]
            self.__log.info(str(key) + " unsubscribed")
        except KeyError:
            string = ("Someone attempted to unsubscribe with a bad key: " +
                               str(key) + "\n"+
                               "Keys in updateSubscribers:"+"\n" +
                               str(self.__updateSubscribers.keys()))
            self.__log.error(string)
            raise KeyError, string
    
    def getUpdates(self, key):
        """getUpdates(key)
        For a subscribed party that has a key, it returns a s
        collections.deque containing tuples about changes in underlying data.
        Items in the deque have the form (degreesLat, degreesLong, newValue)."""
        try:
            temp = self.__updateSubscribers[key]
            self.__updateSubscribers[key] = deque()
            return temp
        except KeyError:
            string = ("Someone attempted to get updates with a bad key: " +
                               str(key) + "\n"+
                               "Keys in updateSubscribers:"+"\n" +
                               str(self.__updateSubscribers.keys()))
            self.__log.error(string)
            raise KeyError, string
    
    def __putUpdate(self, degreesLat, degreesLong, value, key = None):
        """__putUpdate(float degreesLat, float degreesLong,
        signed byte value, [key])
        Places the tuple in the update deques:
        (degreesLat, degreesLong, value)
        
        If a key is provided, the tuple is only put into that deque.
        Otherwise, the tuple is put in all update deques."""
        #Call the method appendleft on every deque object
        #pointed to by the __updateSubscribers dictionary.
        if key == None:
            [stack.appendleft((degreesLat, degreesLong, value)) \
             for stack in self.__updateSubscribers.itervalues()]
        else:
            self.__updateSubscribers[key].appendleft((degreesLat, degreesLong, value))

    @async
    def checkArea(self, degreesLat, degreesLong, degreesLat2, degreesLong2, key = None):
        """checkArea(float degreesLat, float degreesLong,
        float degreesLat2, float degreesLong2, [key])
        Similar to getGrid in that it obtains obstacle information about a 
        particular area, but instead of returning a two-dimensional array,
        it puts every pixel's value in the area on the update deques.
        
        If a key is provided, only that party's deque will have the new information."""
        if (degreesLat > degreesLat2):
            degreesLat2, degreesLat = degreesLat, degreesLat2
        if (degreesLong > degreesLong2):
            degreesLong2, degreesLong = degreesLong, degreesLong2
        iteratorLat = degreesLat
        while iteratorLat <= degreesLat2:
            iteratorLong = degreesLong
            while iteratorLong <= degreesLong2:
                self.__putUpdate(iteratorLat, iteratorLong, 
                    self.getPoint(iteratorLat, iteratorLong), key)
                iteratorLong += self.__DEGREES_PER_PIXEL_LONG
            iteratorLat += self.__DEGREES_PER_PIXEL_LAT
            
    @async
    def clearArea(self, degreesLat, degreesLong, degreesLat2, degreesLong2):
        """clearArea(float degreesLat, float degreesLong,
        float degreesLat2, float degreesLong2)
        Removes all obstacle information over the given area"""
        if (degreesLat > degreesLat2):
            degreesLat2, degreesLat = degreesLat, degreesLat2
        if (degreesLong > degreesLong2):
            degreesLong2, degreesLong = degreesLong, degreesLong2
        iteratorLat = degreesLat
        while iteratorLat <= degreesLat2:
            iteratorLong = degreesLong
            while iteratorLong <= degreesLong2:
                self.__putUpdate(iteratorLat, iteratorLong, 
                    self.clearPoint(iteratorLat, iteratorLong))
                iteratorLong += self.__DEGREES_PER_PIXEL_LONG
            iteratorLat += self.__DEGREES_PER_PIXEL_LAT
    
    def getGrid(self, degreesLat, degreesLong, degreesLat2, degreesLong2):
        """getGrid(float degreesLat, float degreesLong,
        float degreesLat2, float degreesLong2)
        Returns a confidence grid over a particular area, denoted
        by two sets of lat/long pairs in degrees.
        grid = getGrid(...)
        grid[0][0] is in the most negative corner of the requested area
        and grid[max][max] is in the most positive corner of the area."""
        latIndex, longIndex = self.__convertToIndices(degreesLat, degreesLong)
        latIndex2, longIndex2 = self.__convertToIndices(degreesLat2, degreesLong2)
        return self.__getGrid(latIndex, longIndex, latIndex2, longIndex2)
    
    def __getGrid(self, latIndex, longIndex, latIndex2, longIndex2):
        """__getGrid(int latIndex, int longIndex, 
        int latIndex2, int longIndex2)
        See getGrid"""
        grid = []
        if (latIndex > latIndex2):
            latIndex2, latIndex = latIndex, latIndex2
        if (longIndex > longIndex2):
            longIndex2, longIndex = longIndex, longIndex2
            
        for iteratorLat in range(latIndex, latIndex2):
            col = []
            for iteratorLong in range(longIndex,longIndex2):
                col.append(self.__getPoint(iteratorLat, iteratorLong))
            grid.append(col)
        return grid
    
    def get3x3(self, degreesLat, degreesLong):
        """get3x3(float degreesLat, float degreesLong)
        Returns a two-dimensional array (3x3) of obstacle
        information centered on (degreesLat, degreesLong)"""
        return self.getGrid(degreesLat - self.__DEGREES_PER_PIXEL_LAT,
                            degreesLong - self.__DEGREES_PER_PIXEL_LONG,
                            degreesLat + self.__DEGREES_PER_PIXEL_LAT,
                            degreesLong + self.__DEGREES_PER_PIXEL_LONG)

    def getXxX(self, degreesLat, degreesLong, width):
        """getXxX(float degreesLat, float degreesLong, int width)
        Returns a two-dimensional array (XxX) of obstacle
        information centered on (degreesLat, degreesLong).
        
        Not to be confused with the getXXX() function.  That does an entirely different thing."""
        offsetFromCenter = width/2
        return self.getGrid(degreesLat - offsetFromCenter*self.__DEGREES_PER_PIXEL_LAT,
                            degreesLong - offsetFromCenter*self.__DEGREES_PER_PIXEL_LONG,
                            degreesLat + offsetFromCenter*self.__DEGREES_PER_PIXEL_LAT,
                            degreesLong + offsetFromCenter*self.__DEGREES_PER_PIXEL_LONG)
    
    def getNumObstaclesInXxX(self, degreesLat, degreesLong, width, obstacleThreshold = 50):
        """getNumObstaclesInXxX(float degreesLat, float degreesLong, int width, int threshold)
        Returns a integer ofthe number of obstacles over the theshold
        in the two-dimensional array (XxX) of obstacle
        information centered on (degreesLat, degreesLong)"""
        offsetFromCenter = width/2
        grid = self.getGrid(degreesLat - offsetFromCenter*self.__DEGREES_PER_PIXEL_LAT,
                            degreesLong - offsetFromCenter*self.__DEGREES_PER_PIXEL_LONG,
                            degreesLat + offsetFromCenter*self.__DEGREES_PER_PIXEL_LAT,
                            degreesLong + offsetFromCenter*self.__DEGREES_PER_PIXEL_LONG)
        numObstacles = 0
        for col in grid:
            for pixel in col:
                if pixel >= obstacleThreshold:
                    numObstacles+=1   
        return numObstacles
    
    def getPoint(self, degreesLat, degreesLong):
        """getPoint(float degreesLat, float degreesLong)
        Returns a signed byte confidence value"""
        latIndex, longIndex = self.__convertToIndices(degreesLat, degreesLong)
        return self.__getPoint(latIndex, longIndex)
    
    def __getPoint(self, latIndex, longIndex):
        """__getPoint(int latIndex, int longIndex)
        Returns a signed byte confidence value"""
        return self.__getSector(latIndex, longIndex).getPixel(latIndex, longIndex)
    
    def setPoint(self, degreesLat, degreesLong, value = 127):
        """setPoint(float degreesLat, float degreesLong, [int value])
        Sets a point to the value provided.  If no value is provided,
        the value is 127 - creating a Hard obstacle.
        Returns the new signed byte confidence value of the point."""
        latIndex, longIndex = self.__convertToIndices(degreesLat, degreesLong)
        return self.__setPoint(latIndex, longIndex, value)
    
    def __setPoint(self, latIndex, longIndex, value = 127):
        """__setPoint(int latIndex, int longIndex, [int value])
        Sets a point to the value provided.  If no value is provided,
        the value is 127 - creating a Hard obstacle.
        Returns the new signed byte confidence value of the point."""
        actualValue, changed = self.__getSector(latIndex, longIndex).setPixel(latIndex, longIndex, value)
        if changed:
            lat, long = self.__convertToDegrees(latIndex, longIndex)
            self.__putUpdate(lat, long, value)
        return actualValue
    
    def changePoint(self, degreesLat, degreesLong, delta = 1):
        """changePoint(float degreesLat, float degreesLong, [int delta])
        Changes a point's confidence by a delta.  If no delta is provided,
        the point's confidence is incremented.  Note that this function
        cannot create or destroy Hard obstacles, as they must be explicitly set.
        Returns the new signed byte confidence value of the point."""
        latIndex, longIndex = self.__convertToIndices(degreesLat, degreesLong)
        return self.__changePoint(latIndex, longIndex, delta)
    
    def __changePoint(self, latIndex, longIndex, delta = 1):
        """__changePoint(int latIndex, int longIndex, [int delta])
        Changes a point's confidence by a delta.  If no delta is provided,
        the point's confidence is incremented.  Note that this function
        cannot create or destroy Hard obstacles, as they must be explicitly set.
        Returns the new signed byte confidence value of the point."""
        actualValue, changed = self.__getSector(latIndex, longIndex).changePixel(latIndex, longIndex, delta)
        if changed:
            lat, long = self.__convertToDegrees(latIndex, longIndex)
            self.__putUpdate(lat, long, actualValue)
        return actualValue
        
    def clearPoint(self, degreesLat, degreesLong):
        """clearPoint(float degreesLat, float degreesLong)
        Sets a point's confidence to 0.
        Returns 0"""
        latIndex, longIndex = self.__convertToIndices(degreesLat, degreesLong)
        return self.__setPoint(latIndex, longIndex, 0)
    
    def __getSector(self, latIndex, longIndex):
        """__getSector(int latIndex, int longIndex)
        Returns a Sector reference"""
        sectorLongIndex = longIndex % self.__SECTOR_WIDTH_PIXELCOUNT
        sectorLatIndex = latIndex % self.__SECTOR_WIDTH_PIXELCOUNT
        sectorLong = longIndex - sectorLongIndex
        sectorLat = latIndex - sectorLatIndex
        sectorKey = str(sectorLat)+"-"+str(sectorLong)
        
        with self.__rlockSectorList:
            try:
                return self.__sectorsDict[sectorKey]    
            except KeyError:
                #Didn't find it in memory, so make a new sector.
                newSector = \
                   self.__Sector(sectorLat, sectorLong, 
                              self.__SECTOR_WIDTH_PIXELCOUNT, self.__path,
                              self.__log)
                self.__sectorsDict[sectorKey] = newSector
                return newSector
        
    def __convertToIndices(self, degreesLat, degressLong):
        """__convertToIndices(float degreesLat, float degreesLong)
        Returns int latIndex, int longIndex"""
        #The small value added is to resolve floating point errors
        longIndex = int(degressLong/self.__DEGREES_PER_PIXEL_LONG + 0.00000001)
        latIndex = int(degreesLat/self.__DEGREES_PER_PIXEL_LAT + 0.00000001)
        return latIndex, longIndex
    
    def __convertToDegrees(self, latIndex, longIndex):
        """__convertToDegrees(int latIndex, int longIndex)
        Returns float degreesLat, float degreesLong"""
        return latIndex*self.__DEGREES_PER_PIXEL_LAT, \
               longIndex*self.__DEGREES_PER_PIXEL_LONG
               
    @async
    def addLine(self, degreesLat, degreesLong, degreesLat2, degreesLong2):
        """addLine(float degreesLat, float degreesLong,
        float degreesLat2, float degreesLong2)
        Creates a line of Hard obstacles between two points"""    
        longDelta = lambda: degreesLong2 - degreesLong
        latDelta = lambda: degreesLat2 - degreesLat
        
        direction = 0
        if longDelta() == 0:
            if latDelta() < 0:
                direction = (1.5)*pi
            else:
                direction = pi/2.0
        else:
            direction = atan(latDelta()/longDelta())
            if longDelta() < 0:
                direction += pi
        
        
        #Pythagorean
        remainingDistance = lambda: sqrt(longDelta()**2+latDelta()**2)
        distanceToBeTraveled = self.MIN_DEGREES_PER_PIXEL
        
        while(remainingDistance() >= distanceToBeTraveled):       
            degreesLong += distanceToBeTraveled * cos(direction)
            degreesLat += distanceToBeTraveled * sin(direction)
            self.setPoint(degreesLat, degreesLong, 127)
            
        self.__log.debug("Line of Hard obstacles drawn between ("+
                         str(degreesLat) + ", " + str(degreesLong) +
                         ") and (" + str(degreesLat2) + ", " + str(degreesLong2) +
                         ")")
        
    @async
    def addCircle(self, centerDegreesLat, centerDegreesLong, radiusLat, radiusLong = None):
        """addCircle(float centerDegreesLat, float centerDegreesLong, 
        float radiusLat, [float radiusLong])
        Creates a hollow circle or ellipse of Hard obstacles
        centered on a point."""
        #Allow for circles
        if radiusLong == None: radiusLong = radiusLat
        #Enforce radius sign
        radiusLong = abs(radiusLong)
        radiusLat = abs(radiusLat)
        #Prevent divide by zero
        if radiusLong + radiusLat == 0:
            return self.setPoint(centerDegreesLat, centerDegreesLong)
        
        h = ((radiusLong-radiusLat)**2)/((radiusLong+radiusLat)**2)
        circum =  pi * (radiusLong + radiusLat)* (3.0 - sqrt(4.0-h))
        numPoints = circum / self.MIN_DEGREES_PER_PIXEL
        fullCircle = pi + pi
        deltaAngle = fullCircle / numPoints
        angle = 0
        while (angle < fullCircle):
            self.setPoint(centerDegreesLat + radiusLat * sin(angle),
                          centerDegreesLong + radiusLong * cos(angle),
                          127) 
            angle += deltaAngle
        self.__log.debug("Hollow circle of Hard obstacles centered on (" +
                         str(centerDegreesLat) + ", " + str(centerDegreesLong) + 
                         ") with radii of " + str(radiusLat) + " and " +
                         str(radiusLong) + " drawn.")
            
    class __Sector(object):
        """__Sector(int cornerLatIndex, int cornerLongIndex, 
        int sectorWidthPixelCount, string sectorFilepath,
        [logging log])
        To improve the memory usage and scalability of the system, points are grouped into sectors.  
        Each sector contains a square grid of contiguous points, addressed by GPS coordinates.
        Sectors covering all area are assumed to be present.  When information about a location 
        is requested or asked to be changed, the system will check if the sector containing 
        that point is loaded in memory.  If not, an attempt is made at loading that sector from 
        disk. If the file is not present, then a blank sector is created.
        
        Usage:
            sectorInstance = Sector(41050, 85103, 50, os.curdir)
            a_50_by_50_byte_array = sectorInstance.grid
            sectorInstance.setPixel(4,4,30) #Note that the 
            sectorInstance.save()"""       
        def __init__(self, cornerLatIndex, cornerLongIndex,
                     sectorWidthPixelCount, sectorFilepath,
                     log = logging): #Default to the root logger
            self.__cornerLongIndex = cornerLongIndex
            self.__cornerLatIndex = cornerLatIndex
            self.__SECTOR_WIDTH_PIXELCOUNT = int(sectorWidthPixelCount)
            self.__rlock = RLock()
            
            #Verify constructor parameter bounds
            if self.__SECTOR_WIDTH_PIXELCOUNT <= 0: raise Exception, \
                "Sector: Sector width in pixels cannot be <= 0"
            
            self.__log = log
            self.__sectorFilePathAndName = \
                os.path.join(sectorFilepath, str(cornerLatIndex) + "-" + str(cornerLongIndex) + ".sec")
            self.load()
        
        def load(self):
            """Load this sector from the anticipated location on disk"""
            with self.__rlock:
                #'dirty == True' means that the data in memory 
                #differs from that on the disk
                try:
                    #Attempt to load a sector file from disk with this name.
                    #If the file doesn't exist or isn't usable, 
                    #then make a signed byte array from scratch.
                    with open(self.__sectorFilePathAndName, "r") as fileHandle:
                        #Make an array of signed bytes from the decompressed file data
                        self.__confidenceGrid = array('b', zlib.decompress(fileHandle.read()))
                        #If the file that was loaded is the wrong size, 
                        #then delete the bad file and continue.
                        if (len(self.__confidenceGrid) != self.__SECTOR_WIDTH_PIXELCOUNT**2):
                            self.__log.error(
                                "Sector " + self.__sectorFilePathAndName + 
                                ": Existing file is the incorrect size; removing file.")
                            os.remove(self.__sectorFilePathAndName)
                            raise IOError
                    self.__dirty = False
                    self.__log.debug("Sector " + self.__sectorFilePathAndName + " loaded from disk")
                except Exception:  #zlib throws generic errors, so catch every Exception type.
                    self.__confidenceGrid = array('b') #signed byte
                    #TODO: Better filling of array and better array type
                    [self.__confidenceGrid.append(0) for x in 
                     xrange(self.__SECTOR_WIDTH_PIXELCOUNT**2)]
                    self.__dirty = True
                    self.__log.debug("Sector created; to be saved as " + self.__sectorFilePathAndName)
                self.__lastAccessed = time()
                        
        def save(self):
            """Write this sector's obstacle information to the predetermined location on disk"""
            try:
                with self.__rlock:
                    #If there is nothing new to write to the disk, don't waste the time.
                    if not self.__dirty: return
                    with open(self.__sectorFilePathAndName, "w") as fileHandle:
                        fileHandle.write(zlib.compress(self.__confidenceGrid.tostring()))    
                    self.__dirty = False
                self.__log.info("Sector " + self.__sectorFilePathAndName + " saved to disk")
            except IOError:
                self.__log.error("Unable to save sector as " + self.__sectorFilePathAndName)
                    

        
        age = property(lambda self: time() - self.__lastAccessed,
                       doc = "The floating point number of seconds since the last access")
        
        def getPixel(self, latIndex, longIndex):
            """getPixel(int latIndex, int longIndex)
            Returns the confidence value at that pixel"""
            latIndex %= self.__SECTOR_WIDTH_PIXELCOUNT
            longIndex %= self.__SECTOR_WIDTH_PIXELCOUNT
            self.__lastAccessed = time()
            with self.__rlock:
                return self.__confidenceGrid[latIndex * self.__SECTOR_WIDTH_PIXELCOUNT + longIndex]

        def setPixel(self, latIndex, longIndex, value):
            """setPixel(int latIndex, int longIndex, int value)
            Returns int newValue, boolean isChanged"""
            latIndex %= self.__SECTOR_WIDTH_PIXELCOUNT
            longIndex %= self.__SECTOR_WIDTH_PIXELCOUNT
            value = int(value)
            if (value < -128 or value > 127): 
                raise Exception, "Point value cannot be set to " + value
            self.__lastAccessed = time()
            with self.__rlock:
                #Only change the pixel value if the new value is different from the old.
                if (self.__confidenceGrid[latIndex * self.__SECTOR_WIDTH_PIXELCOUNT + 
                                        longIndex] != value):
                    self.__confidenceGrid[latIndex * self.__SECTOR_WIDTH_PIXELCOUNT + 
                                        longIndex] = value
                    self.__dirty = True
                    return value, True
                return value, False

            
        def changePixel(self, latIndex, longIndex, delta = 1):
            """changePixel(int latIndex, int longIndex, int delta)
            Returns int newValue, boolean isChanged"""
            latIndex %= self.__SECTOR_WIDTH_PIXELCOUNT
            longIndex %= self.__SECTOR_WIDTH_PIXELCOUNT
            delta = int(delta)
            self.__lastAccessed = time()
            with self.__rlock:
                #Get
                value = self.__confidenceGrid[
                    latIndex * self.__SECTOR_WIDTH_PIXELCOUNT + longIndex]
                
                #Check
                if delta == 0: return value, False
                if value == -128 and delta < 0: return -128, False
                if value == 126 and delta > 0: return 126, False
                
                value += delta
                if value < -128: value = -128
                if value > 126: value = 126
                
                #Set
                self.__confidenceGrid[latIndex * self.__SECTOR_WIDTH_PIXELCOUNT + 
                                    longIndex] = value
                self.__dirty = True
                return value, True
        
        lat =  property(lambda self: self.__cornerLatIndex, doc = "cornerLatIndex")
        long = property(lambda self: self.__cornerLongIndex, doc = "cornerLongIndex")
        grid = property(lambda self: self.__confidenceGrid, 
                        doc = "Discouraged but direct reference to the confidence grid")

    class __SectorUnloadThread(Thread, object):
        """__SectorUnloadThread(threading.RLock sectorListRlock,
        dict sectorsDict,
        int periodInSeconds, int sectorAgeThresholdInSeconds,
        [int logLevel])
        
        Sectors that have been accessed for the current execution remain in memory.  
        As a program executes over time, sectors would slowly build up over time,
        creating a memory leak situation.  This class is designed to prevent that situation.
        
        Once every 'periodInSeconds' seconds, this thread will acquire the lock provided
        and step through every sector in the list.
        If the sector is older than sectorSageThresholdInSeconds seconds,
        the sector is asked to write itself to disk and removed from the list,
        releasing the reference to the garbage collector."""
        def __init__(self, 
                     sectorListRlock,
                     sectorsDict, 
                     periodInSeconds,
                     sectorAgeThresholdInSeconds,
                     logLevel = logging.ERROR):
            self.__rlock = sectorListRlock
            self.__sectorsDict = sectorsDict
            self.__PERIOD = periodInSeconds
            self.__SECTOR_AGE_THRESHOLD = sectorAgeThresholdInSeconds
            self.__stopEvent = Event() #http://docs.python.org/lib/event-objects.html
            self.__stopEvent.set()
            
            #Verify constructor parameter bounds
            if self.__PERIOD < 0: raise Exception, \
                "SectorUnloadThread: Period cannot be less than 0"
            if self.__SECTOR_AGE_THRESHOLD < 0: raise Exception, \
                "SectorUnloadThread: Sector age threshold cannot be less than 0"

            #Configure the logger
            self.__log = logging.getLogger("SectorUnloader")
            self.__log.setLevel(logLevel)
            self.__log.debug("Created with period of " + str(self.__PERIOD) +
                               " and sector age threshold of " +
                               str(self.__SECTOR_AGE_THRESHOLD))
            
            Thread.__init__(self, name = "SectorUnloadThread")
            self.start()
       
        def stop(self):
            """Blocking call to disable the thread.
            If it is currently cleaning out old sectors,
            this call blocks until it finishes."""
            if self.__stopEvent.isSet():
                self.__log.debug("Already stopped")
            else:
                self.__log.debug("Attempting to stop thread")
                self.__stopEvent.set()
                #Stopping this thread is a blocking call because assuming the cleanup
                #functionality finished executing when it is actively removing sectors
                #can introduce instability.
                self.join()
                self.__log.debug("Stopped")
                Thread.__init__(self, name = "SectorUnloadThread")
           
        def run(self):
            self.__log.debug("Started")
            self.__stopEvent.clear()    #Allow a start() to follow a stop()
            
            #In the interest of efficiency and faster startup times,
            #don't search for old sector data at the beginning of the program.
            self.__stopEvent.wait(self.__PERIOD)
            while not self.__stopEvent.isSet():
                self.__log.info("Unloading old sector information...")
                unloadedCount = 0
                with self.__rlock:
                    #Timing data gathering is within the lock to give more
                    #accurate information.
                    startTime = time()
                    for key, sector in self.__sectorsDict.items():
                        if (sector.age >= self.__SECTOR_AGE_THRESHOLD):
                            sector.save()
                            del self.__sectorsDict[key]
                            unloadedCount += 1
                    
                    timeSpent = time() - startTime
                if unloadedCount > 0:
                    self.__log.info("Unloaded " + str(unloadedCount) + " sectors in "
                             + str(timeSpent) + "seconds" + 
                             " (" + str(timeSpent / unloadedCount) + " seconds/sector)")
                else:
                    self.__log.info("No sectors unloaded")
                #Since this thread only executes every two minutes, allow it
                #to wake up early in case the subsystem is asked to shut down.
                self.__stopEvent.wait(self.__PERIOD)