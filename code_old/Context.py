from TGProcess import *



class LMPoint(Point):

    def __init__(self, time, mark, phn1, phn2): 
        Point.__init__(self, time, mark)
        # the phoneme pair which generates the LM and the LM (Phoneme instances)
        self.phns = (phn1, phn2)
        self.counterLM = None

    def split(self, delta, subdelta):
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
                    out.append(LMPoint(t, ss.strip(), self.phns[0], self.phns[1]))     
                    t += subdelta
            else:
            ##                    print("S", s)
                out.append(LMPoint(t, s.strip(), self.phns[0], self.phns[1]))
                t+= delta
        return out
    
    def writeContext(self):
##	""" Return the string representation of the landmark point's context information.        The following parameters are listed in order, seperated by tabs:
##	FROM_PHONEME  -pos  -accent TO_PHONEME  -pos  accent FROM_WORD   -pos    -dialogFrequency    TO_WORD     -pos  -dialogFrequency
##	FROM_SUBPHRASE   -pos    TO_SUBPHRASE    -pos    FROM_PHRASE     -pos    TO_PHRASE   -pos      DIADLOGUE_WORD_FREQ
##	"""            
        phn1 = self.phns[0]
        phn2 = self.phns[1]
        w1 = phn1.word
        w2 = phn2.word
        sph1 = w1.subphrase
        sph2 = w2.subphrase
         
        if phn2.text=='#':
            lst = [phn1.text, phn1.pos(),phn1.reverse_pos(),phn1.accent, '-', '-', '-','-', w1.text, w1.number, w1.dialogFreq, '-', '-', '-', sph1.text, sph1.ip, '-', '-']
        elif phn1.text=='#':
            lst = ['-', '-','-','-', phn2.text, phn2.pos(),phn2.reverse_pos(), phn2.accent,  '-', '-', '-', w2.text, w2.number, w2.dialogFreq, '-', '-' , sph2.text, sph2.ip]
        else:
            lst = [phn1.text, phn1.pos(), phn1.reverse_pos(), phn1.accent, phn2.text, phn2.pos(),phn2.reverse_pos(), phn2.accent, w1.text, w1.number, w1.dialogFreq, w2.text, w2.number, w2.dialogFreq, sph1.text, sph1.ip, sph2.text, sph2.ip]
        out = lst[0]
        for item in lst[1:]:
            out+='\t' +str(item)
        return out


class LMTier(PointTier):
    """ Class Invariant - All items must be LMPoint instances """
    def __init__(self, name, xmin, xmax):
        PointTier.__init__(self, name, xmin, xmax)
    
    def splitLMs(self, delta = 0.00001, subdelta = 0.000001):
        """ Split concurrent landmark labels into seperate labels ','-seperated lms are
        DELTA apart; '/'-seperated lms are SUBDELTA apart. Return a new PointTier instance. """
        print("Splitting concurrent landmarks...")

        ptier = LMTier('Splitted lm', self.xmin, self.xmax)
        lastTime = self.xmin
        for lm in self.items:
            if lm.time<lastTime:
                raise Exception("LM label out of order at time=", lastTime)
            
            if ','  in lm.mark or '/' in lm.mark:
                splitted = lm.split(delta, subdelta)
                for p in splitted:
                    ptier.insert(p)
            else:
                ptier.insert(lm)
                
            lastTime = ptier[-1].time
            
        return ptier

    def insert(self, lmpoint):
        if not isinstance(lmpoint, LMPoint):
            raise Exception("Not a LMPoint instance: ", lmpoint)
        PointTier.insert(self, lmpoint)

    def alignedTier(self):
        """ Return a LMTier with time adjustment on each point to
        line up with its counter landmark, if present; insert 'INS'
        mark where a counter lm is not found; deletion is implied
        by a missing point."""
        tier = LMTier('Aligned LM', self.xmin, self.xmax)
        for lm in self.items:
            if lm.counterLM == None:
                tier.insert(LMPoint(lm.time, 'INS:'+lm.mark, lm.phns[0], lm.phns[1]))
            else:
                tier.insert(LMPoint(lm.counterLM.time, lm.mark, lm.phns[0], lm.phns[1]))
        
        return tier
        
class Phoneme(Interval):
    def __init__(self, tmin, tmax, word, phn='#', manner='#', t='', n=0, sn=0):
        """ Default values corresponds to a silence interval. """
        Interval.__init__(self, tmin, tmax, phn)
        
        # manner class of the phoneme (string)
        self.manner = manner
        
        # Lexical stress (int)
        try:
            self.stress = phn[-1]
        except:
            self.stress = -1
            
        # Syllabic position of phoneme 
        # Type (string)
        self.type = t
        # Number (int)
        self.number = n
        # Subnumber (int)
        self.subnumber = sn
    
            
        # Pitch accent (boolean)    
        self.accent = False     # default
        
        # word associated to the phoneme (Word instance)
        self.word = word

        # TO-DO: distinctive feature

    def pos(self):
        """ Return the string representation of the syllabic position of the phoneme.
        Return '-' if self is a silence. """
        if self.text=='#':
               return '-'
        return self.type+str(self.number)+str(self.subnumber)

    def is_end(self):
        return self.type == 'c' or (self.type=='n' and self.number == self.word.syllableCount)
    
    def reverse_pos(self):
        """ Return the distance of from the phoneme, if a nucleus, to the end of the word. """
        if self.type == 'n':
            rn = -(self.word.syllableCount-self.number+1)
        elif self.type == 'a':
            rn = -(self.word.syllableCount-self.number)
        else:
            rn = self.number
        return self.type+str(rn)+str(self.subnumber)
    
    def writeInterval(self, f):
        if self.text!='#':
            f.write("            xmin = " + str(self.xmin) + "\n")
            f.write("            xmax = " + str(self.xmax) + "\n")            
            text = self.type+str(self.number)+str(self.subnumber)+':'+self.text+' ('+self.manner+')'
            f.write("            text = \"" + text + "\" \n")
        else:
            Interval.writeInterval(self, f)

##        
##class SyllableConstituent(Interval):
##    def __init__(self, tmin, tmax, t, n, sn, st):
##        Interval.__init__(self, tmin, tmax, '')
##
##    def writeInterval(self, f):
##        f.write("            xmin = " + self.xmin + "\n")
##        f.write("            xmax = " + self.xmax + "\n")
##        f.write("            text = \"" + self.type+str(self.number)+str(self.subnumber)+
##                "\tstress="+str(self.stress)+"\taccent="+str(self.accent)+"\" \n")        


class Word(Interval):
    def __init__(self, tmin, tmax, txt):
        # Word text
        Interval.__init__(self, tmin, tmax, txt)
        # subphrase that the phoneme belong to (Subphrase instance)
        self.subphrase = None
        # Position of word in subphrase
        self.number = None          # Need phrase break tier
        # Syllable Count (int)      
        self.syllableCount = 0
        # *Part of Speech (string)
        self.partOfSpeech = None    # Need grammar tier 
        # Recent Frequency (float)  
        self.recentFreq = None      # HOW TO DEFINE RECENT?
        # Dialogue Frequency (float)
        self.dialogFreq = None
        # Language Frequency (float)
        self.langFreq = None
        # *Prominence (int)
        self.prominence = False
        
    def writeInterval(self, f):
        f.write("            xmin = " + str(self.xmin) + "\n")
        f.write("            xmax = " + str(self.xmax) + "\n")
        if self.subphrase==None:
            text = ''
        else:
            text = str(self.subphrase.phrase.IP)+':'+str(self.subphrase.ip) +':'+str(self.number)
        f.write("            text = \"" +text+"\" \n")        

        
    
class Subphrase(Interval):
    """ Subphrase level context """
    def __init__(self, tmin, tmax, ip, text, f):
        Interval.__init__(self, tmin, tmax, '')
        # Subphrase text (list of strings)
        self.text = text
        # phrase that the phoneme belong to (Phrase instance)
        self.phrase = None
        # Position of subphrase in phrase
        self.ip = ip
        # Word Count (int)
        self.wordCount = len(text)
        # Frequence in Dialogue (float)
        self.dialogFreq = f
        # Grammatical Constituent (string)
        self.gramConst = None
        
    def writeInterval(self, f):
        f.write("            xmin = " + str(self.xmin) + "\n")
        f.write("            xmax = " + str(self.xmax) + "\n")
        f.write("            text = \"" + str(self.ip)+"\" \n")        


        
class Phrase(Interval):
    """ Phrase level context """
    def __init__(self, tmin, tmax, IP, text,f):
        Interval.__init__(self, tmin, tmax, '')
        # Phrase text (list of strings)
        self.text = text
        # Position of phrase in dialog
        self.IP = IP
        # Word Count (int)
        self.wordCount = len(text)
        # Frequence in Dialogue (float)
        self.dialogFreq = f
        # Grammatical Constituent (string)  
        self.gramConst = None       # Need additional information
        
    def writeInterval(self, f):
        f.write("            xmin = " + str(self.xmin) + "\n")
        f.write("            xmax = " + str(self.xmax) + "\n")
        f.write("            text = \"" + str(self.IP)+"\" \n")




    

        

    
