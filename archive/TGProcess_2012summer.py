####################################################################################

#   TGProcess.py 
#   - Created by Jason P.R. and modified by Minshu Zhan
#   - May 2012 (Minshu):
#       * Added get_tier() and fill_tier() functions in TextGrid class.
#       * Added PointTier and IntervalTier classes, both of which inherit Tier
#       and modified relevant parsing code in TextGrid.readGrid()
#       * Added find() functions in PointTier and IntervalTier to allow finding 
#       items by time.
#       * Added truncate() function in TextGrid class to allowing for selecting
#       a sub-region of the textgrid for testing purposes
#   - 2012 July (Minshu):
#       * Changed time representation from string to float; added time resolution DELTA
#       * Added the following query functions: IntervalTier.findBetween(),
#       IntervalTier.findBetweenAsIndices(), PointTier.findAsIndices(),
#       PointTier.findLastAsIndex(),  

###############################################################################

import re
import operator
import csv

"""Conventions:
This script zero-indexes everything. So, the first point/interval in the first tier is
referenced as textGrid[0][0].

Also, Praat strangely decided to call tiers "items."  I ignore this convention, and
instead use "item" as the general term for a Point or an Interval.  I have not (yet)
found a need to superclass Point and Interval, but if I did, I'd have it be Item, and
define Point(Item) and Interval(Item)
"""

# Time resolution
DELTA = 0.000001

def stripQuotes(s):
    """Removes outer quotes, and whitespace outside those quotes, from a mark/text."""
    """ stripQuotes(" \"This is the intended use\"  ") yields "This is the intended use"  """
    """ stripQuotes(" \"This is the \"intended\" use  ") yields "This is the \"intended\" use" """
    return s[::-1].strip().replace('"',"",1)[::-1].replace('"',"",1)

class TextGrid:
    """Top-level object for storing and manipulating TextGrids."""
    def __str__(self):
        return "TextGrid with " + str(len(self)) + " tiers: " + ", ".join(["\"" + tier.name + "\"" for tier in self.tiers])
    __repr__ = __str__
    def __len__(self):
        return len(self.tiers)
    def __getitem__(self,i): #allows textGrid[i] where textGrid = TextGrid()
        return self.tiers[i]
    def __setitem__(self,i,item):
        self.tiers[i]=item
    def __delitem__(self,i):
        del(self.tiers[i])
    def append(self,item):
        self.tiers.append(item)
    def __init__(self,fileType="ooTextFile", objectClass="TextGrid", xmin=0, xmax=0, hasTiers="exists", filepath=None ):
        """Creates an empty TextGrid with to specified metadata, or reads a grid from the filepath into a new TextGrid instance."""
        if filepath != None:
            self.tiers = []
            self.readGridFromPath(filepath)
        else:
            self.tiers = []
            self.fileType = fileType
            self.objectClass = objectClass
            self.xmin = xmin
            self.xmax = xmax
            self.hasTiers = hasTiers
            self.enc = None #Encoding must be set when grid is read.
                            #We don't define self.size.  We simply use len(self.tiers)
        
    def writeGridToPath(self, path):
        """Writes the TextGrid in the standard TextGrid format to the file path."""
        f = open(path,'w',encoding=self.enc)
        self.writeGrid(f)
        
    def writeGrid(self,f):
        f.write("File type = \"" + self.fileType + "\"\n")
        f.write("Object class = \"" + self.objectClass + "\"\n")
        f.write("\n")
        f.write("xmin = " + str(self.xmin) + "\n")
        f.write("xmax = " + str(self.xmax) + "\n")
        f.write("tiers? <" + self.hasTiers + "> \n")
        f.write("size = " + str(len(self.tiers)) + " \n")
        f.write("item []: \n")
        for tierNum in range(0,len(self.tiers)):
            f.write("    item [" + str(tierNum+1) + "]:\n")
            self.tiers[tierNum].writeTier(f)

    def readGridFromPath(self, filepath):
        """Parses a .TextGrid file and represents it internally in this TextTier() instance."""
        try:
            self.readGrid(open(filepath,'r',encoding='utf-8'))
        except UnicodeDecodeError:
            self.readGrid(open(filepath,'r',encoding='utf-16'))
 
    def readGrid(self,f):
        """Parses the .TextGrid file described by the file descriptor and represents it internally in this TextTier() instance.  It is recommended to use readGridFromPath() unless you have a good reason not to."""

        #f.seek(0) #Should we do this?  Probably not.

        self.enc = f.encoding

        #Regexes for parsing info from TextGrid
        fileTypeRE = re.compile(r"File type = \"(.+)\"")
        objectClassRE = re.compile(r"Object class = \"(.+)\"")
        xminRE = re.compile(r"xmin = (.+)")
        xmaxRE = re.compile(r"xmax = (.+)")
        tiersRE = re.compile(r"tiers\? <(.+)>")
        sizeRE = re.compile(r"size = (.+)")
        
        tierRE = re.compile(r"item \[(.+)\]:") # beginning of new tier!
        classRE = re.compile("class = \"(.+)\"")
        nameRE = re.compile(r"name = \"(.+)\"")

        pointRE = re.compile(r"points \[(.+)\]:")
        intervalRE = re.compile(r"intervals \[(.+)\]:")

        timeRE = re.compile(r"(?:number|time) = (.+)") 
        markRE = re.compile(r"mark = (.+)")
        textRE = re.compile(r"text = (.+)")

        inMeta = True #reading the Grid metadata section, not the data tiers.
        
        while True:
            line = f.readline()
            if not line:
                break
            
            if inMeta:
                match = fileTypeRE.search(line)
                if match:
                    self.fileType = match.groups()[0]
                    continue

                match = objectClassRE.search(line)
                if match:
                    self.objectClass = match.groups()[0]
                    continue

                match = xminRE.search(line)
                if match:
                    self.xmin = float(match.groups()[0])
                    time = self.xmin
                    continue

                match = xmaxRE.search(line)
                if match:
                    self.xmax = float(match.groups()[0])
                    continue

                match = tiersRE.search(line)
                if match:
                    self.hasTiers = match.groups()[0]
                    continue

                #Currently, we dierctly tabulate "size" from the data.
                """match = sizeRE.search(line)
                if match:
                    self.size = match.groups()[0]
                    continue"""

                match = tierRE.search(line)
                if match:
                    inMeta = False
                    #"Don't interpret future lines as grid metadata..."
                    inTierMeta = True
                    #"...they are tier metadata (or point/interval data)"
                    continue
                
            elif inTierMeta:
                match = classRE.search(line)
                if match:
                    tClass = match.groups()[0]
                    continue

                match = nameRE.search(line)
                if match:
                    tname = match.groups()[0]
                    continue

                match = xminRE.search(line)
                if match:
                    tmin = float(match.groups()[0])
                    time = tmin
                    continue

                match = xmaxRE.search(line)
                if match:
                    tmax = float(match.groups()[0])
                    continue

                
                # Done parsing tier metadata; start parsing items
                inTierMeta = False
                if tClass == 'IntervalTier':
                    self.append(IntervalTier(tname, tmin, tmax))
                elif tClass == 'TextTier':
                    self.append(PointTier(tname, tmin, tmax))
                else:
                    raise Exception("Unrecognized tier class: ", tClass)
                    
                matchP = pointRE.search(line)
                matchI = intervalRE.search(line)
                if matchP:
                    self[-1].append(Point(time,'')) 
                    inTierMeta = False #Done reading this tier's metadata.  Next lines are data.
                    continue
                elif matchI:
                    self[-1].append(Interval(time, time, ''))
                    inTierMeta = False #Done reading this tier's metadata.  Next lines are data.
                    continue                    

                
            else: # not in any type of metadata
                  #TODO: factor out test for interval vs point?                    
                match = timeRE.search(line)
                if match:
                    self[-1][-1].time = float(match.groups()[0])
                    time = self[-1][-1].time
                    continue

                match = xminRE.search(line)
                if match:
                    self[-1][-1].xmin = float(match.groups()[0])
                    time = self[-1][-1].xmin
                    continue

                match = xmaxRE.search(line)
                if match:
                    self[-1][-1].xmax = float(match.groups()[0])
                    time = self[-1][-1].xmax
                    continue
                
                match = markRE.search(line)
                if match:
                    mark = match.groups()[0]
                    while mark.count('"')%2==1: #Praat escapes quotes by doubling: '"' -> '""'
                        #If the quotes don't add up to an even number (1 opening +  1 closing + 2*escaped quote count), \
                        #the mark must be multi-lined.
                        line = f.readline() 
                        if line:
                            mark += line
                        else:
                            raise Exception("TextGrid file ends mid-mark!")
                    if self[-1].tierClass == "TextTier":
                        self[-1][-1].mark = stripQuotes(mark)
                    else:
                        raise Exception("Found a \"mark\" in a non-TextTier.")            
                    continue

                match = textRE.search(line)
                if match:
                    text = match.groups()[0]
                    while text.count('"')%2==1:
                        line = f.readline()
                        if line:
                            text += line
                        else:
                           raise Exception("TextGrid file ends mid-text!")
                    if self[-1].tierClass == "IntervalTier":
                        self[-1][-1].text = stripQuotes(text)
                    else:
                        raise Exception("Found a \"text\" in a non-IntervalTier!")
                    continue

                #new point or interval               
                matchP = pointRE.search(line)
                matchI = intervalRE.search(line)
                if matchP:
                    self[-1].append(Point(time, '')) 
                elif matchI:
##                    print(type(Interval()))
                    self[-1].append(Interval(time, time,''))

                match = tierRE.search(line)
                if match:
                    inTierMeta = True #We just started a tier, we need to read the metadata.
                    continue

    def listTiers(self):
        for i in range(0,len(self)):
            print(str(i+1) + ": " + str(self[i]))

    def get_tier(self, n):
        t = None
        for tier in self.tiers:     # tier names are case-insensitive
            if tier.name.strip().lower() == n.lower():
                t = tier
        if t == None:
            raise Exception("Tier named \"", n,"\" not found.")
        print('Found', t)
        return t

    # Fill in the gaps in an interval layer with empty text
    def fill_tier(self, t):
        """ Fill the gaps in an interval tier with empty intervals. """
##        This function is created to correct manually created interval
##        tiers which consist of interval that do not span the text grid's
##        entire time range.

        if t.tierClass != 'IntervalTier':
            print("Tier", t.name, "is not an Interval Tier.")
            return
        
        gapEnd = 0
        i = 0
        while i<len(t.items):
            interval = t.items[i]
            if abs(interval.xmin-gapEnd)>DELTA:
                t.items.insert(i, Interval(gapEnd, interval.xmin, ""))
                print("inserted at ", i, " ", gapEnd, "-", interval.xmin)
                i+=1
            gapEnd = interval.xmax
            i+=1
        if abs(interval.xmax- t.xmax)>DELTA:
            t.append(Interval(interval.xmax, t.xmax, ""))
            print("inserted at ", i, " ", interval.xmax, "-", t.xmax)
            
        
            
    def sample(self, end, start = 0):
        """ Sample a sub-region of the entire textgrid bounded by end and start. Return a textgrid object."""
        new = TextGrid()
        tmin = self.xmax
        tmax = 0
        
        for t in self:
            if t.tierClass == 'IntervalTier':
                tnew = IntervalTier(t.name, t.xmin, t.xmax)
                s = t.find(start)
                e = t.find(end)
                if s.xmin < tmin:
                    tmin = s.xmin
                if e.xmax > tmax:
                    tmax = e.xmax
                tnew.items = t[t.items.index(s):t.items.index(e)+1]
            elif t.tierClass == 'TextTier':
                points = t.find(start, end)
                tnew = PointTier(t.name, t.xmin, t.xmax)
                tnew.items = points
            else:
                raise Exception("Unknown tier class", t.tierClass)
            new.append(tnew)
            
        for t in new:
            t.xmin = tmin
            t.xmax = tmax
            if t.tierClass == 'IntervalTier':
                new.fill_tier(t)
        new.xmin = tmin
        new.xmax = tmax
        return new

    def split(self, target, reference, delimiter='#'):
        """
        Split target tier according to the delimiters found in the
        reference tier. 
        This function is created to split LM tier around silences, which
        are indicated in the phoneme tier.
        target: name of a PointTier
        reference: name of IntervalTier
        delimiter: a string
        extension: a float 
        Return a list of IntervalTier instances 
        """
        sections = []
        smin = 0
        smax = 0
        target_tier=self.get_tier(target)
        ref_tier = self.get_tier(reference)
        print(target_tier)
        print(ref_tier)
        
        for p in ref_tier:            
##            print(p.text)
            if p.text==delimiter:
                smax = (p.xmax+p.xmin)/2     # extended to midpoint of boundary silence interval                
                if smax>smin:
                    # Create a new tier which is bounded by smin and smax; the higher and
                    # lower bound are both extended to include points near the boundaries
                    # of delimiter intervals                    
                    section = target_tier.find(smin, smax)
                    t = PointTier(target+'_'+str(len(sections)), smin, smax)
                    t.items = section
                    sections+=[t]
                smin = smax
            else:
                smax = p.xmax
        if smax>smin:            
            section = self.get_tier(target).find(smin, smax)
            t = PointTier(target+'_'+str(len(sections)), smin, smax)
            t.items = section
            sections+= [t]

        return sections
                
        
                
            
        
# Uncommented the following to fill in the gaps in the phoneme tier
##fname = "Conv7_amh_5-1" # CHANGE THIS TO THE FILE THAT YOU ARE WORKING
##tg =TextGrid()
##tg.readGridFromPath(fname+".textgrid")  
##tg.fill_tier("phoneme")
##tg.writeGridToPath(fname+"_fixec.textgrid")



# TO-DO: Seperate PointTier and IntervalTier subclasses and enable class invariant checking
class Tier:
    """Object for storing and manipulating Tiers.
    Intended to be stored in a TextGrid() instance."""
    def __init__(self, tClass, name, xmin, xmax):
        self.tierClass = tClass
        self.name = name
        self.xmin = xmin
        self.xmax = xmax
        self.items = []
    def __str__(self):
        return " \"" + self.name + "\" " + self.tierClass + " with " + str(len(self.items)) + " items."
    __repr__ = __str__
    def __len__(self):
        return len(self.items)
    def __getitem__(self,i):
        return self.items[i]
    def __setitem__(self,i,item):
        self.items[i]=item
    def __delitem__(self,i):
        self.removeItem(i) #See below
    def append(self,item):
        self.items.append(item)
    def sort(self, *args, **kwords):
        self.items.sort(*args,**kwords)
    def writeTier(self,f):
        """Writes the contents of the Tier to the file f in TextGrid format.
        Intended to be called as part of TextGrid().writeGrid(), as to contribute to a valid TextGrid file."""
        f.write("        class = \"" + self.tierClass + "\" \n")
        f.write("        name = \"" + self.name + "\" \n")
        f.write("        xmin = " + str(self.xmin) + "\n")
        f.write("        xmax = " + str(self.xmax) + "\n")
        if self.tierClass == "IntervalTier":
            f.write("        intervals: size = " + str(len(self.items)) + " \n")
            for itemNum in range(0,len(self.items)):
                f.write("        intervals [" + str(itemNum+1) + "]:\n")
                self.items[itemNum].writeInterval(f)
        elif self.tierClass == "TextTier":
            f.write("        points: size = " + str(len(self.items)) + " \n")
            for itemNum in range(0,len(self.items)):
                f.write("        points [" + str(itemNum + 1) + "]:\n")
                self.items[itemNum].writePoint(f)        
    
           
    def remove(self, item):
        self.items.remove(item)
        
    def removeItem(self,itemIndex):
        del(self.items[itemIndex])

    def writeTierToPathAsCSV(self,filepath):
        """Writes the contents of a tier to a path as a CSV (Excel-readable) file."""
        tierWriter = csv.writer(open(filepath,'w',newline=''))
        if self.tierClass == "TextTier":
            tierWriter.writerow(['time','mark'])
            for point in self:
                tierWriter.writerow([point.time,point.mark])
        elif self.tierClass == "IntervalTier":
            tierWriter.writerow(['xmin','xmax','text'])
            for interval in self:
                tierWriter.writerow([interval.xmin,interval.xmax,interval.text])


class PointTier(Tier):
    """
    Class Invariants:
        - All items are Point instances
    """
    def __init__(self, name, xmin, xmax):
        Tier.__init__(self, "TextTier", name, xmin, xmax)
        
    def insert(self, point): #TODO: Use log(n) algorithm to find correct placement
        if not isinstance(point, Point):
            raise Exception( "Not a Point instance: ", point)
        if point.time<self.xmin or point.time>self.xmax:
            raise Exception("Point", point, "exceeded tier boundary [", self.xmin, ',',self.xmax)
        
        if self.items == [] or self.items[-1].time<point.time:
            self.items.append(point)
            return

        pos = self.findLastAsIndex(point.time)

        if self.items[pos+1].time==point.time:
            
            ## lols this does happen!
            print("WARNING: inserted point ",point,"overlaps with existing point", self.items[pos+1])
            
        self.items.insert(pos+1, point)


    def find(self, start, end, offset=0):
        """ Returns the Point instances located between given start time and end time """
        i = offset
        pt = self.items[i]
        pts = []
        while pt.time<start:
            i+=1
            pt = self.items[i]
        while pt.time<end:
            pts += [pt]
            i+=1
            if i>=len(self.items):
                break
            pt = self.items[i]
        return pts
    
    def findAsIndices(self, start, end, offset=0):
        """ Returns indices of the Point instances located between given start time and end time """
        i = offset
        pt = self.items[i]
        pts = []
        indices = []
        while pt.time<start:
            i+=1
            pt = self.items[i]
        while pt.time<end:
            indices.append(i)
            pts += [pt]
            i+=1
            if i>=len(self.items):
                break
            pt = self.items[i]
        return indices
    
    def findLastAsIndex(self, endtime, offset=0):
        """ Returns the last point preceding the given time """
        i = offset
        while self.items[i].time<endtime:
            i+=1
        return i-1

    def locate(self, mark, offset=0):
        """
        Return the first point with the given mark, searching starting from offset.
        """
        raise Exception("Not implemented.")


    def remove(self, point):
        """ Remove a Point instance from the point tier."""
        self.items.remove(point)
    
    def removeByIndex(self, pointIndex):
        """ Remove a Point from the point tier by its index."""
        self.removeItem(pointIndex)

    

class IntervalTier(Tier):
    """
    Class Invariants:
        - Intervals must cover entire time range
        - All items must be Interval Instances
    """
    def __init__(self, name, xmin, xmax):
        Tier.__init__(self, "IntervalTier", name, xmin, xmax)

    ## WARNING: THIS FUNCTION MAY BREAK CLASS INVARIANT ##
    # TO-DO:  does this function even make sense??
    def insert(self, interval):        
        """Insert an interval to the Tier."""
        if not isinstance(interval, Interval):
            raise Exception("Not an Interval instance: ", interval)
            return
        if interval.xmax>self.xmax+DELTA or interval.xmin<self.xmin-DELTA:
            raise Exception("Interval", interval, "exceeded tier boundary.")
                            
        #TODO: Use logn(n) algorithm to find correct placement 
##        left = self.xmin
##        right = self.xmax
##        while left<right:
##            middle = (right+left)/2
##            dif= interval.xmin-middle
##            if dif<0:
##                right = middle
##            elif dif<DELTA:
##                
                            
        addLoc = 0
        while self[addLoc].xmin<interval.xmin:
            addLoc+=1
            if addLoc == len(self.items):
                self.items.append(interval)
                return
            
    def append(self, interval):
        """ Append an interval to the end of the interval tier directly. """
        """Insert an interval to the Tier."""
        if not isinstance(interval, Interval):
            raise Exception("Not an Interval instance: ", interval)
            return
        if interval.xmax>self.xmax+DELTA or interval.xmin<self.xmin-DELTA:
            raise Exception("Interval", interval, "exceeded tier boundary.")
        
        if self.items!=[] and interval.xmin < self.items[-1].xmax-DELTA:
            raise Exception("Interval", interval, "overlaps with existing interval", self.items[-1])                            
        self.items.append(interval)
        
    def find(self, time, offset=0):
        """ Find the interval that covers a given time """
        i = offset
        intl = self.items[i]
        while time-intl.xmax>DELTA:
            i+=1
            if i>=len(self.items):
                break
            intl = self.items[i]
        return intl
    
    def findAsIndex(self, time, offset=0):
        """ Find the index of the interval that covers a given time """
        i = offset
##        print(len(self.items))
        intl = self.items[i]
        while time-intl.xmax>DELTA:
            i+=1
            if i>=len(self.items):
                break
            intl = self.items[i]
        return i

    def findBetween(self, start, end, offset=0):
        """ Find the intervals bounded by given start and end times. """
        i = offset
        intl = self.items[i]
        out = []
        while time-intl.xmax>DELTA:
            out.append(intl)
            i+=1
            if i>=len(self.items):
                break
            intl = self.items[i]
        return out        

    def findBetweenAsIndices(self, start, end, offset=0):
        """ Find indices of the intervals bounded by given start and end times. """
        i = offset
        intl = self.items[i]
        out = []
        while time-intl.xmax>DELTA:
            out.append(i)
            i+=1
            if i>=len(self.items):
                break
            intl = self.items[i]
        return out

    def remove(self, interval):
        """ Remove an Interval instance from the interval tier."""
        self.items.remove(interval)
        
    def removeByIndex(self,intervalIndex):
        """ Remove an Interval from the interval tier by its index."""
        self.removeItem(intervalIndex)
        
            
    
class Interval:
    def __init__(self, xmin, xmax, text):     
        self.xmin = xmin
        self.xmax = xmax
        self.text = text
    def __str__(self):
        return "(" + str(self.xmin) + "," + str(self.xmax )+") " + self.text
    __repr__ = __str__

    def __eq__(self, other):
        if other==None:
            return False        
        return abs(self.xmin-other.xmin)<DELTA and abs(self.xmax-other.xmax)<DELTA and self.text==other.text
    def writeInterval(self, f):
        f.write("            xmin = " + str(self.xmin) + "\n")
        f.write("            xmax = " + str(self.xmax) + "\n")
        f.write("            text = \"" + self.text + "\" \n")
                    
        


class Point:
    def __init__(self, time, mark):
        self.time = time
        self.mark = mark
    def __str__(self):
        return str(self.time) + " " + self.mark
    __repr__ = __str__
    #This __lt__ function is definend only for sorting purposes.
    #If we wish to expand for __gt__, __eq__, etc, we'll need to devote some thought to it,
    #because we may only want to consider points "equal" if their times *and* marks are the same.
    def __lt__(self,other):
        try:
            return operator.lt(self.time, other.time)
        except:
            try:
                return operator.lt(self.time, other)
            except:
                raise TypeError("Unorderable types: Point() < " + type(other))
    def __eq__(self, other):
        if other==None:
            return False
        return abs(self.time-other.time)<DELTA and (self.mark==other.mark)
    

    def splitLM(self, delta, subdelta):
        """Separates the mark's string of slash-separated landmarks into a list of 
        adjacent single landmarks. Return a list of LMPoint instances  """

        split = self.mark.split(',')

        out = []

        t = self.time        
        for s in split:
            if '/' in s:
                subsplit = s.split('/')
                for ss in subsplit:
            ##                        print("SS", ss)
                    # splitted lms result from the same phoneme transitions, i.e. lm.phns
                    out.append(Point(t, ss.strip()))     
                    t += subdelta
            else:
            ##                    print("S", s)
                out.append(Point(t, s.strip(), ))
                t+= delta
        return out
    
    
    def convertLM(self):
        """
        Convert a single hand-labelled landmark into the standard format.
        Returns a new Point instance; the mark is unchanged if conversion failed.
        """
        lmAlt = {
            'Nc':['m-cl', 'n-cl', 'ng-cl'],
            'Nr':['m', 'n', 'ng'],
            'Fc':['f-cl', 'th-cl', 's-cl', 'sh-cl', 'v-cl', 'dh-cl', 'z-cl', 'zh-cl', 'ch1', 'jh1/dj1', 'j1', 'dh1'],
            'Fr':['f', 'th', 's', 'sh', 'v', 'dh', 'z', 'zh', 'ch2', 'jh2/dj2','j2'],
            'Tn' : ['s-cl', 'sh-cl', 'z-cl', 'zh-cl'],
            'Tf': ['s', 'sh', 'z', 'zh'],
            'Sc' : ['p-cl', 't-cl', 'k-cl', 'b-cl', 'd-cl', 'g-cl', 'ch-cl', 'jh/dj-cl', 'j-cl'],
            'Sr' : ['p', 't', 'k', 'b', 'd', 'g', 'ch1', 'jh1/dj1','j1'],
            'Gc' : ['w-cl', 'y-cl', 'r-cl', 'l-cl', 'h-cl'],
            'Gr' : ['w', 'y', 'r', 'l', 'h'],
            }

        lm = self.mark
        if 'x' in lm and '?' in lm:       # Forbid concurrent '-x' and '-?' for parsing purpose
            raise Exception("'-x' and '-?' occurred together: "+lm)
        suffix = ''
        if 'x' in lm:
            suffix = '-x' 
        elif '?' in lm:
            suffix='-?'    
        mark = lm.strip("?x-")
        if mark in ['V', '+g','-g','+n','-n']: return Point(self.time, mark+suffix)
        for key, values in lmAlt.items():
            if mark in values:
                return Point(self.time, key+suffix)
        print('WARNING: Cannot convert landmark', self)
        return Point(self.time, self.mark )


    
    def setMarkFromList(self,list):
        """Takes a list of landmarks, joins them with slashes, and sets the resulting string as the point's mark."""
        mark = "/".join(list)

    
    def writePoint(self,f):
        f.write("            number = " + str(self.time) + "\n")
        f.write("            mark = \"" + self.mark + "\" \n")
    





