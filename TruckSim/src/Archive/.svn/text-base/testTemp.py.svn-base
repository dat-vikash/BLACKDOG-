# -*- coding: cp1252 -*-
import time
import random



def main():
    
    tempVar=0.5            #in percent
    maxTemp=34.0
    avgTemp=0.7*maxTemp
    minTemp=0.5*maxTemp
    temp = avgTemp        #temp is in celsius

    tempPosNeg=0;

    while True:

        tempPosNeg=random.randrange(0,2)
        if tempPosNeg==0:
            tempPosNeg=-1
        temp=temp+(random.random()*tempVar)*tempPosNeg
        if temp>maxTemp:
            temp=maxTemp
        if temp<minTemp:
            temp=minTemp
        time.sleep(1)
        print temp


if __name__ == '__main__':
    main()
