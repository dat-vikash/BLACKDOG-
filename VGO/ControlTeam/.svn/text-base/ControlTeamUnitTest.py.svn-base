#Embry-Riddle Aeronautical University - SE450 - Senior Design, Fall 2007
#Control Team
#Jesse Berger, Cory Carson, Janelle Hilliard

import unittest
import sys
from Control import *
from ObstacleManager import *

#Package local copy for testing purposes
class Waypoint:    
    def __init__(self, latitude, longitude, type):
        self.latitude = latitude
        self.longitude = longitude        
        self.type = type
        
        self.latitudeSecTolerance = 0.000001
        self.longitudeSecTolerance = 0.000001
                
    def getLatitude(self):
        return self.latitude
    def getLongitude(self):
        return self.longitude
    def getType(self):
        return self.type
    
    def __str__(self):
        return "Lat: " + str(self.latitude) + " Lon: " + str(self.longitude) + " Type: " + str(self.type) 

#Handy function for easy printing of a grid when there is a problem.
def gridToString(grid):
    ret = "\n"
    for y in range(len(grid[0])-1, -1, -1):
        ret = ret + " "
        for x in range(0, len(grid)):
            ret = ret + str(grid[x][y]) + " "
        ret = ret + "\n"
    return ret

class ObstacleManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.prefix =  "ControlTeam: ObstacleManager: "
        self.om = ObstacleManager()
    
    def tearDown(self):
        self.om.close()

class ControlTestCase(unittest.TestCase):
    def setUp(self):
        self.prefix =  "ControlTeam: Control: "
        self.con = Control()
        self.om = self.con.getObsManager()
        
    def tearDown(self):
        self.con.close()
        
class ObstacleManagerTest(ObstacleManagerTestCase):
    def testC1(self):
        self.om.clearAll()
        retVal = self.om.changePoint(0.000073, 0.000002, 1)
        assert retVal == 1, self.prefix + "C1: Point not set properly.  Should be 1, returned " + str(retVal)
        retVal = self.om.changePoint(0.000003, 0.000065, 5)
        assert retVal == 5, self.prefix + "C1: Point not set properly.  Should be 5, returned " + str(retVal)
        retVal = self.om.changePoint(0.000024, 0.000038, 9)
        assert retVal == 9, self.prefix + "C1: Point not set properly.  Should be 9, returned " + str(retVal)
        grid = self.om.getGrid(0.0,0.0,0.000090,0.000090)
        assert len(grid[0]) == 10, self.prefix + "C1: Grid too high.  Expected 10, got " + str(len(grid[0]))
        assert len(grid) == 10, self.prefix + "C1: Grid too wide.  Expected 10, got " + str(len(grid))
        for x in range(0, len(grid)):
            for y in range(0, len(grid[0])):
                if x == 7 and y == 0:
                    assert grid[x][y] == 1, self.prefix + "C1: Point recalled incorrectly. (7,0) should be 1, is " + str(grid[x][y]) + gridToString(grid)
                elif x == 0 and y == 6:
                    assert grid[x][y] == 5, self.prefix + "C1: Point recalled incorrectly. (0,6) should be 5, is " + str(grid[x][y]) + gridToString(grid)
                elif x == 2 and y == 3:
                    assert grid[x][y] == 9, self.prefix + "C1: Point recalled incorrectly. (2,3) should be 9, is " + str(grid[x][y]) + gridToString(grid)    
                else:
                    assert grid[x][y] == 0, self.prefix + "C1: Point recalled incorrectly. (" + str(x) + "," + str(y) + ") should be 0, is " + str(grid[x][y]) + gridToString(grid)
                   
    def testC2(self):
        self.om.getGrid(0.0,0.0,0.00145,0.00145)
        self.om.saveAll()
        requiredFiles = ["0-0.sec", "0-10.sec", "10-0.sec", "10-10.sec"]
        files = os.listdir(self.om.path)
        for file in files:
            if file[-4:] == ".sec":
                if file in requiredFiles:
                    requiredFiles.remove(file)
        assert len(requiredFiles) == 0, self.prefix + "C2: Files not created: " + str(requiredFiles)
        
    def testC5(self):
        self.om.clearAll()
        self.om.unloader.sleepTime = 1
        self.om.unloader.expireTime = 0
        self.om.changePoint(0.000073, 0.000002, 1)
        time.sleep(12)
        found = False
        self.om.unloader.stop()
        assert len(self.om.sectors) == 0, self.prefix + "C5: Unloader thread did not remove sector from memory"
        files = os.listdir(self.om.path)
        for file in files:
            if file == "0-0.sec":
                found = True
                break
        if not found:
            assert False, self.prefix + "C5: Unloader thread did not save sector file 0-0.sec"
            
    def testC9(self):
        self.om.clearAll()
        self.om.addObjectByLine(0.000073, 0.000002, 0.000023, 0.000045)
        
    def testC10(self):
        self.om.clearAll()
        self.om.addObjectByCircle(0.000073, 0.000002, 0.00035, 0.00076)
        
    def testC11(self):
        self.om.clearAll()
        self.om.addObjectByCircle(0.000002, 0.000073, 0.00035, 0.00035)        
        
class ControlTest(ControlTestCase):
    def testC3(self):
        self.om.clearAll()
        self.om.changePoint(10,10,5)
        waypoint = self.con.validateWaypoint(Waypoint(10.00001, 10.00001, "waypoint"))
        assert waypoint.getLatitude() == 10.00001 and waypoint.getLongitude() == 10.00001, self.prefix + "C3: Waypoint nudged when shouldn't have been"
        
    def testC4(self):
        self.om.clearAll()
        self.om.changePoint(0.0009, 0.0009, 6)
        waypoint = self.con.validateWaypoint(Waypoint(0.0009, 0.0009, "waypoint"))
        assert not (waypoint.getLatitude() == 0.0009 and waypoint.getLongitude() == 0.0009), self.prefix + "C4: Waypoint not nudged when it should have been"
    
    #def testExtra(self):
    #    self.om.clearAll()
    #    self.om.changePoint(0.00005,0.00005, 7)
    #    self.om.changePoint(0.000049497,0.0000636396, 7)
    #    self.om.changePoint(0.0001,0.00005, 7)
    #    self.om.changePoint(0.00007,0.0, 7)
    #    listToBeValidated = []
    #    listToBeValidated.append(Waypoint(0.0,0.0,0))
    #    listToBeValidated.append(Waypoint(0.0001,0.0001,0))
    #    listToBeValidated.append(Waypoint(0.0001,0.0,0))
    #    listToBeValidated.append(Waypoint(0.00005,-0.00005, 1))
    #    waypointList = self.con.validateWaylist(listToBeValidated,0)
    #    assert waypointList[1].getType() == 1
    #    assert waypointList[3].getType() == 1
    #    assert waypointList[5].getType() == 1
    
    #Test: ValidateWaylist with no obstacles present
    def testC6 (self):
        self.om.clearAll()
        listToBeValidated1 = []
        listToBeValidated1.append(Waypoint(0.000025, 0.000023, 0))
        listToBeValidated1.append(Waypoint(0.000055, 0.000053, 0))
        waypointList1 = self.con.validateWaylist(listToBeValidated1,0)
        assert waypointList1[0].longitude == 0.000023, self.prefix + "C6: Starting waypoint1 longitude changed when it shouldn't have been." 
        assert waypointList1[0].latitude == 0.000025, self.prefix + "C6: Starting waypoint1 latitude changed when it shouldn't have been." 
        assert waypointList1[1].longitude == 0.000053, self.prefix + "C6: Starting waypoint2 longitude changed when it shouldn't have been." 
        assert waypointList1[1].latitude == 0.000055, self.prefix + "C6: Starting waypoint2 latitude changed when it shouldn't have been." 
        
    #Test: ValidateWaylist with obstacle present on an endpoint
    def testC7(self):
        self.om.clearAll()
        self.om.changePoint(0.000055, 0.000053, 7)
        waypoint1 = self.con.validateWaypoint(Waypoint(0.000025, 0.000023, 0))
        waypoint2 = self.con.validateWaypoint(Waypoint(0.000055, 0.000053, 0))
        listToBeValidated2 = []
        listToBeValidated2.append(waypoint1)
        listToBeValidated2.append(waypoint2)
        waypointList2 = self.con.validateWaylist(listToBeValidated2,0)
        assert waypointList2[0].longitude == 0.000023, self.prefix + "C7: Starting waypoint1 longitude changed when it shouldn't have been." 
        assert waypointList2[0].latitude == 0.000025, self.prefix + "C7: Starting waypoint1 latitude changed when it shouldn't have been." 
        assert not waypointList2[1].longitude == 0.000053, self.prefix + "C7: Starting waypoint2 longitude wasn't changed when it should've have been." 
        assert not waypointList2[1].latitude == 0.000055, self.prefix + "C7: Starting waypoint2 latitude wasn't changed when it should've have been." 
                
    #Test: ValidateWaylist with obstacle present on path
    def testC8(self):
        self.om.clearAll()
        listToBeValidated3 = []
        listToBeValidated3.append(Waypoint(0.000025, 0.000023, 0))
        listToBeValidated3.append(Waypoint(0.000055, 0.000053, 0))
        self.om.changePoint(0.000045, 0.000043, 7)
        waypointList3 = self.con.validateWaylist(listToBeValidated3,0)
        assert waypointList3[0].longitude == 0.000023, self.prefix + "C8: Starting waypoint1 longitude changed when it shouldn't have been." 
        assert waypointList3[0].latitude == 0.000025, self.prefix + "C8: Starting waypoint1 latitude changed when it shouldn't have been."
        assert waypointList3[1].getType() == 1, self.prefix + "C8: Navigation waypoint not added when it should've been."
        
        #for waypoint in waypointList:
        #    print waypoint
if __name__ == "__main__":
     unittest.main()       

