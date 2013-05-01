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
    - Run tg.linkLMtoWords("pred. LM") and tg.linkLMtoWords("act. LM")
    - Run tg.alignLM()
4) LM context in praat as a tier
    - lm_tier.links("Words"), lm_tier.links("phones") etc  
5) LM alignment as a tier
    - tg.aligned() 
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
from tables import *


class ExtendedTextGrid(TextGrid):
    def __init__(self, f):
        TextGrid.__init__(self, filepath = f)
        self.fname = f[:-9]

    def readObject(tg):   # static method for reading .pkl file
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

    def saveTab(self):
        """ Save as .tab file named 'fname' """
        f = open(self.fname+'.tab', 'w')
        phones = self.get_tier('phones')
        words = self.get_tier('Words')
        plms = self.get_tier('pred. LM')
        alms = self.get_tier('act. LM')
        def pLMcontext(plm):
            phn_context = '\t'.join([phones[i].context() for i in plm.links['phones']])
##            wd_context = '\t'.join([words[i].context() for i in plm.links['Words']])
            c = plm.counterLM
            if c!=None:
                prosody='\t'.join([str(v!=None) for v in c.links.values()])
                if plm.mark==c.mark:
                    y='P'       # Preserved
                elif c.mark[-1]=='x':
                    y='D'
                elif c.mark[-1]=='?':   # Weakened
                    y='W'
                else:
                    y = 'M'     # Modified
            else:
                prosody = '\t'.join([str(False)]*4)
                y = 'D'         # Deleted
            
            return '\t'.join([plm.mark, phn_context, prosody, y])
        x1s = ['_cls','_acnt', '_type','_num', '_snum']
        h1='\t'.join(['\t'.join([y+ x for x in x1s]) for y in ['phn1', 'phn2']])
        h0 = 'lm'

##        x2s = ['_text', '_prom', '_ip', '_IP']
##        h2 = '\t'.join(['\t'.join([y+ x for x in x2s]) for y in ['w1', 'w2']])
        h2 = alms[0].links.keys()
        n=1+2*len(x1s)+len(h2)      # number of attributes
        header = '\t'.join([h0, h1, '\t'.join(h2), 'outcome'])+'\n'+ \
        '\t'.join(['discrete' for i in range(n+1)])+'\n'+\
        '\t'*n+'class\n'
        f.write(header)
        f.write('\n'.join([pLMcontext(m) for m in plms]))
        f.close()

        
    def extendWords(self):
        words = self.get_tier('Words')
        new_words = IntervalTier('words', self.xmin, self.xmax)
        for w in words:
            new_words.append(Word(w.xmin, w.xmax, w.text))
        self.tiers.remove(words)
        self.tiers = [new_words]+self.tiers
        
        
    def putPhns(self):
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
                    phonemes=lexicon[word].split()[1:]      # keeps the phonemes only (DictEntry := WORD PHONEME+)
                    duration = (interval.xmax-interval.xmin)/len(phonemes)    # duration of each phoneme

                    # Find phoneme positions
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
        position = IntervalTier(name = 'syll. pos.', xmin=self.xmin, xmax=self.xmax)
        for p in phn_tier:
            position.append(Interval(p.xmin, p.xmax, p.type+' '.join([str(p.number), str(p.subnumber)])))
        self.append(position)
        
    
    def convertLM(self):
        """
        Convert a single hand-labelled landmark into the standard format.
        Returns a new Point instance; the mark is unchanged if conversion failed.
        """
        old_lms = LMTier.lmTier(self.get_tier('landmarks')).splitLMs()
        old_comments = LMTier.lmTier(self.get_tier("comments")).splitLMs()
        merged = old_lms.merge(old_comments)
        self.append(merged)
        new_lms = LMTier('act. LM', self.xmin, self.xmax)

                    
        print('Converting hand-labeled landmarks into standard representation....')
        for point in merged:
            lm = point.mark
            if 'x' in lm and '?' in lm:       # Forbid concurrent '-x' and '-?' 
                raise Exception("'-x' and '-?' occurred together: "+lm)
            suffix = ''
            if 'x' in lm:
                suffix = '-x' 
            elif '?' in lm:
                suffix='-?'
            elif '+' in lm:
                suffix = '-+'
            s = lm.strip("?x-+")
            if s in lm_table:
                p=LMPoint( point.time,lm_table[s])
                for pt in p.split(100*EPSILON, 10*EPSILON):
                    pt.mark+=suffix
                    new_lms.append(pt)
            else:                
                print('WARNING: Cannot convert landmark', point)

##        print("Converting glides...")
##        merged = 0
##        ngc = 0
##        ngr = 0
##        prev = LMPoint(0, 'Gr')
##        for lm in new_lms:
##            if lm.mark == 'Gc':
##                ngc+=1
##                if prev.mark == 'Gr':
##                    prev = lm
##            if lm.mark == 'Gr':
##                ngr+=1
##                if prev.mark == 'Gc':
##                    merged+=1
##                    t = (lm.time+prev.time)/2
##                    new_lms.insert(LMPoint(t, 'G'))
##                    new_lms.remove(lm)
##                    new_lms.remove(prev)
##                    prev = lm
##        print("# Merged:", merged)
##        print('# Gc:', ngc)
##        print('# Gr:', ngr)


##        print("Extracting +/-g +/-n labels...")
##        gns = PointTier("g/n", '0', self.xmax)
##        for lm in new_lms:
##            if lm.mark in ['+g', '-g','+n','-n']:
##        ##        print(lm)
##                new_lms.remove(lm)
##                gns.append(lm)
##
##        self.append(gns)                
        self.append(new_lms)

    def predictLM(self):
        """ Predict landmarks from generated phonemes."""
        try:
            phns = self.get_tier('phones')
        except:
            raise Exception("Phoneme tier not found!")
        lm_tier = LMTier(name="pred. LM", xmin = self.xmin, xmax=self.xmax)                
        prev = Phoneme(0,0)
        for phn in phns:
            # generate landmark from phoneme pairs
            lm1, lm2 =predict_table[phoneme_class(prev.text)][phoneme_class(phn.text)]
            t1 = (prev.xmax+prev.xmin)/2
            t2 = phn.xmin
            if lm1.strip()!='':
                lm_tier.insert(LMPoint(t1, lm1.strip()))
            if lm2.strip()!='':
                lm_tier.insert(LMPoint(t2, lm2.strip()))
                                
            prev=phn
        print(lm_tier)
        self.append(LMTier.lmTier(lm_tier).splitLMs())
        
    def split(self, target, reference, delimiter='#'):
        """
        Split target tier according to the delimiters found in the reference tier.
        Return a list of tuples spedifying the range of each section        
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

    def linkLMtoWords(self):
        """ Create links from landmarks in given LMTier to 'words' IntervalTier.
        tname: name of landmark tier. """
        words = self.get_tier('words')
        lmTier = self.get_tier('act. lm')
        lmTier.linkToIntervalTier(words)
        lmTier = self.get_tier('pred. lm')
        lmTier.linkToIntervalTier(words)
        
    def linkLMtoPhones(self):
        """ Create links from predicted landmarks to 'phones' IntervalTier."""
        plms = self.get_tier('pred. LM')
        phns = self.get_tier('phones')
        plms.linkToIntervalTier(phns)
                
                
    def alignLM(self):
        '''
        Modified implementation of Needleman-Wunsch algorithm, seen at http://en.wikipedia.org/wiki/Needleman-Wunsch_algorithm.
        Minimizes cost of deletions, insertions of mutations, where all three are weighted equally undesirably.
        Requires the existence of the predicted and actual landmark tier.
        '''

        # Cost values
        INFTY = 1000000
        D = -1   # deletion
        I = -1   # insertion
        MATCH = 1   # match 
        MISS = -1   # mutation
        words = self.get_tier('words')
        plms = self.get_tier('pred. LM')
        alms = self.get_tier('act. LM')
        phns = self.get_tier('phones')
        psections = self.split('pred. LM', 'phones')
        asections = self.split('act. LM', 'phones')

        
        def compare(predLM, actlLM, poffset=0, aoffset=0):
            """ Computes the similarity of two landmark labels. A match occurs if two labels are identical or
            if one is representing the deletion or uncertainty of the other. """
            if predLM==None:
                if actlLM.mark[-1] in 'x?':
                    return -INFTY
                elif actlLM.mark[-1] =='+':
                    return MATCH                    
                return I
            pword1,pword2 = predLM.links['words']

            if actlLM==None:
                return D
            aword1,aword2 = actlLM.links['words']                

            # Crossover cannot exceed two words
            if abs(pword1-aword1)>1 and abs(pword2-aword2)>1:
                return -INFTY
            if  actlLM.mark[-1]=='+':
                return -INFTY
            
            p= predLM.mark
            a= actlLM.mark.strip(' -x?')
            if p in a:
                return MATCH    # G v.s. Gc, Gr            
            elif actlLM.mark[-1] in 'x?':      # BAD: comment not matching corresponding LM
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
                    insertion = (F[j][i-1][0] + compare(None, l2[s2+j-1]), (j,i-1))
                    deletion = (F[j-1][i][0] + compare(l1[s1+i-1], None), (j-1, i))                    
                    mutation = (F[j-1][i-1][0] + compare(l1[s1+i-1],l2[s2+j-1]), (j-1,i-1))
                    opt = max([deletion, insertion, mutation])      # max compares the first item in the (C, prev) tuples
                    F[j].append(opt)
                    
            #Fun stats:
            insertionCount = 0
            deletionCount = 0
            mutationCount = 0
            noChangeCount = 0
            score = 0
            print(F[m][n])
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
                    if l1[s1+i-1].mark.strip()==l2[s2+j-1].mark.strip():                    
                        noChangeCount += 1
                    else:
                        mutationCount += 1
                    l1[s1+i-1].counterLM = l2[s2+j-1]
                    l2[s2+j-1].counterLM = l1[s1+i-1]
                    (j,i) = (j-1,i-1)

                else:
                    raise Exception("Error aligning landmarks",l1[i+s1],l2[j+s2]) 
                                    
            total = insertionCount+deletionCount+mutationCount
            if total>5:
                    
                print("Compared", n, "predicted landmarks against", m, "actual landmarks")
                print("Total number of alterations is ", total, ":")
                print("   " + str(insertionCount) + " insertions,")
                print("   " + str(deletionCount) + " deletions, ")
                print("   " + str(mutationCount) + " mutations,")
                print("   " + str(noChangeCount) + " preserved.")

        for i in range(len(psections)):
            s1, e1 = psections[i]
            s2, e2 = asections[i]
            print("Aligning section", i, ', from', plms[s1].time, 'to', plms[e1-1].time)
            align(plms, s1,e1, alms, s2, e2)
        plms.counterLMTier = alms
        alms.counterLMTier = plms


    def addBreaks(self, breaks, r=0.35):
##        """ Construct phrase and subphrase context tier according to given breaks;
##        also link each word with its corresponding phrase and subphrase.
##        breaks: a PointTier
##        """
        """ Mark the closest observed landmark to each 3 or 4 break """
        count=0
        offset=0
        lm_tier = self.get_tier('act. LM')
        for lm in lm_tier:
            lm.links['3-break']=None
            lm.links['4-break']=None
##        phn_tier=self.get_tier('phones')
##        wd_tier = self.get_tier('words')
        # Update phonemes
        for t in breaks:
            if '3' in t.mark and 'p' not in t.mark:
##                print( t)
                count+=1
                # Find the nearest observed V landmark
                nbrs=[(abs(lm.time-t.time), lm) for lm in sorted(lm_tier.find(t.time-r, t.time+r))]
##                print(t)
                if nbrs!=[]:
                    dt, m = nbrs[0]
                    m.links['3-break']=t
            if '4' in t.mark and 'p' not in t.mark:
##                print( t)
                count+=1
                # Find the nearest observed V landmark
                nbrs=[(abs(lm.time-t.time), lm) for lm in sorted(lm_tier.find(t.time-r, t.time+r))]
##                print(t)
                if nbrs!=[]:
                    dt, m = nbrs[0]
                    m.links['4-break']=t
                    
        
##        words = self.get_tier("words")
##        phrs = IntervalTier("3-break", self.xmin, self.xmax)
##        sphrs = IntervalTier("4-break", self.xmin, self.xmax)
##
##        # Initiate links field in words --> TO-DO: modify constructor
##        for w in words:
##            w.links['3-break']=-1
##            w.links['4-break']=-1
##        
##        # First pass: put phrasing information in words
##        o = 0
##        for w in words:
##            bs =  breaks.findAsIndexRange(w.xmin, w.xmax, offset=o)
##            for i in bs[:-1]:
##                if '3' in breaks[i].mark:
##                    w.break3 = True
##                else:
##                    w.break3 = False
##                if '4' in breaks[i].mark:
##                    w.break4 = True
##                else:
##                    w.break4 = False
##            o = bs[-1]
##            
##        # Second pass: create subphrases
##        text = []       # words in subphrase
##        tprev = self.xmin
##        for w in words:
##            if is_word(w.text):
##                text+=[w]
##                w.links['ip']=len(text)
##                if w.break3:
##                    sphrs.append(Subphrase(tprev,w.xmax,text))
##                    text=[]
##                    tprev = w.xmax
##        if not w.break3:
##                sphrs.append(Subphrase(tprev,w.xmax,text))
##            
##        # Third pass: crease phrases
##        text = []       # words in phrase
##        tprev = self.xmin
##        for w in words:
##            if is_word(w.text):
##                text+=[w]
##                w.links['IP']=len(text)
##                if w.break4:
##                    phrs.append(Phrase(tprev,w.xmax,text))
##                    text=[]
##                    tprev = w.xmax
##        if not w.break4:
##                phrs.append(Phrase(tprev,w.xmax,text))
##
##        self.append(sphrs)
##        self.append(phrs)        

    def addTones(self, tones):
        """ Set tone attribute of phonemes; requires completion of lm alignment. """
        count=0
        bad=[]
        o=0
        lm_tier = self.get_tier('act. LM')
        for lm in lm_tier:
            lm.prominence=False
            lm.links['*']=None
##        phn_tier=self.get_tier('phones')
##        wd_tier = self.get_tier('words')
        # Update phonemes
        for t in tones:
            if '*' in t.mark:
                count+=1
                # Find the nearest observed V landmark
                nbrs=[(abs(lm.time-t.time), lm) for lm in sorted(lm_tier.find(t.time-0.2, t.time+0.2))]
##                print(t, nbrs)
                try:
                    dt, v = nbrs[[lm.mark=='V' for (dt, lm) in nbrs].index(True)]
                    v.links['*']=t
                    v.prominence = True
                except:
                    print('Cannot add prominence', t)
##                ind = lm_tier.findLastAsIndex(t.time,o)
##                prevLM = lm_tier[ind]
##                succLM = lm_tier[ind+1]
##                # Find the corresponding predicted landmarks
##                prevPLM = prevLM.counterLM
##                succPLM = succLM.counterLM
##                # Find associated phonemes
##                phns = []
##                if prevPLM!=None:
##                    phns+= prevPLM.links['phones']
##                if succPLM!=None:
##                    phns+= succPLM.links['phones']
##                done=False
##                marked=None                
##                for p in [phn_tier[i] for i in phns]:
##                    if phoneme_class(p.text)=='v':
##                        if not done:
##                            p.accent = True
##                            done=True
##                            marked=p
##                        else:
##                            if marked!=p:
##                                print("Prominance", t, "has been used on",
##                                      marked, "not adding to", p)
##                if not done:
##                    print("Did not use prominance", t)
##                o=ind
##        # Update words
##        o=0
##        for t in tones:
##            if '*' in t.mark:
##                ind = wd_tier.findAsIndex(t.time,o)
##                wd_tier[ind].prominence=True
##                o=ind
    def linkInserted(self, r=0.2):
        alms = self.get_tier('act. lm')
        plms = self.get_tier('pred. lm')
        for p in plms:
            p.links['ins'] = [None, None]
            
        for i in range(len(alms)):
            a = alms[i]
            if a.counterLM==None:
                p1=plms.findLast(a.time)
                if a.time-p1.time<r:
                    if p1.links['ins'][1]!=None:
                        print(a, ':', p1,'(-', p1.counterLM, ')', 'is already responsible for', p1.links['ins'][1])
                    p1.links['ins'][1] = a
                    print(a, ':', p1,'(-', p1.counterLM, ')', p1.links['ins'])
                p2=plms.findLast(a.time+r)
                if p2.links['ins'][0]!=None:
                    print(a,':',p2,'(-', p2.counterLM, ')', 'is already responsible for', p2.links['ins'][0])
                if p2.time-a.time<r and p2!=a:
                    p2.links['ins'][0] = a
                    print(a, ':', p2,'(-', p2.counterLM, ')', p2.links['ins'])
            


class LMPoint(Point):
    def __init__(self, time, mark): 
        Point.__init__(self, time, mark)
        # the phoneme pair which generates the LM and the LM (Phoneme instances)
        self.counterLM = None
        self.links = {}
        self.prominence=False

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
                    # ['Tn', 'Tf', '-n', '+n', '-g', '+g'] ARE TEMPORARILY IGNORED!!
                    if ss.strip() not in ['Tn', 'Tf', '-n', '+n', '-g', '+g']:
                        out.append(LMPoint(t, ss.strip()))     
                        t += subdelta
            elif s.strip() not in ['Tn', 'Tf', '-n', '+n', '-g', '+g']:
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
        if 'pred' in self.name:
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
        mark ("m-+") where a counter lm is not found; deletion ("m-x") is implied
        by a missing point."""
        if self.counterLMTier==None:
            print('Not aligned.')
            return
        tier = LMTier('modifications', self.xmin, self.xmax)
        if mode == 'a':
            tier = LMTier('aligned', self.xmin, self.xmax)
            
        for lm in self.items:
            if lm.counterLM == None:
                tier.insert(LMPoint( lm.time, 'D:'+lm.mark))
            else:
                if lm.mark!=lm.counterLM.mark:     # show changes only
                    tier.insert(LMPoint(lm.counterLM.time, 'M:'+lm.mark+'-->'+lm.counterLM.mark))
                elif mode=='a':
                    tier.insert(LMPoint(lm.counterLM.time, lm.mark))
                                    
                
        for lm in self.counterLMTier:
            if lm.counterLM==None:
                tier.insert(LMPoint(lm.time, 'I:'+lm.mark))
                if '-' in lm.mark and '+' not in lm.mark:
                    print('WARNING: insertion of comment', lm)
         
        return tier

    def reset(self):
        """ Clear alignment by setting counterLM to None for all LMPoints."""
        self.counterLMTier = None
        for m in self.items:
            m.counterLM=None
          
        
class Phoneme(Interval):
    def __init__(self, tmin, tmax, phn='#', t='#', n=0, sn=0):
        """ Default values corresponds to a silence interval. """
        Interval.__init__(self, tmin, tmax, phn)
        
        # manner class of the phoneme (string)
        self.manner = phoneme_class(phn)
        
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


        

    
               
            
        
