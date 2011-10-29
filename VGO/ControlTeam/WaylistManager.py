#Embry-Riddle Aeronautical University
#SE/CS/CE Senior Project 2007-08
#Control Team
#Jesse Berger, Cory Carson, Janelle Hilliard

from __future__ import with_statement #Necessary until Python 2.6 or 3.0
from Queue import Queue
from Waypoint import Waypoint
from string import lower
from threading import Thread, RLock, Lock
import logging

class WaylistManager(Thread, object):
    """WaylistManager(ObjectGen vgo, [logging.level loggingLevel])
    WaylistManager allows multiple thread-safe accesses to a list of waypoints by type.
    Navigation waypoints do not have to wait for user waypoint operations to complete.
    
    Modification functions that receive a user waypoint (type != 1), a lock is grabbed
    and it is put into a queue.  This queue should never have more than one waypoint in it -
    it is merely a way to not block an outside caller when a navigation thread has the lock
    on the waylist.
    
    In addition, as a temporary workaround, waypoints of type 3 can be appended directly.
    
    There is a special functionality regarding this.  Consider the situation:
    Navigation thread acquires the waylist lock
    Blackbird GUI inserts a user waypoint at index 3
    Blackdog GUI inserts a user waypoint at index 3
    Navigation thread releases the waylist lock.
    Blackbird waypoint gets inserted at 3
    Blackdog waypoint gets inserted at 3, moving Blackbird waypoint to index 4
    
    There could be the situation where the Blackdog GUI does not wish to just append
    if the user waypoints are in the middle of being changed.  Perhaps that waypoint
    needs to be inserted after the Blackbird waypoint.
    To allow this, the functions (append, insert, update, remove) take
    an additional optional boolean parameter: ignoreChangingWaylist.
    If the waylist is being changed, an exception is raised (WaylistChangingError).
    
    One way to use this functionality would be:
    try:
        waylistInstance.insert(index, someWaypoint, ignoreChangingWaylist = False)
    except Exception:    #or if WaylistChangedError is imported, except WaylistChangedError:
        #Force a screen update to show the new waylist
        #Tell the user to reconfirm their waypoint insert index
    """
    version = property(lambda self: 0, 
                       doc = "Different versions are not compatible")
    def __init__(self, vgo, loggingLevel = logging.ERROR):
        self.__vgo = vgo
        self.__updateRequests = Queue()
        self.__numInQueueLock = Lock()
        self.__entireListLock = RLock()
        self.__waylist = []
        logging.basicConfig()
        self.__log = logging.getLogger("WaylistManager")
        self.__log.setLevel(loggingLevel)
        Thread.__init__(self, name = "WaylistManager")
        self.__del__ = self.stop
        self.start()

    __stopThread = True   
    #TODO: Protect this method
    def stop(self):
        if self.__stopThread == True:
            self.__log.debug("Already stopped")
        else:
            self.__log.debug("Stopping...")
            self.__stopThread = True
            #Breaks the 'block forever' call in run()
            self.__updateRequests.put([lambda x,y: None,None,None],False)
            self.join()
            Thread.__init__(self, name = "WaylistManager")
            self.__log.debug("Stopped")
                 
    def run(self):
        self.__stopThread = False
        while self.__stopThread == False:
            waylistModification = self.__updateRequests.get(True) #Block forever
            waylistModification[0](waylistModification[1],waylistModification[2])
        
    #someWaypoint = someNavigatorInstance.waylist[4]
    def __getitem__(self, index):
        #If the below line has an error, set your project type to Python 2.5
        with self.__entireListLock:
            try:
                return self.__waylist[index]
            except IndexError:
                self.__log.debug("Someone attempted to access a waypoint index that doesn't exist"+
                                   ": " + str(index) + ", len(waylist)="+str(len(self.__waylist)))
                raise IndexError

    #someNavigatorInstance.waylist[4] = someWaypoint
    def __setitem__(self, index, value):
        """Deprecated.
        Use .update()"""
        with self.__entireListLock:
            try:
                self.__waylist[index] = value
            except IndexError:
                self.__log.debug("Someone attempted to access a waypoint index that doesn't exist"+
                                   ": " + str(index) + ", len(waylist)="+str(len(self.__waylist)))
                raise IndexError
    
    #shallowListCopy = someNavigatorInstance.waylist[:]
    def __getslice__(self, start = None, stop = None, step = None):
        with self.__entireListLock:
            return self.__waylist[start:stop]
    
    #length = len(someNavigatorInstace.waylist)
    def __len__(self):
        with self.__entireListLock:
            return len(self.__waylist)
    
    lock = property(lambda self: self.__entireListLock,
                    doc = "Allow a Navigator instance to lock the waylist")
    
    #"Package" access level would be preferred when Python supports it.
    userWaypointList = property(lambda self: filter(
                          lambda waypoint: waypoint.getType() != 1, self.__waylist),
                          doc = "Returns a shallow copy of the subset of the " +
                          "waylist that contains only non-nav waypoints. " +
                          "Only intended for Navigation instances to use.")
    
    __numInQueue = 0    #Guarded by self.__numInQueueLock
    def append(self, waypoint, ignoreChangingWaylist = True):
        """append(Waypoint waypoint, [boolean ignoreChangingWaylist])
        Appends a waypoint to the waylist.
        
        If the waypoint is a user waypoint, then the waypoint change is added
        to an update request queue.  This allows navigation functions
        to lock the waylist without blocking user interfaces.
        If the user interface desires to know if there are other
        pending changes, set ignoreChangingWaylist to False.
        Doing so will raise a WaylistChangingError exception
        if there are other changes pending."""
        if self.__stopThread: raise Exception, "WaylistManager thread not executing"
        if waypoint.getType() == 1 or waypoint.getType() == 3:
            #if it is a navigation waypoint or Follow waypoint
            #just let it through in a synchronous fashion
            with self.__entireListLock: return self.__waylist.append(waypoint)
                
        with self.__numInQueueLock:
            if not ignoreChangingWaylist and self.__numInQueue > 0:
                raise WaylistChangingError
            self.__numInQueue += 1
        self.__updateRequests.put([self.__append, waypoint, None]) #Put it on the list
        self.__log.debug("Waypoint(" + str(waypoint.getLatitude()) +\
                         ", " + str(waypoint.getLongitude()) + ", " +\
                         str(waypoint.getType()) + ") append action queued")
                

    def insert(self, index, waypoint, ignoreChangingWaylist = True):
        """insert(int index, Waypoint waypoint, [boolean ignoreChangingWaylist])
        Inserts a waypoint to the waylist at index.  If the waypoint is a user waypoint,
        the index is a user index.  Otherwise, its the true list index.
        
        If the waypoint is a user waypoint, then the waypoint change is added
        to an update request queue.  This allows navigation functions
        to lock the waylist without blocking user interfaces.
        If the user interface desires to know if there are other
        pending changes, set ignoreChangingWaylist to False.
        Doing so will raise a WaylistChangingError exception
        if there are other changes pending."""
        if self.__stopThread: raise Exception, "WaylistManager thread not executing"
        if waypoint.getType() == 1 or waypoint.getType() == 3: #if it is a navigation waypoint
            #just let it through in a synchronous fashion
            with self.__entireListLock: return self.__waylist.insert(index, waypoint)
        
        with self.__numInQueueLock:
            if not ignoreChangingWaylist and self.__numInQueue > 0:
                raise WaylistChangingError
            self.__numInQueue += 1
        self.__updateRequests.put([self.__insert, waypoint, index])
        self.__log.debug("Waypoint(" + str(waypoint.getLatitude()) +\
                         ", " + str(waypoint.getLongitude()) + ", " +\
                         str(waypoint.getType()) + ") insert action at " +\
                         str(index) + " queued")
         
    #named 'update' to be consistent with the Python built-in dictionary's functions    
    def update(self, index, waypoint, ignoreChangingWaylist = True):
        """update(int index, Waypoint waypoint, [boolean ignoreChangingWaylist])
        Updates index to a new waypoint.  If the waypoint is a user waypoint,
        the index is a user index.  Otherwise, its the true list index.
        
        If the waypoint is a user waypoint, then the waypoint change is added
        to an update request queue.  This allows navigation functions
        to lock the waylist without blocking user interfaces.
        If the user interface desires to know if there are other
        pending changes, set ignoreChangingWaylist to False.
        Doing so will raise a WaylistChangingError exception
        if there are other changes pending."""
        if self.__stopThread: raise Exception, "WaylistManager thread not executing"
        if waypoint.getType() == 1 or waypoint.getType() == 3:
            with self.__entireListLock:
                if self.__waylist[index].getType() == 1 or self.__waylist[index].getType() == 3:
                    self.__waylist[index] = waypoint
                else:
                    raise NotANavigationWaypointError
            return
                    
        with self.__numInQueueLock:
            if not ignoreChangingWaylist and self.__numInQueue > 0:
                raise WaylistChangingError
            self.__numInQueue += 1
        self.__updateRequests.put([self.__update, waypoint, index])
        self.__log.debug("Waypoint(" + str(waypoint.getLatitude()) +\
                         ", " + str(waypoint.getLongitude()) + ", " +\
                         str(waypoint.getType()) + ") update action at " +\
                         str(index) + " queued")
    
    #Note the difference between this remove and the built-in removes:
    #This remove takes the user waypoint index, not the object reference to remove
    def remove(self, index, ignoreChangingWaylist = True, navigationWaypoint = False):
        """remove(int index, [boolean ignoreChangingWaylist], [boolean navigationWaypoint])
        Removes a waypoint at index.  If the waypoint is a user waypoint,
        the index is a user index.  Otherwise, its the true list index.
        
        If the waypoint is a user waypoint, then the waypoint change is added
        to an update request queue.  This allows navigation functions
        to lock the waylist without blocking user interfaces.
        If the user interface desires to know if there are other
        pending changes, set ignoreChangingWaylist to False.
        Doing so will raise a WaylistChangingError exception
        if there are other changes pending."""
        if self.__stopThread: raise Exception, "WaylistManager thread not executing"
        #Let navigation waypoints through
        if navigationWaypoint:
            with self.__entireListLock:
                if self.__waylist[index].getType() == 1 or self.__waylist[index].getType() == 3:
                    del self.__waylist[index]
                else:
                    raise NotANavigationWaypointError, "type = " + str(self.__waylist[index].getType())
            return
                    
        with self.__numInQueueLock:
            if not ignoreChangingWaylist and self.__numInQueue > 0:
                raise WaylistChangingError
            self.__numInQueue += 1
        self.__updateRequests.put([self.__remove, None, index])
        self.__log.debug("User waypoint remove action at " +\
                         str(index) + " queued")
        
    def __append(self, waypoint, ignoredParameter):
        """__append(Waypoint waypoint, None ignoredParameter)
        Appends the user waypoint at the end of the list"""
        with self.__entireListLock:
            self.__waylist.append(waypoint)
            if len(self.__waylist)==1:
                self.commit()
        with self.__numInQueueLock: self.__numInQueue -= 1
        self.__log.info("User waypoint(" + str(waypoint.getLatitude()) +\
                         ", " + str(waypoint.getLongitude()) + ", " +\
                         str(waypoint.getType()) + ") appended")
        
    def __insert(self, waypoint, userIndex):
        """__insert(Waypoint waypoint, int userIndex)
        Inserts the waypoint before userIndex"""
        with self.__entireListLock:
            self.__waylist.insert(self.getUserWaypointIndex(userIndex), waypoint)
        with self.__numInQueueLock: self.__numInQueue -= 1
        self.__log.info("User waypoint(" + str(waypoint.getLatitude()) +\
                         ", " + str(waypoint.getLongitude()) + ", " +\
                         str(waypoint.getType()) + ") inserted at " +\
                         str(userIndex))
    
    def __update(self, waypoint, userIndex):
        """__update(Waypoint waypoint, int userIndex)
        Replaces the waypoint at userIndex with the waypoint parameter"""
        with self.__entireListLock:
            realIndex = self.getUserWaypointIndex(userIndex)
            self.__waylist.insert(realIndex, waypoint)
            del self.__waylist[realIndex+1]
        with self.__numInQueueLock: self.__numInQueue -= 1
        self.__log.info("User waypoint(" + str(waypoint.getLatitude()) +\
                         ", " + str(waypoint.getLongitude()) + ", " +\
                         str(waypoint.getType()) + ") updated at " +\
                         str(userIndex))
    
    def __remove(self, ignoredParameter, userIndex):
        """__remove(None ignoredParameter, int userIndex)
        Remove the user waypoint at userIndex"""
        with self.__entireListLock:
            del self.__waylist[self.getUserWaypointIndex(userIndex)]
        with self.__numInQueueLock: self.__numInQueue -= 1
        self.__log.debug("User waypoint at " + str(userIndex) + " removed")
        
    def clear(self):
        """Remove all waypoints"""
        with self.__entireListLock: 
            self.__waylist = []
            self.commit()
        
    def removeNavigationWaypoints(self, userStartIndex = None, userStopIndex = None):
        """removeNavigationWaypoints([int userStartIndex], [int userStopIndex])        
        Remove only Navigation waypoints from userStartIndex to userStopIndex.
        If userStartIndex is greater than userStopIndex, then the function
        will 'wrap around'; that is, from userStartIndex to end of list, and
        then start of list to userStopIndex.
        
        The value of 'None' signifies the end/start of the list.
        
        Note that when userStartIndex == userStopIndex, it has the same
        functionality as called with None, None or empty parameters."""
        with self.__entireListLock:
            try:
                startIndex = self.getUserWaypointIndex(userStartIndex)
            except IndexError:
                startIndex = None
            try:
                stopIndex = self.getUserWaypointIndex(userStopIndex)
            except IndexError:
                stopIndex = None
                
            if stopIndex > startIndex or startIndex == None or stopIndex == None:
                self.__removeNavigationWaypoints(startIndex, stopIndex)
            else:
                self.__removeNavigationWaypoints(startIndex, None)
                self.__removeNavigationWaypoints(None, stopIndex)
    
    def __removeNavigationWaypoints(self, startIndex, stopIndex):
        """See removeNavigationWaypoints()"""
        waylist = self.__waylist; remove = self.__waylist.remove #performance optimization
        [remove(waypoint) for waypoint in 
         filter(lambda waypoint: waypoint.getType() == 1, waylist[startIndex:stopIndex])]
    
    __oldList = []
    def commit(self, vgo = None, fromWaypoint = None, toWaypoint = None):
        """commit([ObjectGen vgo], [Waypoint fromWaypoint], [Waypoint toWaypoint])
        Takes the active waylist in memory and 'commit's a portion to the ground vehicle via it's VGO.
        The waylist can be committed to a different VGO if desired by passing in the reference.
        
        The subset of the list to be sent is from fromWaypoint to toWaypoint."""
        if vgo == None: vgo = self.__vgo
        with self.__entireListLock:
            try:
                secondIndex = self.getIndexOfWaypoint(toWaypoint)+1
            except (ValueError, IndexError):
                secondIndex = None
            try:
                firstIndex = self.getIndexOfWaypoint(fromWaypoint)+1
            except (ValueError, IndexError):
                firstIndex = None
            self.__log.debug("Sending waylist["+str(firstIndex)+":" + str(secondIndex) + "]")
            
            if firstIndex==None or secondIndex==None:
                return vgo.sendWaylist([])
            
            waylistToSend = self.__waylist[firstIndex:secondIndex]
            length = len(self)
            truckIndex = firstIndex-1
            indexToBeAppended = secondIndex%length
            numWaypointsAppended = 0
            while(numWaypointsAppended<3):
                if indexToBeAppended != truckIndex:
                    waylistToSend.append(self[indexToBeAppended])
                    numWaypointsAppended=numWaypointsAppended+1
                indexToBeAppended = (indexToBeAppended+1)%length
                
            if len(self.__oldList) != len(waylistToSend):
                self.__oldList = waylistToSend
                return vgo.sendWaylist(waylistToSend)
            for index in range(len(waylistToSend)):
                if not self.__oldList[index].equals(waylistToSend[index]):
                    self.__oldList = waylistToSend
                    return vgo.sendWaylist(waylistToSend)
        
    def getUserWaypointIndex(self, userIndex):
        """getUserWaypointIndex(int userIndex)
        Returns the real list index of a user waypoint index"""
        if userIndex == None: return None
        with self.__entireListLock:
            return self.__waylist.index(self.userWaypointList[userIndex])
    
#    def getNextUserWaypointIndex(self, userIndex):
#        """getNextUserWaypointIndex(int userIndex)
#        Returns the real list index of the next user waypoint index"""
#        with self.__entireListLock:
#            userIndex = (userIndex + 1) % len(self.userWaypointList)
#            return self.getUserWaypointIndex(userIndex)
#    
#    def getPrevUserWaypointIndex(self, userIndex):
#        """getPrevUserWaypointIndex(int userIndex)
#        Returns the real list index of the previous user waypoint index"""
#        return self.getUserWaypointIndex(userIndex-1) #Note: No modulus needed.
    
    def getIndexOfWaypoint(self, waypoint):
        """getIndexOfWaypoint(Waypoint waypoint)
        Returns the real list index of a given waypoint"""
        with self.__entireListLock:         
                return self.__waylist.index(waypoint)
        
    def numUserWaypoints(self):
        """Returns the number of user waypoints"""
        with self.__entireListLock:
            return len(self.userWaypointList)
            
    def numNavigationWaypoints(self):
        """Returns the number of navigation waypoints"""
        with self.__entireListLock:
            return sum([waypoint.getType() == 1 for waypoint in self.__waylist])
    
    def numTypeWaypoints(self, type):
        """Returns the number of waypoints of a certain type"""
        with self.__entireListLock:
            return sum([waypoint.getType() == type for waypoint in self.__waylist])                

    
#This provides a way to notify the caller that the waylist
#was in the middle of being changed when they asked to make one themselves.
class WaylistChangingError(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return repr("The waylist was being changed.  "+
                 "Please check your index and try again")
class NotANavigationWaypointError(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return repr("That was not a navigation waypoint")