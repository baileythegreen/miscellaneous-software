#!/usr/bin/python

import sys, math
import pandas as pd
import scipy.stats
from collections import namedtuple
import pprint


Landmark = namedtuple('Landmark', ['name', 'x', 'y', 'c', 'm'])
MissingLandmark = namedtuple('MissingLandmark', ['name', 'iid', 'point'])
PixelSize = namedtuple('PixelSize', ['x', 'y'])
TraitEndPoints = namedtuple('TraitEndPoints', ['start', 'end'])
traitDescriptions = { 
    'humerusRight'  :   TraitEndPoints('humerus_rp', 'humerus_rd'),    #a dictionary of all of the point
    'humerusLeft'   :   TraitEndPoints('humerus_lp', 'humerus_ld'),    #pairs that make up each distance
    'radiusRight'   :   TraitEndPoints('radius_rp', 'radius_rd'),
    'radiusLeft'    :   TraitEndPoints('radius_lp', 'radius_ld'),
    'ulnaRight'     :   TraitEndPoints('ulna_rp', 'ulna_rd'),
    'ulnaLeft'      :   TraitEndPoints('ulna_lp', 'ulna_ld'),
    'femurRight'    :   TraitEndPoints('femur_rp', 'femur_rd'),
    'femurLeft'     :   TraitEndPoints('femur_lp', 'femur_ld'),
    'tibiaRight'    :   TraitEndPoints('tibia_rp', 'tibia_rd'),
    'tibiaLeft'     :   TraitEndPoints('tibia_lp', 'tibia_ld'),
    'fibulaRight'   :   TraitEndPoints('fibula_rp', 'fibula_rd'),
    'fibulaLeft'    :   TraitEndPoints('fibula_lp', 'fibula_ld'),
    'shoulders'     :   TraitEndPoints('humerus_rp', 'humerus_lp'),
    'acetabular'    :   TraitEndPoints('femur_rp', 'femur_lp'),
    'torsoRight'    :   TraitEndPoints('humerus_rp', 'femur_rp'),
    'torsoLeft'     :   TraitEndPoints('humerus_lp', 'femur_lp') }

dexas = {}
missing = set()

#####################################################################

class Dexa(object):
    r = len(dexas)    
    def __init__(self, iid, pixel, landmarks):
        self.iid = iid 
        self.pixel = pixel
        self.landmarks = landmarks
        self.traitValues = {}
        print "Dexa object created."
        Dexa.r += 1
   #maybe redo the Dexa.r thing
   # def createTraitObject(type, name, *value):
   #    name = type(name)
   # def __repr__(self):
   #     return self.iid #("Pixel size: "
     #   + str(pprint.pprint(self.pixel)) + "\n")
       # + "Landmarks: "
       # + str(pprint.pprint(self.landmarks.values()))
       # )

    def getTraitValues(self):
        global traitDescriptions
        for trait, endpoints in traitDescriptions.items():
            name = trait
            # names in landmarks are still 'tibia_rd', this code wants 'tibiaRight'
            coordinates = self.getLandmarkValues(traitDescriptions[name])
            if None in coordinates:
                continue
            if name.endswith('Right'):
                name = sidedTrait(trait, 'right', self.pixel, coordinates)
            elif name.endswith('Left'):
                name = sidedTrait(trait, 'left', self.pixel, coordinates)
            else:
                name = horizontalTrait(trait, self.pixel, coordinates)
        #calculate trait values, somehow 
            self.traitValues[trait] = name.length
        return self.traitValues

    def getLandmarkValues(self, trait):
        start = end = None
        try:
            start = self.landmarks[trait.start]
        except KeyError: #caused by a missing point
            print "%s is missing %s" % (self, trait.start)
        try:
            end = self.landmarks[trait.end]
        except KeyError:
            print "%s is missing %s" % (self, trait.end)
        return (start, end)
#####################################################################

class Trait(object):
    def __init__(self, name, pixel, coordinates):
        #Trait is passed a TraitDescription tuple
        #print coordinates
        #print type(coordinates)
        #if type(coordinates) is not TraitEndPoints:
        #    raise TypeError('description is not a TraitEndPoints. The Trait class must be passed a TraitEndPoints object.')
        self.name = name
        self.X, self.Y = pixel
        self.start, self.end = coordinates
        if type(self.start) is not Landmark:
            raise TypeError('start is not a Landmark. A TraitEndPoints tuple must be made up of two Landmark tuples.')
        if type(self.end) is not Landmark:
            raise TypeError('end is not a Landmark. A TraitEndPoints tuple must be made up of two Landmark tuples.')
        self.alpha = self.start
        self.beta = self.end

    @property
    def deltaX(self):
        x1 = self.alpha.x
        x2 = self.beta.x
        deltaX = float(x1) - float(x2)
        deltaX = deltaX * self.X
        return deltaX
        

    @property
    def deltaY(self):
        y1 = self.alpha.y
        y2 = self.beta.y
        deltaY = float(y1) - float(y2)
        deltaY = deltaY * self.Y
        return deltaY

    @property
    def length(self):
        deltaX = self.deltaX
        deltaY = self.deltaY
        l = math.sqrt(deltaX**2 + deltaY**2)
        return l

#####################################################################
#giving traits specific names if I do this might be difficult; not sure this class adds much
class sidedTrait(Trait):
    def __init__(self, trait, side, pixel, description):
        super(sidedTrait, self).__init__(trait, pixel, description)
        self.side = side


#####################################################################

class horizontalTrait(Trait):
    def __init__(self, trait, pixel, description):
        super(horizontalTrait, self).__init__(trait, pixel, description)

    @property
    def slope(self):
        deltaX = super(horizontalTrait, self).deltaX
        deltaY = super(horizontalTrait, self).deltaY
        slope = deltaY/deltaX
        return slope

#####################################################################


#def newTraitDescription(name, start, end):

def readScan():
    row = None
    while True:
        entry = (yield row)
        #print "line 44"
        #print type(entry)
        print entry
        iid = str(getIid(entry))
        pixel = getPixelSize(entry) #should this be an attribute of a class object?
        # or you could initialise the object without the attributes, then go get them. lets you create the dict first
        #process entry
        landmarks = getLandmarks(entry)
        dexas[str(iid)] = Dexa(iid, pixel, landmarks)
        #Dexa(pixel, landmarks)
        print "Dexas: %d" % len(dexas.keys())
        print "line 153"
        #print dexas[str(iid)]

def getIid(entry):
    #print "Get id started."
    #r = len(dexas)
    iid = entry.ix[Dexa.r,('assay')]  #--> returns an integer
    #print type(iid)
    #iid = entry['assay']  --> returns a series
    print "Id: " + str(iid)
    return iid

def getPixelSize(entry):
    print "Get pixel started."
    x_mm = entry.ix[Dexa.r,('pixelsz_x')]
    y_mm = entry.ix[Dexa.r,('pixelsz_y')]
    pixel = PixelSize(x_mm, y_mm)
    print "Get pixel complete."
    return pixel


def getLandmarks(entry):
    print "Get landmarks started."
    landmarks = {}
    points = (4*c + 3 for c in xrange(24))
    for i in points:
        name = entry.columns[i].rsplit('_', 1)[0]
        #print "Name: %s" % name + '\t',
        x = entry.ix[Dexa.r,i]
        #print "X: %d" % x + '\t',
        y = entry.ix[Dexa.r,i+1]
        #print "Y: %d" % y + '\t',
        c = entry.ix[Dexa.r,i+2]
        #print "C: %f" % c + '\t',
        m = entry.ix[Dexa.r,i+3]
        #print "M: %s" % m
        if m != 0:
            point = Landmark(name, x, y, c, m)
            landmarks[name] = point
        else:
            iid = getIid(entry)
            point = MissingLandmark(iid, iid, name) #these argument names foster confusion
            missing.add(point)
    print "No. of landmarks %d" % len(landmarks)
    print "Get landmarks complete."
    return landmarks

#need a distances{}
def getDistances():
    distances = {}
    for key, value in traitDescriptions.items():
        name = key
        key = Trait(name, value)
        distances[name] = key.length #get the hypotenuse
    return distances


if __name__ == '__main__':
    #global dexas
    print "Main started."
    if len(sys.argv) != 3:
        sys.stderr.write("Usage: python %s inputfile outputfile\n" % sys.argv[0])
        raise SystemExit(1)
    inputfile = sys.argv[1]
    outputfile = sys.argv[2]
    print inputfile
    #outputfile = sys.argv[2]
    subsetter = pd.read_csv(inputfile, header = 'infer', iterator = True)
    #print dir(subsetter)
    parser = readScan()
    parser.next()
    #print parser
    z = 0
    while True:
        try:
            parser.send(subsetter.get_chunk(1))#for dexa in dexas:
            #print "line 103: %s" % z
            z += 1
        except StopIteration:
            break
            #print dexas.keys()
    distances = {}
    phenotypes = pd.DataFrame()
    print "Phenotypes: "
    print phenotypes.shape
    for dexa in dexas:
        print "line 226"
        distances[str(dexa)] = dexas[dexa].getTraitValues()
        print len(distances.keys())
    phenotypes = pd.DataFrame.from_dict(distances).transpose()  #, orient = "index")
    print phenotypes.shape
    phenotypes.to_csv(outputfile, sep = "\t")
    print "Line 105: " + str(dexas.items())
    print "Main finished."
    


# Example .json output
'''
{
  "points": {
    "humerus_rp":  [83.5000,    172.0000],
    "humerus_rd":  [67.0000,    332.5000],
    "humerus_lp":  [241.0000,   163.0000],
    "humerus_ld":  [273.3333,   318.0000],
    "radius_rp":  [58.0000,     333.3333],
    "radius_rd":  [35.3333,     452.0000],
    "radius_lp":  [280.0000,    319.3333],
    "radius_ld":  [296.0000,    438.3333],
    "ulna_rp":  [70.6667,       324.3333],
    "ulna_rd":  [25.6667,       446.6667],
    "ulna_lp":  [269.3333,      309.3333],
    "ulna_ld":  [303.6667,      434.0000],
    "femur_rp":  [100.0000,     428.3333],
    "femur_rd":  [117.3333,     647.6666],
    "femur_lp":  [233.6667,     429.6667],
    "femur_ld":  [207.0000,     647.3334],
    "tibia_rp":  [117.0000,     649.3334],
    "tibia_rd":  [106.6667,     842.6667],
    "tibia_lp":  [207.3333,     650.3334],
    "tibia_ld":  [207.3333,     842.0000],
    "fibula_rp":  [99.3333,     658.6666],
    "fibula_rd":  [94.6667,     847.6667],
    "fibula_lp":  [224.0000,    661.6666],
    "fibula_ld":  [218.6667,    848.6667],
  }
}
'''
