#Embry-Riddle Aeronautical University
#SE/CS/CE Senior Project 2007-08
#Control Team
#Jesse Berger, Cory Carson, Janelle Hilliard
#This module contains the Navigator class.
#It is responsible for navigating the ground vehicle around obstacles. 

from __future__ import with_statement #Necessary until Python 2.6 or 3.0
from ObstacleManager import ObstacleManager
from WaylistManager import WaylistManager
from util import async, distance, direction
from Waypoint import Waypoint
from math import sqrt, cos, sin, pi
from string import lower
from threading import Thread, RLock, Event, currentThread
from time import time,sleep
import logging

class Navigator(object): #New-style class declaration
    """Navigator(ObjectGen vgo,  #Reference to the truck object to navigate
    [ObstacleManager obstacleManager],
    [WaylistManager waylistManager],
    [int obstacleThreshold],    #The confidence value at which 
                                #obstacles are considered impassable
    [float maxDistance],        #The maximum number of degrees between
                                #user waypoints allowed to navigate over
                                #due to performance reasons
    [int maxNavWaypointsBetweenUserWaypoints], #If this many navigation
                                #waypoints are inserted between two user
                                #waypoints, then assume an infinite loop.
    [waypointModeUpdatePeriod], #How often (in seconds)
                                #to recalculate all navigation waypoints
    [truckUpdatePeriod],     #How often (in seconds) to check for the truck reaching a waypoint
    [followModeUpdatePeriod],   #How often (in seconds) to update the destination
                                #waypoint based on the plane's position
    [string mode],              #The mode to start the navigator in
    [logging.level logLevel])

    High-level navigation object for a ground vehicle represented 
    by an ObjectGen reference.  It uses a right-hand rule for avoidance,
    and if that never reaches the target, it uses a left-hand rule.
    
    If there are avoidance or performance problems with the logic,
    it may need to be replaced by a better algorithm, such as D*.
    
    Usage:
    #Single ground vehicle
        navInstance = Navigator(vehicle_object_to_control)
    #Multiple ground vehicles
        navInstance1 = Navigator(vehicle_object_to_control)
        navInstance2 = Navigator(second_vehicle_object_to_control, 
                                   navInstance1.obstacleManager)
                                   
    #Host the ObstacleManager instance on your Pyro daemon:
    uri = self.getDaemon().connect(navInstance.obstacleManager)
    referenceToReturnOverPyro = navInstance.obstacleManager.getProxy()                               
                                       
    navInstance.mode = "follow" #Not case sensitive
    #The ground vehicle connected to the vgo instance should now follow an aircraft.
    navInstance.mode = "follow"
    #No change in behavior
    navInstance.mode = "disabled"
    #The navigation logic is disabled - all navigation waypoints are cleared
    #and no new ones will be added 
    navInstance.mode = "waypoint"
    #The navigation logic is now in waypoint-to-waypoint mode.
    
    #**navInstance.waylist is a WaylistManager instance.
    #**See documentation on WaylistManager for more information.
    navInstance.waylist.append(Waypoint(20,20,0))
    #User waypoint appended to the waylist
    navInstance.waylist.append(Waypoint(20.0001,20.0002,0))
    #Another user waypoint appended to the waylist
    
    #**navInstance.obstacleManager is an ObstacleManager instance.
    #**See documentation on ObstacleManager for more information.
    key = navInstance.obstacleManager.subscribe()
    navInstance.obstacleManager.addCircle(20,20,0.0003,0.0004)
    #User defined (Hard) obstacles defined in an ellipse centered on (20,20)
    #with radii of 0.0003 degrees latitude and 0.0004 degrees longitude
    updateDeque = navInstance.obstacleManager.getUpdates(key)
    #collections.deque of tuples: (degreesLat, degreesLong, confidenceValue)
    #The values in the deque signify the points that have changed since the
    #subscription or last time updates were gotten.
    navInstance.obstacleManager.unsubscribe(key)
    #Listener is closing down, so don't fill up a deque for it.
    
    shallowCopy = navInstance.waylist[:]
    #If used in conjunction with Pyro, this makes a deep copy.
    #Useful when displaying waypoints on a user interface
    
    navInstance.waylist.remove(0)
    #The first user waypoint is removed from the list
    
    #Closing the system
    navInstance.close()
    
    Limitations:
    Note that while multiple vehicles may work, multiple ground vehicle features
    are out of scope for this year, including intravehicular avoidance
    and a persistent ObstacleManager instance.
    
    Cages of obstacles are not identified directly.  When they occur,
    an infinite loop error will be caught and all navigation waypoints
    between those two user waypoints will be deleted.
    """
    version = property(lambda self: 0, 
                       doc = "Different versions are not compatible")
    def __init__(self, vgo,                 
                 obstacleManager = None,    
                 waylistManager = None,     
                 obstacleThreshold = 50,    
                 maxDistance = 0.5,  
                 maxNavWaypointsBetweenUserWaypoints = 250,
                 waypointModeUpdatePeriod = 10,
                 truckUpdatePeriod = 0.1, 
                 followModeUpdatePeriod = 10,
                 startupMode = "waypoint",
                 clearRadius = 0.00005, 
                 logLevel = logging.INFO): 
        #For deployment, set level to logging.ERROR or logging.CRITICAL
        
        #To prevent a problem with orphan threads that cannot be garbage collected,
        #try self.close() to shut down the existing subsystem.
        #If the object has not been already instantiated, an 
        #AttributeError is raised.
        #This means that calling __init__ again will reset the navigator
        #and all referenced instances.
        try: 
            self.close()
        except AttributeError:
            pass
        
        #Future implementation may ask information to be logged to file,
        #and using the logging library allows this to be done with 
        #a configuration command to the log object.
        #http://docs.python.org/lib/module-logging.html
        logging.basicConfig()
        self.__log = logging.getLogger("Navigator")
        self.__log.setLevel(logLevel)
        
        if obstacleManager == None:
            obstacleManager = ObstacleManager(loggingLevel = logLevel)
        self.__obstacleManager = obstacleManager
        
        if waylistManager == None:
            waylistManager = WaylistManager(vgo, loggingLevel = logLevel)
        self.__waylistManager = waylistManager
        
        self.__waypointThread = self.__WaypointThread(
                self.__listwalker,
                self.__waylistManager,
                vgo,
                waypointModeUpdatePeriod,
                truckUpdatePeriod,
                self.__log)
        
        self.__followThread = self.__FollowThread(
                vgo,
                self.__listwalker,
                self.__waylistManager,
                followModeUpdatePeriod,
                self.__log)
        
        #Confidence value at which obstacles are to be avoided
        self.obstacleThreshold = obstacleThreshold
        
        #Infinite/near infinite loop protection
        self.__MAX_DISTANCE_TO_CALCULATE = maxDistance
        self.__MAX_NAV_BETWEEN_USER = int(maxNavWaypointsBetweenUserWaypoints)
        
        self.clearRadius = clearRadius
        
        #Verify constructor parameters
        if self.__MAX_DISTANCE_TO_CALCULATE < 0: raise Exception, \
            "Navigator: Max distance to navigate between cannot be less than 0 degrees"
        if self.__MAX_NAV_BETWEEN_USER <= 0: raise Exception, \
            "Navigator: Maximum navigation waypoints between user waypoints" + \
            "cannot be < 0"
        if self.__waylistManager.version != self.version: raise Exception, \
            "Version mismatch.  Navigator is " + str(self.version) + ", WaylistMananger "+ \
            "is " + str(self.__waylistManager.version)
        if self.__obstacleManager.version != self.version: raise Exception, \
            "Version mismatch.  Navigator is " + self.version + ", ObstacleMananger "+ \
            "is " + str(self.__obstacleManager.version)

        #Start the truck telemetry
        #vgo.sendWaylist([Waypoint(0,0,0)])
        #sleep(4)
        #vgo.sendWaylist([])
        
        self.__del__ = self.close
        self.mode = startupMode
        self.__log.debug("Initialized")
   
    def close(self):
        """Stop all owned active threads and write all relevant files to disk"""
        self.__log.debug("Closing...")
        self.mode = "disabled"
        self.__obstacleManager.close()
        self.__waylistManager.stop()
        self.__log.debug("Closed")
    
    def __setObstacleThreshold(self, value):
        """See property definition for obstacleThreshold"""
        value = int(value)
        if not -128 <= value < 128:
            raise Exception, \
            "Navigator: Cannot use an obstacle threshold of under -128 or over 127." \
            + " Tried " + str(value)
        else:
            self.__obstacleThreshold = value
            
    #lambda is a function definition operator.
    #http://www.secnetix.de/olli/Python/lambda_functions.hawk
    #properties allow easy access to the information but enforce certain access.
    #http://users.rcn.com/python/download/Descriptor.htm
    obstacleThreshold = property(lambda self: self.__obstacleThreshold,
        __setObstacleThreshold,
        doc = "The confidence value of which an obstacle is considered " + \
              "impassable and requires avoiding.")
    
    def __setClearRadius(self, value):
        """See property definition for clearRadius"""
        if value < 0:
            raise Exception, \
            "Navigator:  Cannot use a negative clear radius." \
            + " Tried " + str(value)
        else:
            self.__clearRadius = value
    
    clearRadius = property(lambda self: self.__clearRadius,
                           __setClearRadius,
                           doc = "The radius of information that must be clear")
    
    obstacleManager = property(lambda self: self.__obstacleManager,
        doc = "The ObstacleManager reference in use by this instance")
    
    #someNavigatorInstance.waylist.addWaypoint(waypoint)
    waylist = property(lambda self: self.__waylistManager,
        doc = "The WaylistManager reference in use by this instance")
    
#    Changes the navigation mode to a particular type:
#        "waypoint"
#            This is the default mode.
#            This navigates the truck to user waypoints in list order.
#            When the truck reaches the last waypoint in the list, the truck will go to the 
#            first in the list.
#        "follow"
#            This navigates the truck in the direction of the aircraft.  When this is enabled,
#            any previous waypoints stored in the list will be lost.
#        "disabled"
#            This disables all truck navigation logic.
    __mode = "uninitialized"
    mode = property(lambda self: self.__mode,
                    (lambda self, value: 
                    {'waypoint': self.__setWaypointMode, 
                    'follow': self.__setFollowMode, 
                    'disabled': self.__setDisabledMode
                    }[lower(value)]()),
                    doc = 'Modes: "waypoint", "follow", "disabled"')
    
    def resume(self):
        self.__waypointThread.resume()
        self.__followThread.resume()
        
    #Internal methods for setting the mode.
    def __setWaypointMode(self):
        #If the mode isn't changing, ignore the command.
        if self.__mode == "waypoint":
            self.__log.debug("Waypoint mode set when already in waypoint mode")
        else:
            self.__mode = "waypoint"
            self.__followThread.stop()
            self.__waypointThread.start()
            self.__log.info("Waypoint mode set")
    
    def __setFollowMode(self):
        if self.__mode == "follow":
            self.__log.debug("Follow mode set when already in follow mode")
        else:
            self.__mode = "follow"
            self.__waypointThread.stop()
            self.__followThread.start()
            self.__log.info("Follow mode set")
    
    def __setDisabledMode(self):
        if self.__mode == "disabled":
            self.__log.debug("Disabled mode set when already in disabled mode")
        else:
            self.__mode = "disabled"
            self.__waypointThread.stop()
            self.__followThread.stop()
            self.waylist.removeNavigationWaypoints()
            #self.waylist.commit()
            self.__log.info("Disabled mode set")
    
    def goToUserWaypoint(self, userIndex):
        """goToUserWaypoint(int userIndex)
        Will command the truck to go to a particular user waypoint"""
        with self.__waylistManager.lock:
            userList = self.__waylistManager.userWaypointList
            truckWaypoint = filter(lambda wp: hasattr(wp,'truck'), self.__waylistManager[:])[0]
            self.__waylistManager.remove(self.__waylistManager.getIndexOfWaypoint(truckWaypoint), navigationWaypoint = True)
            self.__waylistManager.insert(self.__waylistManager.getIndexOfWaypoint(userList[userIndex]),
                                         truckWaypoint)
        self.__log.info("Now navigating truck to user waypoint " + str(userIndex))
    
    #Uses tail recursion
    def __checkAndNudgeWaypoint(self, waypoint, 
                                  direction = pi, 
                                  moveByNumPixels = 1):
        """__checkAndNudgeWaypoint(Waypoint waypoint, 
        [radians direction], [numeric moveByNumPixels])
        
        Checks to see if a Waypoint is on a known obstacle.
        If it is, then move it in (direction) by (moveByNumPixels) pixels until
        it is not on any known obstacles.
        
        Generally called with just (waypoint, someOriginalDirection+1.5*pi)
        to move a waypoint perpendicular to the right of the original direction.
        
        Waypoints that have been bumped will have an attribute
        named 'bumped' set to True.  If the attribute doesn't exist, it is created.
        """
        
        
        #For each pixel in a 3x3grid around the waypoint
            #If the pixel is considered an obstacle
                #Tell the waypoint it's been bumped
                #call and return self with a bumped waypoint
        #otherwise, just return the unchanged waypoint
        
        for col in self.__obstacleManager.getGrid(waypoint.getLatitude() - self.clearRadius,
                                                  waypoint.getLongitude() - self.clearRadius,
                                                  waypoint.getLatitude() + self.clearRadius,
                                                  waypoint.getLongitude() + self.clearRadius):
            for pixel in col:
                if pixel >= self.__obstacleThreshold:
                    waypoint.bumped = True
                    return self.__checkAndNudgeWaypoint(
                        self.__nudgeWaypoint(waypoint, 
                                             direction,
                                             moveByNumPixels))
        else: #Else if there are no obstacles in the immediate area, then return the original.
            return waypoint
    
    def __nudgeWaypoint(self, waypoint, direction = pi, moveByNumPixels = 1):
        """__nudgeWaypoint(Waypoint waypoint, [radians direction], [numeric moveByNumPixels])
        Moves a waypoint by (moveByNumPixels) in (direction)"""
        waypoint.longitude += self.__obstacleManager.DEGREES_PER_PIXEL_LONG \
            * cos(direction) * moveByNumPixels
        waypoint.latitude += self.__obstacleManager.DEGREES_PER_PIXEL_LAT \
            * sin(direction) * moveByNumPixels
        return waypoint
        
    def __listwalker(self, startIndex, stopIndex, nudgeDirection=1.25*pi):
        """__listwalker(int startIndex, int stopIndex,
        [radians nudgeDirection])
        Creates navigation waypoints between every User waypoint in the waylist
        Slated for redesign pending truck current waypoint information"""
        with self.waylist.lock:
            if self.waylist.numUserWaypoints() < 2: return #Nothing to navigate
            index = startIndex
            numWaypointsInserted = 0
            while index != stopIndex:
                if numWaypointsInserted > self.__MAX_NAV_BETWEEN_USER:
                    raise InfiniteLoopError, \
                        "Too many navigation waypoints were inserted: "+ \
                        str(numWaypointsInserted)
                
                secondIndex = (index+1)%len(self.waylist)
                #Move the starting and ending waypoints as necessary based on obstacles
                self.waylist[index] = self.__checkAndNudgeWaypoint(self.waylist[index])
                self.waylist[secondIndex] = \
                    self.__checkAndNudgeWaypoint(self.waylist[secondIndex])
                
                firstPoint = self.waylist[index]
                secondPoint = self.waylist[secondIndex]
                
                returnedWaypoint = self.__linewalker(firstPoint, secondPoint, nudgeDirection)

                if returnedWaypoint != secondPoint:
                    #Otherwise, insert the navigation waypoint and try again.
                    self.waylist.insert(index+1, returnedWaypoint)
                    numWaypointsInserted += 1
                    
                    #In case listWalker start and stop spans more than two user waypoints
                    if stopIndex > index:
                        stopIndex += 1

                if index!=startIndex:
                    
                    checkIndex = startIndex
                    while checkIndex != index:
                        previousPoint = self.waylist[checkIndex]
                        nextPoint = self.waylist[(index+1)%len(self.waylist)]
                        hopefullyNextPoint = self.__linewalker(previousPoint, nextPoint, nudgeDirection)
                        
                        if hopefullyNextPoint == nextPoint:
                            for i in range(0,(index-checkIndex)):
                                if self.waylist[(checkIndex+1)%len(self.waylist)].getType() == 1:
                                    self.waylist.remove((checkIndex+1)%len(self.waylist), navigationWaypoint = True)
                                    if stopIndex >  index:
                                        stopIndex -= 1
                                        secondIndex -=1
                            index=(checkIndex+1)%len(self.waylist)
                            break
                        checkIndex = (checkIndex+1)%len(self.waylist)

                #If the returned waypoint is the same as the endpoint passed in
                if returnedWaypoint == secondPoint:
                    #It's clear.  Move on.
                    index=(index+1)%len(self.waylist)

                    
    def __linewalker(self, startWaypoint, endWaypoint, nudgeDirection=1.5*pi):
        """lineWalker(Waypoint startPoint, Waypoint endPoint, [radians nudgeDirection])
        This is the main avoidance logic.
        If there are navigation difficulties, it will be replaced by D*.
        Slated for redesign pending truck current waypoint information"""
        
        curWaypoint = Waypoint(startWaypoint.getLatitude(), startWaypoint.getLongitude() ,1)   
        curWaypoint.bumped = False #Dynamically add this attribute to this Waypoint object    
        
        remainingDistance = lambda: distance(endWaypoint,curWaypoint)
        
        #If two points are drastically far apart, don't spend the processing time
        #to calculate it
        if remainingDistance() > self.__MAX_DISTANCE_TO_CALCULATE:
            raise InfiniteLoopError, \
                "Points are too far apart to navigate between: "+ \
                               str(remainingDistance())+ " degrees"
        
        proximityThreshold = sqrt(self.__obstacleManager.DEGREES_PER_PIXEL_LONG**2 + 
                                  self.__obstacleManager.DEGREES_PER_PIXEL_LAT**2)
        
        dir = direction(startWaypoint, endWaypoint)
        
        #TODO minimum space to clear
        while(remainingDistance() > proximityThreshold):
            self.__nudgeWaypoint(curWaypoint, dir, 1)
            self.__checkAndNudgeWaypoint(curWaypoint, dir+nudgeDirection, 5)
            if curWaypoint.bumped: return curWaypoint
        return endWaypoint
    
    class __WaypointThread(Thread, object):
        """__WaypointThread(function listWalker,
        WaylistManager waylist,
        [numeric updatePeriodInSeconds],
        [logging.logger log])"""
        def __init__(self,
                     listwalker,
                     waylist,
                     vgo,
                     updatePeriodInSeconds,
                     truckUpdatePeriod,
                     log = logging):
            self.__listwalker = listwalker    #Function pointer
            self.__waylist = waylist          #WaylistManager
            self.__vgo = vgo
            self.__UPDATE_PERIOD_IN_SECONDS = updatePeriodInSeconds
            self.__TRUCK_UPDATE_PERIOD = truckUpdatePeriod
            self.__log = log
            
            #Verify constructor parameters
            if self.__UPDATE_PERIOD_IN_SECONDS < 0:
                raise Exception, "Waypoint mode update period cannot" \
                    +" be less than 0.  Was set to " + str(self.__UPDATE_PERIOD_IN_SECONDS)
            #TODO: Typechecking on other params
            
            self.__stopEvent = Event()
            self.__stopEvent.set()
            self.__pauseEvent = Event()
            self.resume = self.__pauseEvent.set 
            self.resume()
            Thread.__init__(self, name = "WaypointThread")
        
        def stop(self):
            if not self.__stopEvent.isSet():
                self.__log.debug("Stopping WaypointThread...")
                self.__stopEvent.set()
                self.join()
                Thread.__init__(self, name = "WaypointThread")
                self.__log.debug("WaypointThread stopped")
            else:
                self.__log.debug("WaypointThread already stopped")
        
        __BUMP_DIRECTION = pi/4
        def run(self):
            self.__log.debug("WaypointThread started")
            self.__stopEvent.clear()
            userNext = 0
            self.__waylist.lock.acquire()
            self.__waylist.clear()
            truckLocationWaypoint = Waypoint(0,0,3)
            truckLocationWaypoint.truck = True
            self.__waylist.append(truckLocationWaypoint)
            Thread(target = self.__truckUpdater, name = "TruckPositionUpdater", args = (truckLocationWaypoint, self.__TRUCK_UPDATE_PERIOD)).start()
            currentWaypoint = None
            while not self.__stopEvent.isSet():
                with self.__waylist.lock:
                    truckLocationWaypoint.type = 3
                    #Allows continuity of the lock from startup to inside the loop.
                    if currentWaypoint == None:
                        currentWaypoint = ""
                        self.__waylist.lock.release()
                        
                    userWaylist = self.__waylist.userWaypointList
                    numUserWaypoints = len(userWaylist)
    
                    
                    #Note that the truck waypoint above counts as a user waypoint
                    if numUserWaypoints >= 2:
                        #Increment
                        userNext += 1
                        
                        #Correct for size
                        userNext %= numUserWaypoints
                        
                        #Get waypoint object references
                        currentWaypoint = userWaylist[userNext-1]
                        nextWaypoint = userWaylist[userNext]
                       
                        #Navigate
                        try:
                            self.__waylist.removeNavigationWaypoints(userNext-1, userNext)
                            self.__listwalker(self.__waylist.getIndexOfWaypoint(currentWaypoint),
                                              self.__waylist.getIndexOfWaypoint(nextWaypoint),
                                              pi+self.__BUMP_DIRECTION)
                        except InfiniteLoopError:
                            try:
                                self.__waylist.removeNavigationWaypoints(userNext-1, userNext)
                                self.__listwalker(self.__waylist.getIndexOfWaypoint(currentWaypoint),
                                                  self.__waylist.getIndexOfWaypoint(nextWaypoint),
                                                  pi-self.__BUMP_DIRECTION)
                            except InfiniteLoopError:
                                self.__waylist.removeNavigationWaypoints(userNext-1, userNext)
                                self.__log.error("Aborted navigation between " +
                                                 "user waypoints " +
                                                 str(userNext) + ".  " + 
                                                 "Too many intermediate waypoints created.")
                                self.__vgo.setHaltMode()
                                self.__vgo.setNavError(True)
                                truckLocationWaypoint.type = 1
                                userNext -= 1
                                self.__pauseEvent.clear()
                                self.__waylist.lock.release()
                                self.__pauseEvent.wait()
                                self.__pauseEvent.clear()
                                self.__waylist.lock.acquire()
                                continue
                        self.__waylist.commit(fromWaypoint = truckLocationWaypoint,
                            toWaypoint = userWaylist[(userWaylist.index(truckLocationWaypoint)+1)%numUserWaypoints])
                    truckLocationWaypoint.type = 1
                self.__stopEvent.wait(self.__UPDATE_PERIOD_IN_SECONDS)
        
        __ALLOWED_PROXIMITY = 0.00012            
        def __truckUpdater(self, truckLocationWaypoint, updatePeriod):
            while not self.__stopEvent.isSet():
                with self.__waylist.lock:
                    self.__pauseEvent.wait()
                    truckLocationWaypoint.type = 3
                     #Update the truck waypoint location information
                    truckLocationWaypoint.latitude = float(self.__vgo.getVehicleLatitude())
                    truckLocationWaypoint.longitude = float(self.__vgo.getVehicleLongitude())
                    userWaylist = self.__waylist.userWaypointList
                    numUserWaypoints = len(userWaylist)
                    if numUserWaypoints > 2:
                        truckIndex = userWaylist.index(truckLocationWaypoint)
                        if distance(truckLocationWaypoint, userWaylist[truckIndex+1-numUserWaypoints]) <= self.__ALLOWED_PROXIMITY:
                            self.__waylist.remove(self.__waylist.getIndexOfWaypoint(
                                                            truckLocationWaypoint),
                                                          navigationWaypoint = True)
                            nextWaypoint = userWaylist[truckIndex+1-numUserWaypoints]
                            self.__waylist.insert(self.__waylist.getIndexOfWaypoint(
                                                            nextWaypoint),
                                                          truckLocationWaypoint)
                            self.__waylist.commit(fromWaypoint = truckLocationWaypoint,
                                                      toWaypoint = userWaylist[(truckIndex+2)%numUserWaypoints])
                            #If the truck arrived at a Halt waypoint
                            if nextWaypoint.getType() == 2:
                                self.__log.info("Halt waypoint encountered.  Waiting for " + str(nextWaypoint.getStopTime()) + " seconds")
                                self.__vgo.setHaltMode()
                                truckLocationWaypoint.type = 1
                                self.__waylist.lock.release()
                                self.__stopEvent.wait(nextWaypoint.getStopTime())
                                self.__waylist.lock.acquire()
                    truckLocationWaypoint.type = 1
                self.__stopEvent.wait(updatePeriod) 
                        
    class __FollowThread(Thread, object):
        """__WaypointThread__(Navigator navigator, ObjectGen vgo,
        [logging.log log], [numeric updatePeriodInSeconds])"""
        #TODO: Discuss communication overhead for this function
        def __init__(self,
                     vgo,
                     listwalker,
                     waylist, 
                     updatePeriodInSeconds,
                     log = logging):
            self.__vgo = vgo
            self.__listwalker = listwalker
            self.__waylist = waylist
            self.__UPDATE_PERIOD_IN_SECONDS = updatePeriodInSeconds
            self.__log = log
            
            #Verify constructor parameters
            if self.__UPDATE_PERIOD_IN_SECONDS < 0:
                raise Exception, "Follow mode update period cannot" \
                    +" be less than 0.  Was set to "+ str(self.__UPDATE_PERIOD_IN_SECONDS)
            #TODO: Typechecking on other params
    
            self.__stopEvent = Event()
            self.__stopEvent.set()
            self.__pauseEvent = Event()
            self.resume = self.__pauseEvent.set
            self.resume()
            Thread.__init__(self, name = "FollowThread")
        
        def stop(self):
            if not self.__stopEvent.isSet():
                self.__log.debug("Stopping FollowThread...")
                self.__stopEvent.set()
                self.join()
                Thread.__init__(self, name = "FollowThread")
                self.__log.debug("FollowThread stopped")
            else:
                self.__log.debug("FollowThread already stopped")
        
        __BUMP_DIRECTION = pi/4 
        def run(self):
            self.__log.debug("FollowThread started")
            self.__stopEvent.clear()
            while not self.__stopEvent.isSet():
                with self.__waylist.lock:
                    self.__waylist.clear()
                    self.__waylist.append(Waypoint(float(self.__vgo.getVehicleLatitude()),
                                                     float(self.__vgo.getVehicleLongitude()),
                                                     3))
                    self.__waylist.append(Waypoint(self.__vgo.getPlanePositionLat(),
                                                     self.__vgo.getPlanePositionLong(),
                                                     3))
                    #Navigate
                    try:
                        self.__listwalker(0, 1, pi+self.__BUMP_DIRECTION)
                    except InfiniteLoopError:
                        try:
                            self.__waylist.removeNavigationWaypoints(None, None)
                            self.__listwalker(0, 1, pi-self.__BUMP_DIRECTION)
                        except InfiniteLoopError:
                            self.__waylist.removeNavigationWaypoints(None, None)
                            self.__log.error("Aborted navigation avoidance to plane.  " + 
                                             "Too many intermediate waypoints created.")
                            self.__vgo.setHaltMode()
                            self.__vgo.setNavError(True)
                            self.__pauseEvent.clear()
                            self.__waylist.lock.release()
                            self.__pauseEvent.wait()
                            self.__pauseEvent.clear()
                            self.__waylist.lock.acquire()
                            continue
                    self.__waylist[0].type = 1
                    self.__waylist.remove(0, navigationWaypoint = True)
                    self.__waylist.append(Waypoint(5,5,3))
                    self.__waylist[1].type = 1
                    self.__waylist.commit()
                self.__stopEvent.wait(self.__UPDATE_PERIOD_IN_SECONDS)

class InfiniteLoopError(Exception):
    def __init__(self,value="Infinite loop state"):
        self.parameter = value
    def __str__(self):
        return repr(parameter)
                