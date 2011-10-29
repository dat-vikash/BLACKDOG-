#Embry-Riddle Aeronautical University
#SE/CS/CE Senior Project 2007-08
#Control Team
#Cory Carson

from threading import Thread
#This is a decorator to spawn a new thread for a function.
#usage:
#>>> @async
#def test(a,b):
#    sleep(10)
#    print a,b
#
#    
#>>> test(4,65)
#<Thread(test, started)>
#>>> 4 65
def async(function):
    def wrapped_function(*args, **kwds):
        thread = Thread(None,
                        function,
                        function.__name__,
                        args,
                        kwds)
        thread.setDaemon(True)
        thread.start()
        return thread
    return wrapped_function



from math import pi, sqrt, atan

#Returns the distance between two waypoints in degrees.
def distance(fromWaypoint, toWaypoint): return sqrt(
        (fromWaypoint.getLongitude() - toWaypoint.getLongitude())**2+
        (fromWaypoint.getLatitude() - toWaypoint.getLatitude())**2)


def direction(fromWaypoint, toWaypoint):
    """direction(Waypoint fromWaypoint, Waypoint toWaypoint)
    Returns the direction in radians"""
    direction = 0
    if toWaypoint.getLongitude() == fromWaypoint.getLongitude():
        if toWaypoint.getLatitude() - fromWaypoint.getLatitude() < 0:
            direction = 1.5 * pi
        else:
            direction = 0.5 * pi 
    else:
        direction = atan(
            (toWaypoint.getLatitude() - fromWaypoint.getLatitude()) /
            (toWaypoint.getLongitude() - fromWaypoint.getLongitude())
            )
        if toWaypoint.getLongitude() - fromWaypoint.getLongitude() < 0:
            direction += pi
    return direction