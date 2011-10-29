import unittest
from ObjectGen import ObjectGen
from Communications import Communications
from Waypoint import Waypoint

class VGOTestBase(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def runTest(self):
        pass
        
class SimpleWaypointTest(VGOTestBase):
       
       def test__waypointTest(self):
           self.object = ObjectGen()
           self.comm = Communications(self.object, mode="TEST")
           
           self.testWaypoint = Waypoint([29,11,23.29],[-81,2,51.72],"nav")
           self.object.addWaypoint(self.testWaypoint)
           print "CurWaypoint: " + str(self.object.getWaypoint())
           self.failUnlessEqual(self.testWaypoint, self.object.getWaypoint(), "YOU LOSE!")

#testcase = unittest.FunctionTestCase()
           
           


           
        
        
   # def tearDown(self):
 