import pickle

class GPSImage:
    def __init__(self, imageName, latTL, lonTL, latBR, lonBR):
        self.imageName = imageName
        self.latTL = latTL
        self.longTL = longTL
        self.latBR = latBR
        self.longBR = longBR
    
    def getCorners(self):
        return [self.latTL, self.latBR, self.longTL, self.longBR]
        
class GPSImageUtil:
    def __init__(self):
        pass
    
    def write(self, file, gpsImage):
        p = pickle.Pickler(file)
        p.dump(gpsImage)
    
    def read(self, file, gpsImage):
        u = pickle.Unpickler(file)
        gpsImage = u.load(gpsImage)
        return gpsImage