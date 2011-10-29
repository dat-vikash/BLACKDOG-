# -*- coding: cp1252 -*-
import time
import random



def main():
    
    speedVar=0.1            #in percent
    maxSpeed=1.0
    avgSpeed=0.7*maxSpeed
    minSpeed=0.5*maxSpeed
    speed = avgSpeed        #speed is in degrees per second

    speedPosNeg=0;

    while True:

        speedPosNeg=random.randrange(0,2)
        if speedPosNeg==0:
            speedPosNeg=-1
        speed=speed+(random.random()*speedVar)*speedPosNeg
        if speed>maxSpeed:
            speed=maxSpeed
        if speed<minSpeed:
            speed=minSpeed
        time.sleep(1)
        print speed


if __name__ == '__main__':
    main()
