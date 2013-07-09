"""
- By Minshu Zhan 2012
[Usage]
1) Read file
    - .textgrid (praat) file: ExtendedTextGrid(f='conv07.textgrid')
    - .pkl (TextGrid python object) file: ExtendedTextGrid.readObject('conv07.pkl')
2) Predict landmarks given words, hand-labeled landmarks, and comments (presumbly 
named "Words", "Landmarks", "Comments" respectively):
    - Run tg.putPhns()
    - Run tg.predictLM()
3) Align observed and predicted landmarks
    - Run tg.convertLM() to change the format of hand labels (ignore the warnings for now)
    - Run tg.linkLMtoWords("predicted") and tg.linkLMtoWords("observed")
    - Run tg.alignLM()
4) LM context in praat as a tier
    - lm_tier.links("Words"), lm_tier.links("phones") etc  
5) LM alignment as a tier
    - lm_tier.aligned() 
6) Write file
    - tg.writeGridToPath('conv07') (notice omission of extension name; both .textgrid and 
    .pkl will be created.)
    - alias: tg.saveAs('conv07')
    - save with the original name: tg.save()
7) Write out context in a tab-delimited format
    - tg.saveTab()
"""

from TGProcess import *
import pickle
import LMref 


class ExtendedTextGrid(TextGrid):
    def __init__(self, f):
        "f: textgrid file name"
        if f[-8:].lower()!='.textgrid':
            f+='.textgrid'
        TextGrid.__init__(self, filepath = f)
        self.fname = f[:-9]

    def readObject(tg):   # static method for reading .pkl file
        "tg: pkl file name including extension"        
        pkl= pickle.load(open(tg, 'rb'))
        pkl.fname = tg[:-4]
        return pkl
    
    def writeGridToPath(self, path):
        """ Write both textgrid and pickle files."""
        TextGrid.writeGridToPath(self,path)
        fpkl = open(path+'.pkl','wb')
        pickle.dump(self, fpkl)
        
    def save(self):
        self.writeGridToPath(self.fname)
    def saveAs(self, path):
        "Save to a new file; path should not have any file extension; directory must exist"
        self.fname = path
        self.writeGridToPath(path)



    def saveTab(self):
        """ Save as .tab file named 'fname' """
        f = open(self.fname+'.tab', 'w')
        phones = self.get_tier('phones')
        words = self.get_tier('Words')
        plms = self.get_tier('predictedicted')
        def pLMcontext(plm):
            phn_context = '\t'.join([phones[i].context() for i in plm.links['phones']])
            wd_context = '\t'.join([words[i].context() for i in plm.links['words']])
            if plm.counterLM!=None:
                if plm.mark==plm.counterLM.mark:
                    y='P'       # Preserved
                else:
                    y = 'M'     # Modified
            else:
                y = 'D'         # Deleted
            return '\t'.join([phn_context,wd_context, y])
        x1s = ['_cls','_acnt', '_type','_num', '_snum', '_acnt']
        h1='\t'.join(['\t'.join([y+ x for x in x1s]) for y in ['phn1', 'phn2']])
        x2s = ['_text', '_prom', '_ip', '_IP']
        h2 = '\t'.join(['\t'.join([y+ x for x in x2s]) for y in ['w1', 'w2']])
        n=2*len(x1s+x2s)
        header = '\t'.join([h1, h2, 'modification'])+'\n'+ \
        '\t'.join(['discrete' for i in range(n+1)])+'\n'+\
        '\t'*n+'class\n'
        f.write(header)
        f.write('\n'.join([pLMcontext(m) for m in plms]))
        f.close()

        
    def extendWords(self):
        "Change all Interval instances in 'words' tier into Word instances  " 
        words = self.get_tier('words')
        new_words = IntervalTier('words', self.xmin, self.xmax)
        for w in words:
            new_words.append(Word(w.xmin, w.xmax, w.text))
        self.tiers.remove(words)
        self.tiers = [new_words]+self.tiers
        
        
    def putPhns(self):
        "Translate words into phoneme sequences according to lexicon and append a 'phones' tier."""
        text = self.get_tier('words')
        # Initiate new textgrid tiers for predicted landmarks, phonemes, voicing, and nosal info
        phn_tier = IntervalTier(name="phones", xmin = 0, xmax=text.xmax)
        
        for interval in text:
            try:    
                # non-words
                word = interval.text.lower().strip("\t \" +?.'[],")     # ignore uncertainty marks
                if ('<' in word or '>' in word or word==''):    
                    cur_phn = Phoneme(interval.xmin, interval.xmax)         # silence phoneme
                    phn_tier.append(cur_phn)      # update "phoneme" tier
                # words
                else:
                    phonemes=LMref.lexicon[word].split()[1:]      # keeps the phonemes only (DictEntry := WORD PHONEME+)
                    duration = (interval.xmax-interval.xmin)/len(phonemes)    # duration of each phoneme

                    # Find syllabic positions
                    n = 0
                    sn = 0
                    prevType = None                   
                    for i in range(len(phonemes)):
                        phn = phonemes[i]
                        tphn= interval.xmin+i*duration   # start time of current phoneme                                    
                        if phn[-1] in '012': # vowel -> nucleus
                            t = 'n'
                            stress = phn[-1]
                        else:               # consonant 
                            stress = None
                            if n==0:
                                t = 'o'
                            else:
                                t = 'a'
                        if prevType != t:
                            sn=0
                            if t=='n':
                                n+=1    
                        sn+=1
                        cur_phn = Phoneme(tphn, tphn+duration, phn, t, n, sn)
                        phn_tier.append(cur_phn)
                        prevType = t                       
                    # Determine 'c' (coda) by iterating through the word reversely
                    i=-1
                    end_phn = phn_tier[i]
                    while end_phn.type == 'a':
                        end_phn.type = 'c'
                        i-=1
                        end_phn = phn_tier[i]
                        
            except:       # treat non-recognizable words as silences
                print('Cannot parse word interval:', interval)
                cur_phn = Phoneme(interval.xmin, interval.xmax)
                phn_tier.items.append(cur_phn)      # update "phoneme" tier
                prev_phn = cur_phn
        self.append(phn_tier)
        # Put in another tier showing syllabic positions of phonemes
##        position = IntervalTier(name = 'syll. pos.', xmin=self.xmin, xmax=self.xmax)
##        for p in phn_tier:
##            position.append(Interval(p.xmin, p.xmax, p.pos()))
##        self.append(position)
        
        
    
    def convertLM(self, verbose=False):
        """
        Convert hand-labeled landmarks into the standard format if possible
        (or leave unchanged if parsing failed) and put them into new tier 'observed'
        (See 'Relating manual landmark labels with predicted landmark labels' in reference folder.)
        Return the unconverted points.
        """
        
        old_lms = LMTier.lmTier(self.get_tier('landmarks')).splitLMs()
        old_comments = LMTier.lmTier(self.get_tier("comments")).splitLMs()
        new_lms = old_lms.merge(old_comments)
        new_lms.name = 'observed'
        errors = []

        print('Converting hand-labeled landmarks into standard representation....')
        for point in new_lms:
            try:
                point.mark = LMref.stdLM(point.mark)
            except Exception as e:
                print(e)
                errors.append(point)           
        self.append(new_lms)
        return errors

    def predictLM(self):
        """ Predict landmarks from generated phonemes."""
        try:
            phns = self.get_tier('phones')
        except:
            raise Exception("Phoneme tier not found!")
        lm_tier = LMTier(name="predicted", xmin = self.xmin, xmax=self.xmax)                
##        g_tier = PointTier(name="g", xmin = self.xmin, xmax=self.xmax)
##        n_tier = PointTier(name="v",xmin = self.xmin, xmax=self.xmax)

        prev = Phoneme(0,0)
        for phn in phns:
            # generate landmark from phoneme pairs
            lm=LMref.predict_table[LMref.phoneme_class(prev.text)][LMref.phoneme_class(phn.text)]            
            if lm!='':
                lm_tier.insert(LMPoint(phn.xmin, lm))
                
##            # glottalization
##            if is_voiced(prev.text) and not is_voiced(phn):
##                g_tier.insert(Point(phn.xmin, mark='-g'))
##            elif is_voiced(phn) and not is_voiced(prev.text):
##                g_tier.insert(Point(phn.xmin, mark='+g'))
##            # velopharyngeal
##            if is_nasal(prev.text) and not is_nasal(phn):
##                n_tier.insert(Point(phn.xmin, mark='-n'))
##            elif is_nasal(phn) and not is_nasal(prev.text):
##                n_tier.insert(Point(phn.xmin, mark='+n'))
                
            prev=phn
        
        self.append(LMTier.lmTier(lm_tier).splitLMs())
        
    def split(self, target, reference, delimiter='#'):
        """
        Split target tier around delimiters found in the reference tier.
        Return a list of sections, each represented as a tuple      
        target: name of PointTier
        reference: name of IntervalTier
        delimiter: a string
        """
##        This function was originally created to split a long sequence of landmarks
##        by silences to reduce the work of alignment; nonetheless it applies to all
##        label types.
        
        sections = []
        smin = 0
        smax = 0
        target_tier=self.get_tier(target)
        ref_tier = self.get_tier(reference)
        
        for p in ref_tier:            
            if p.text==delimiter:
                smax = (p.xmax+p.xmin)/2     # midpoint of boundary silence interval                
                if smax>smin:                 
                    section = target_tier.findAsIndexRange(smin, smax)
                    sections+=[section]
                smin = smax
            else:
                smax = p.xmax
        if smax>smin:            
            section = target_tier.findAsIndexRange(smin, smax)

            sections+= [section]
        return sections

    def linkLMtoWords(self, tname):
        """ Create links from landmarks in given LMTier to 'words' IntervalTier.
        tname: name of landmark tier. """
        words = self.get_tier('words')
        lmTier = self.get_tier(tname)
        lmTier.linkToIntervalTier(words)
        
    def linkLMtoPhones(self):
        """ Create links from predicted landmarks to 'phones' IntervalTier."""
        plms = self.get_tier('predicted')
        phns = self.get_tier('phones')
        plms.linkToIntervalTier(phns)
                
                
    def alignLM(self):
        '''
        Modified implementation of Needleman-Wunsch algorithm, seen at http://en.wikipedia.org/wiki/Needleman-Wunsch_algorithm.
        Minimizes cost of deletions, insertions of mutations, where all three are weighted equally undesirable,
        while forbidding alignments the cross word boundaries.
        Requires the existence of the predicted and actual landmark tier.
        '''

        # Cost values
        INFTY = 1000000
        D = 0   # deletion
        I = -1   # insertion
        MATCH = 1   # match 
        MISS = -1   # mutation
        words = self.get_tier('words')
        plms = self.get_tier('predicted')
        alms = self.get_tier('observed')
        phns = self.get_tier('phones')
        # Split the sequence down around silences
        psections = self.split('predicted', 'phones')
        asections = self.split('observed', 'phones')

        
        def compare(predLM, actlLM, poffset=0, aoffset=0):
            """ Computes the similarity of two landmark labels. A match occurs if two labels are identical or
            if one is representing the deletion or uncertainty of the other. """
            pword1,pword2 = predLM.links['words']
            aword1,aword2 = actlLM.links['words']            

            # Crossover cannot exceed two words
            if abs(pword1-aword1)>1 and abs(pword2-aword2)>1:
                return -INFTY
            # 
            if predLM.mark.strip('-x?')==actlLM.mark.strip('-x?'):  
                return MATCH
            elif '-x' in actlLM.mark:      # BAD: LM deletion label M-x not matching corresponding LM label M
                return -INFTY   
            return MISS

        def align(l1,s1,e1, l2,s2,e2):
            """
            Align two sequences given by l1[s1:e1], l2[s2:e2]
            Note that e1, e2 are exclusive bounds.
            l1: predicted sequence. 
            l2: actual sequence. 
            """
            # lengths of sequences
            n = e1-s1
            m = e2-s2

            # F[j][i] is a tuple (C, prev) where C is the minimum cost of aligning the first i points in l1 with the
            # first j points in l2, and prev is the index of the optimal alignment among F[j-1][i], F[j][i-1], F[j-1][F-1]
            # represented as a tuple (j,i)
            F = [[(I*j, (j-1, 0))] for j in range(m+1)] #Generate basis column
            F[0] = [(D*i,(0, i-1)) for i in range(n+1)] #Generate basis row
            F[0][0]= (0, None)          

            for j in range(1,m+1):         
                for i in range(1,n+1):                    
                    deletion = (F[j][i-1][0] + D, (j,i-1))
                    insertion = (F[j-1][i][0] + I, (j-1, i))                    
                    mutation = (F[j-1][i-1][0] + compare(l1[s1+i-1],l2[s2+j-1]), (j-1,i-1))                                                       
                    opt = max([deletion, insertion, mutation])      # max compares the first item in the (C, prev) tuples
                    F[j].append(opt)
                    
            #Fun stats:
            insertionCount = 0
            deletionCount = 0
            mutationCount = 0
            noChangeCount = 0  

            # Find the aligned sequence which yielded the minimal cost
            (j,i) = (m,n)    #"Bottom-right"
            while i>0 or j>0:
                if F[j][i][1]==(j-1,i):
                    #Insertion of element in l2 that doesn't exist in l1.
                    insertionCount+= 1
                    l2[s2+j-1].counterLM=None
                    (j,i) = (j-1,i)
                    
                elif F[j][i][1] == (j, i-1):
                    #Deleted elements exists in l1 but not l2.
                    deletionCount += 1
                    l1[s1+i-1].counterLM=None
                    (j,i) = (j,i-1)
                    
                elif F[j][i][1] == (j-1, i-1):
                    if l1[s1+i-1].mark==l2[s2+j-1].mark:                    
                        noChangeCount += 1
                    else:
                        mutationCount += 1
                    l1[s1+i-1].counterLM = l2[s2+j-1]
                    l2[s2+j-1].counterLM = l1[s1+i-1]
                    (j,i) = (j-1,i-1)

                else:
                    raise Exception("Error aligning landmarks",l1[i+s1],l2[j+s2]) 
                                    
            total = insertionCount+deletionCount+mutationCount

            print("Compared", m, "predicted landmarks against", n, "actual landmarks")
            print("Total number of alterations is ", total, ":")
            print("   " + str(insertionCount) + " insertions,")
            print("   " + str(deletionCount) + " deletions, ")
            print("   " + str(mutationCount) + " mutations,")
            print("   " + str(noChangeCount) + " preserved.")

        for i in range(len(psections)):
            s1 = psections[i][0]
            e1 = psections[i][1]
            s2 = asections[i][0]
            e2 = asections[i][1]
            print("Aligning section", i, ', from', plms[s1].time, 'to', plms[e1-1].time)
            align(plms, s1,e1, alms, s2, e2)
        plms.counterLMTier = alms
        alms.counterLMTier = plms

    def addBreaks(self, breaks):
        """ Construct phrase and subphrase context tier according to given breaks;
        also link each word with its corresponding phrase and subphrase.
        Breaks: a PointTier
        """
        words = self.get_tier("words")
        phrs = IntervalTier("phrases", self.xmin, self.xmax)
        sphrs = IntervalTier("subphrases", self.xmin, self.xmax)

        # Initiate links field in words --> TO-DO: modify constructor
        for w in words:
            w.links['ip']=-1
            w.links['IP']=-1
        
        # First pass: put phrasing information in words
        o = 0
        for w in words:
            bs =  breaks.findAsIndexRange(w.xmin, w.xmax, offset=o)
            for i in bs[:-1]:
                if '3' in breaks[i].mark:
                    w.break3 = True
                else:
                    w.break3 = False
                if '4' in breaks[i].mark:
                    w.break4 = True
                else:
                    w.break4 = False
            o = bs[-1]
            
        # Second pass: create subphrases
        text = []       # words in subphrase
        tprev = self.xmin
        for w in words:
            if LMref.is_word(w.text):
                text+=[w]
                w.links['ip']=len(text)
                if w.break3:
                    sphrs.append(Subphrase(tprev,w.xmax,text))
                    text=[]
                    tprev = w.xmax
        if not w.break3:
                sphrs.append(Subphrase(tprev,w.xmax,text))
            
        # Third pass: crease phrases
        text = []       # words in phrase
        tprev = self.xmin
        for w in words:
            if LMref.is_word(w.text):
                text+=[w]
                w.links['IP']=len(text)
                if w.break4:
                    phrs.append(Phrase(tprev,w.xmax,text))
                    text=[]
                    tprev = w.xmax
        if not w.break4:
                phrs.append(Phrase(tprev,w.xmax,text))

        self.append(sphrs)
        self.append(phrs)        

    def addTones(self, tones):
        """ Set tone attribute of phonemes; requires completion of lm alignment. """
        count=0
        bad=[]
        o=0
        lm_tier = self.get_tier('observed')
        phn_tier=self.get_tier('phones')
        wd_tier = self.get_tier('words')
        # Update phonemes
        for t in tones:
            if '*' in t.mark:
                count+=1
                # Find the nearest observed landmarks 
                ind = lm_tier.findLastAsIndex(t.time,o)
                prevLM = lm_tier[ind]
                succLM = lm_tier[ind+1]
                # Find the corresponding predicted landmarks
                prevPLM = prevLM.counterLM
                succPLM = succLM.counterLM
                # Find associated phonemes
                phns = []
                if prevPLM!=None:
                    phns+= prevPLM.links['phones']
                if succPLM!=None:
                    phns+= succPLM.links['phones']
                done=False
                marked=None                
                for p in [phn_tier[i] for i in phns]:
                    if LMref.phoneme_class(p.text)=='v':
                        if not done:
                            p.accent = True
                            done=True
                            marked=p
                        else:
                            if marked!=p:
                                print("Prominance", t, "has been used on",
                                      marked, "not adding to", p)
                if not done:
                    print("Did not use prominance", t)
                o=ind
        # Update words
        o=0
        for t in tones:
            if '*' in t.mark:
                ind = wd_tier.findAsIndex(t.time,o)
                wd_tier[ind].prominence=True
                o=ind
           

            


class LMPoint(Point):
    def __init__(self, time, mark): 
        Point.__init__(self, time, mark)
        # the phoneme pair which generates the LM and the LM (Phoneme instances)
        self.counterLM = None
        self.links = {}

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
                    # splitted lms result from the same phoneme transitions, i.e. lm.phns
                    out.append(LMPoint(t, ss.strip()))     
                    t += subdelta
            else:
                out.append(LMPoint(t, s.strip()))
                t+= delta
        return out




class LMTier(PointTier):
    """ Class Invariant - All items must be LMPoint instances """
    def __init__(self, name, xmin, xmax):
        PointTier.__init__(self, name, xmin, xmax)
        counterLMTier = None
        
    def lmTier(ptier):
        new = LMTier(ptier.name,ptier.xmin,ptier.xmax)
        for p in ptier:
            new.append(LMPoint(p.time, p.mark))
        return new
    
    def splitLMs(self, delta = EPSILON*10, subdelta = EPSILON):
        """ Split concurrent landmark labels into seperate labels ','-seperated lms are
        DELTA apart; '/'-seperated lms are SUBDELTA apart. Return a new PointTier instance. """
        ptier = LMTier(self.name, self.xmin, self.xmax)     
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

    def merge(self, ptier):
        """ Return a new PointTier that merges self and ptier.
        ptier: a PointTier
        """
        new = LMTier(self.name+'+'+ptier.name, min(self.xmin, ptier.xmin), max(self.xmax,ptier.xmax))
        new.items = self.items+ptier.items
        new.items.sort()
        return new
    
    def insert(self, lmpoint):
        if not isinstance(lmpoint, LMPoint):
            raise Exception("Not a LMPoint instance: ", lmpoint)
        PointTier.insert(self, lmpoint)

    def linkToIntervalTier(self, iTier):
        """ Link LM points to intervals in iTier (phones, words, etc.)
        according to temporal proximity. tname: name of an IntervalTier """
        # TO-DO: doubly-directed link
        if 'predicted'==self.name:
            delta = 2000*EPSILON
            print('PRED')
        else:
            delta = 100*EPSILON
        offset = 0      # moving start of search
        for p in self.items:
            prev = iTier.findAsIndex(p.time-delta, offset-10)    # for concurrent points
            succ = iTier.findAsIndex(p.time+delta, offset-10)
            p.links[iTier.name] = (prev, succ)
            offset = succ
            
    def links(self, tname):
        """ Return a tier representation of landmarks' links to another tier."""
        link_tier=PointTier(self.name+'->'+tname, self.xmin, self.xmax)
        links = []
        for m in self.items:
            links.append(Point(m.time, str(m.links[tname])))
        links.sort()
        link_tier.items = links
        return link_tier
                
    def aligned(self, mode = 'm'):
        """ Return a LMTier with time adjustment on each point to
        line up with its counter landmark, if present; insert 
        mark where a counter lm is not found; deletion is implied
        by a missing point."""
        if self.counterLMTier==None:
            print('Not aligned.')
            return
        tier = LMTier('modifications', self.xmin, self.xmax)
        if mode == 'a':
            tier = LMTier('aligned', self.xmin, self.xmax)
            
        for lm in self.items:
            if lm.counterLM == None:
                tier.insert(LMPoint(lm.time, lm.mark+'-x'))
            else:
                if lm.mark!=lm.counterLM.mark:     # show changes only
                    tier.insert(LMPoint(lm.counterLM.time, lm.mark+'->'+lm.counterLM.mark))
                elif mode=='a':
                    tier.insert(LMPoint(lm.counterLM.time, lm.mark))
                                    
                
        for lm in self.counterLMTier:
            if lm.counterLM==None:
                tier.insert(LMPoint(lm.time, lm.mark+'-!'))
                if '-' in lm.mark:
                    print('WARNING: insertion of comment', lm)
         
        return tier

    def reset(self):
        """ Clear alignment by setting counterLM to None for all LMPoints."""
        self.counterLMTier = None
        for m in self.items:
            m.counterLM=None
          
        
class Phoneme(Interval):
    def __init__(self, tmin, tmax, phn='#', t='', n=0, sn=0):
        """ Default values corresponds to a silence interval. """
        Interval.__init__(self, tmin, tmax, phn)
        
        # manner class of the phoneme (string)
        self.manner = LMref.phoneme_class(phn)
        
        # Lexical stress (int)
        try:
            self.stress = int(phn[-1])
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
        self.prom = False     # default
        

    def context(self):
        return '\t'.join([str(attr) for attr in [self.manner, self.stress, self.type, self.number, self.subnumber]])

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




class Word(Interval):
    def __init__(self, tmin, tmax, txt):
        # Word text
        Interval.__init__(self, tmin, tmax, txt)
        self.links = {}
      # Syllable Count (int)      
        self.syllableCount = 0
        # *Part of Speech (string)
        self.partOfSpeech = ''    # Need grammar tier 
        # Recent Frequency (float)  
        self.recentFreq = -1      # HOW TO DEFINE RECENT?
        # Dialogue Frequency (float)
        self.dialogFreq = -1
        # Language Frequency (float)
        self.langFreq = -1
        # *Prominence (int)
        self.prominence = False
    def context(self):
        return '\t'.join([str(attr) for attr in [self.text, self.prominence, self.links['ip'], self.links['IP']]])
        
  
    
class Subphrase(Interval):
    """ Subphrase level context (seperated by 3-breaks) """
    def __init__(self, tmin, tmax, words):
        Interval.__init__(self, tmin, tmax, ' '.join([w.text for w in words]))
        # Subphrase text (list of strings)
        self.words = words
        # phrase that the phoneme belong to (Phrase instance)
        self.phrase = None
        # Frequence in Dialogue (float)
        self.dialogFreq = None
        # Grammatical Constituent (string)
        self.gramConst = None


        
class Phrase(Interval):
    """ Phrase level context (seperated by 4-breaks"""
    def __init__(self, tmin, tmax, words):
        Interval.__init__(self, tmin, tmax, ' '.join([w.text for w in words]))
        # Phrase text (list of pointers to Word intervals)
        self.words = words
        # Frequence in Dialogue (float)
        self.dialogFreq = None
        # Grammatical Constituent (string)  
        self.gramConst = None       # Need additional information


        

    
               
            
        
