"""
- Minshu Zhan 2013 July
[Usage]
1) Read file
    - .textgrid (praat) file: ExtendedTextGrid(f='conv07.textgrid')
    - .pkl (TextGrid python object) file: ExtendedTextGrid.readObject('conv07.pkl')
2) Predict landmarks and align: given words, hand-labeled landmarks, and comments (presumbly 
named "Words", "Landmarks", "Comments" respectively):
    - Run tg.prepare()
3) Extract context information
    - Run tg.extractContext() 
6) Save
    - tg.save()
    - tg.writeGridToPath('conv07')  textgrid file only
    - alias: tg.saveAs('conv07')    save under a new name (no extension)
7) Write out context in a tab-delimited format that can be parsed by orange
    - tg.saveTab()
"""

from TGProcess import *
import pickle, logging
import LMref

logging.basicConfig(filename="log.txt", level=logging.WARNING)


class ExtendedTextGrid(TextGrid):
    def __init__(self, f):
        "f: textgrid file name"
        if f[-9:].lower()=='.textgrid':
            TextGrid.__init__(self, filepath = f)
            self.fname = f[:-9]
        else: raise Exception('File not found:', f)

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
        phns = self.get_tier('phones')
        words = self.get_tier('Words')
        result = [self.get_tier('Preserved'), self.get_tier('Deleted'), self.get_tier('Inserted'), self.get_tier('Mutated')]
        data = []
        for change in changes:
            for point in change:
                entry = point.context()
                entry['outcome']=change.name
                data.append(entry)

        params = data[0].keys()

        header = '\t'.join(params)

        f.write(header)
        f.write('\n'.join(['\t'.join(e.values()) for e in data]))
        f.close()

        
    def extendWords(self):
        "Change all Interval instances in 'words' tier into Word instances  " 
        words = self.get_tier('words')
        new_words = IntervalTier('words', self.xmin, self.xmax)
        for w in words:
            new_words.append(Word(w.xmin, w.xmax, w.text))
        self.tiers.remove(words)
        self.tiers = [new_words]+self.tiers
        
    def predictPhns(self, wtier="words", newname="phones"):
        "Translate words into phoneme sequences according to lexicon and append a 'phones' tier."""
        text = self.get_tier(wtier)
        # Initiate new textgrid tiers for predicted landmarks, phonemes, voicing, and nosal info
        phn_tier = IntervalTier(name=newname, xmin = 0, xmax=text.xmax)
        
        for interval in text:
            try:    
                # non-words
                word = interval.text.lower().strip("\t \" +?.'[],")     # ignore uncertainty marks
                if ('<' in word or '>' in word or word==''):    
                    cur_phn = Phoneme(interval.xmin, interval.xmax)         # silence phoneme
                    phn_tier.append(cur_phn)      # update "phoneme" tier
                # words
                else:
                    # phonemes=LMref.lexicon[word].split()[1:]      # keeps the phonemes only (DictEntry := WORD PHONEME+)
                    phonemes = []
                    for wordpart in word.split(): #Handle one word interval containing more than 1 word
                        phonemes += LMref.lexicon[word].split()[1:]
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
                logging.warning("Cannot parse word interval: "+str(interval)+" from "+self.fname)
                cur_phn = Phoneme(interval.xmin, interval.xmax)
                phn_tier.items.append(cur_phn)      # update "phoneme" tier
                prev_phn = cur_phn
        phn_tier.fixIntervalSpaces()
        self.append(phn_tier)
        # Put in another tier showing syllabic positions of phonemes
##        position = IntervalTier(name = 'syll. pos.', xmin=self.xmin, xmax=self.xmax)
##        for p in phn_tier:
##            position.append(Interval(p.xmin, p.xmax, p.pos()))
##        self.append(position)
        
    def putPhns(self, wtier="words", newname="phones"):
        """backwards compatibility"""
        predictPhns(self, wtier, newname)
        
        
    
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
        self.append(new_lms.splitLMs())
        return self.tiers[-1]

    def predictLM(self):
        """ Predict landmarks from generated phonemes."""
        phns = self.get_tier('phones')
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
        return self.tiers[-1]
        
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

    def linkToWords(self):
        """ Create links from landmarks in given LMTier to 'words' IntervalTier.
        tname: name of landmark tier. """
        words = self.get_tier('words')
        plms = self.get_tier('predicted')
        olms = self.get_tier('observed')
        plms.linkToIntervalTier(words)
        olms.linkToIntervalTier(words)

                
    def alignLM(self):
        '''
        Modified implementation of Needleman-Wunsch algorithm, seen at http://en.wikipedia.org/wiki/Needleman-Wunsch_algorithm.
        Minimizes cost of deletions, insertions of mutations, where all three are weighted equally undesirable,
        while while certain rules are reinforced.
        Requires the existence of the predicted and actual landmark tier.
        '''

        # Cost values
        INFTY = 1000000
        D = 0   # deletion
        I = -1   # insertion
        MATCH = 1   # match 
        MISS = -1   # mutation

        def compare(plm, olm, poffset=0, aoffset=0):
            """ Computes the similarity of two landmark labels. A match occurs if two labels are identical or
            if one is representing the deletion or uncertainty of the other. """
            if not plm:
                if not olm:
                    return 0
##                elif '-x' in olm.mark:
##                    # Deletion label cannot be an insertion?
##                    return -INFTY
                else:
                    return I
            if not olm:
                return D
                    
            pword1,pword2 = plm.links['words']
            oword1,oword2 = olm.links['words']            

            # landmarks cannot be aligned when they are more than a word apart
            if abs(pword1.index-oword1.index)>1 and abs(pword2.index-oword2.index)>1:
                return -INFTY
            # landmarks should compared without the mutation marking
            p = re.match(LMref.STD_LM, plm.mark).group()
            o = re.match(LMref.STD_LM, olm.mark).group()
            if p==o:
                if '-x' in olm.mark:
                    return D
                return MATCH
            # Deletion label can never be aligned to a landmark other than the one marked deleted i.e. A-x cannot match B-x if A!=B
            elif '-x' in olm.mark:
                return -INFTY   
            return MISS

        def alignSection(l1,s1,e1, l2,s2,e2):
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
                    deletion = (F[j][i-1][0] + compare(l1[s1+i-1],None), (j,i-1))
                    insertion = (F[j-1][i][0] + compare(None,l2[s2+j-1]), (j-1, i))                    
                    mutation = (F[j-1][i-1][0] + compare(l1[s1+i-1],l2[s2+j-1]), (j-1,i-1))                                                       
                    F[j].append(max([deletion, insertion, mutation]) )
                    
            #Stats:
            insertionCount = 0
            deletionCount = 0
            mutationCount = 0
            noChangeCount = 0  

            # Find the aligned sequence which yielded the minimal cost
            print("Section alignment score:", F[m][n])
            (j,i) = (m,n)    #"Bottom-right"
            while i>0 or j>0:
                if F[j][i][0]>=INFTY:
                    # Rule violations
                    raise Exception("Error aligning", l1, s1, ' - ', e1, ' and ', l2,':',s2, '-',e2)
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

            print("Compared", n, "predicted landmarks against", m, "observed landmarks")
            print("Total number of alterations is ", total, ":")
            print("   " + str(insertionCount) + " insertions,")
            print("   " + str(deletionCount) + " deletions, ")
            print("   " + str(mutationCount) + " mutations,")
            print("   " + str(noChangeCount) + " preserved.")

            # Return relevant stats in the order of stat_keys
            result = (insertionCount,deletionCount,mutationCount,noChangeCount)

            return result


        words = self.get_tier('words')      # need to check word boundaries when aligning
        p = self.get_tier('predicted')
        o = self.get_tier('observed')
        self.clearAlignment()
        
        # Split the sequence down around silences
        psections = self.split('predicted', 'phones')
        osections = self.split('observed', 'phones')

        # Stat
        stat_keys = ['ins', 'del', 'mut', 'pre']
        stat = dict((k,[]) for k in stat_keys)

        for s in range(len(psections)):
            s1,e1 = psections[s]
            s2,e2 = osections[s]
            print("Aligning section", s, ', from', s1, p[s1], '/', s2, o[s2], 'to', e1-1, p[e1-1], '/',e2-1, o[e2-1])
            result = alignSection(p, s1,e1, o, s2, e2)
            for i in range(len(stat_keys)):
                stat[stat_keys[i]].append(result[i])
            
        p.counterLMTier = o
        o.counterLMTier = p

        return stat

    def summarize(self):
        """ Four LMTier instances which summarize alignment result. """

        prs = LMTier('Preserved', self.xmin, self.xmax)
        dlt = LMTier('Deleted',  self.xmin, self.xmax)
        ins = LMTier('Inserted',  self.xmin, self.xmax)
        mut = LMTier('Mutated',  self.xmin, self.xmax)

        p = self.get_tier('predicted')
        o = self.get_tier('observed')

        for label in p:
            x = label.copy()
            x.links[p.name]=label
            # todo: merge context links from the observed lm
            if not x.counterLM:
                x.links[o.name]=None
##                print('unlabeled deletion',x)
                dlt.insert(x)
            else:
                x.links[o.name]=x.counterLM
                m = x.counterLM.mark
                if m==x.mark:
                    prs.insert(x)
                elif m==x.mark+'-x':
##                    print('labeled deletion',x)
                    dlt.insert(x)
                else:
                    mut.insert(x)
##                    if m[-1] in ['+', 'x', '?']:
##                        print('WARNING: may not be real mutation',x,'->',x.counterLM)

        for label in o:
            x = label.copy()
            x.links[o.name]=label
            x.links[p.name]=None            
            if not x.counterLM:
                ins.insert(x)                
                if x.mark[-1]=='x':
                    print('WARNING: cannot find landmarked marked as deleted by',x)
        for t in [prs, dlt, ins, mut]:
            self.append(t)
            

    def clearAlignment(self):
        "Remove old alignment information"
        p = self.get_tier('predicted')
        o = self.get_tier('observed')
        for x in p:
            x.counterLM ==None
        for x in o:
            x.counterLM ==None
            

    def prepare(self):
        """ Main routine that predicts landmarks from words and compares with observed landmarks. """
        # Generate landmarks
        if not self.get_tier("phones"):
            self.predictPhns()
        if not self.get_tier("predicted"):
            self.predictLM()        
        if not self.get_tier("observed"):
            self.convertLM()
        
        # If 'Cannot recognize label' exception is raised here, fix corresponding hand labels and run again
        self.get_tier('predicted').checkFormat()
        self.get_tier('observed').checkFormat()

        # Prepare word tier
        self.extendWords()
        self.linkToWords()

        # Align predicted and observed landmarks
        self.alignLM()

        # Produce alignment results (preservations, insertions, deletions, mutations) as LMTier instances
        self.summarize()
            

    def extractBreaks(self):
        """ Construct phrase and subphrase context tier according to given breaks;
        also link each word with its corresponding phrase and subphrase.
        breaks: a PointTier contains break labels
        """
        breaks = self.get_tier("breaks")
        words = self.get_tier("words")
        phrases = PointTier("phrases", self.xmin, self.xmax)
        subphrases = PointTier("subphrases", self.xmin, self.xmax)

##        for w in words:
##            w.break3=None
##            w.break4=None
        
        # First pass: put phrasing information in words
##        o = 0
##        for w in words:
##            bs =  breaks.findBetween(w.xmin, w.xmax, offset=o)
##            for b in bs:
##                if '3' in b.mark:
##                    w.break3 = True
##                if '4' in b.mark:
##                    w.break4 = True
##                o = b.index
##        t = b3[0]       
##        for w in words:
##            w.links[b3.name]=b3.findBetween(w.xmin, w.xmax, t)
##            t = w.links[b3.name][-1]
##        t = b4[0]
##        for w in words:
##            w.links[b4.name]=b4.findBetween(w.xmin, w.xmax, t)
##            t = w.links[b4.name][-1]
            
        # Second pass: word position in subphrases: words.findBetween(sph.xmin, sph.xmax)
        
        b1 = breaks4[0]
        for b2 in breaks4[1:]:
            words = w.findBetween(b1.time, b2.time, words[-1].index+1)
            w1 = words[words[0].index-1]
            w2 = words[words[-1].index+1]
            if w1.xmax - b1 < b1 - w1.xmin:
                words = [w1]+words
            if w2.xmax - b2 > b2 - w2.xmin:
                words.append(w2)            
            sph = Subphrase(b1.time, b2.time, ' '.join([w.text for w in words]))         
            for i in range(len(words)):
                word.links[breaks4.name]=(b1, b2)
                word.links[subphrases.name]=sph
            subphrases.apend(sph)
            b1=b2
        
        b1 = breaks3[0]
        for b2 in breaks3[1:]:
            words = w.findBetween(b1.time, b2.time, words[-1].index+1)
            w1 = words[words[0].index-1]
            w2 = words[words[-1].index+1]
            if w1.xmax - b1 < b1 - w1.xmin:
                words = [w1]+words
            if w2.xmax - b2 > b2 - w2.xmin:
                words.append(w2)            
            ph = Phrase(b1.time, b2.time, ' '.join([w.text for w in words]))         
            for i in range(len(words)):
                word.links[breaks3.name]=(b1, b2)
                word.links[Phrase.name]=ph
            phrases.apend(sph)
            b1=b2

        text = []       
        tprev = self.xmin
        for w in words:
            if LMref.is_word(w.text):
                text+=[w]
                w.ip=len(text)
                if w.break4:
                    sphrs.append(Subphrase(tprev,w.xmax,text))
                    text=[]
                    tprev = w.xmax
        if not w.break4:    # last word
                sphrs.append(Subphrase(tprev,w.xmax,text))
            
        # Third pass: word position in phrases
        text = []       
        tprev = self.xmin
        for w in words:
            if LMref.is_word(w.text):
                text+=[w]
                w.IP=len(text)
                if w.break3:
                    phrs.append(Phrase(tprev,w.xmax,text))
                    text=[]
                    tprev = w.xmax
        if not w.break3:
                phrs.append(Phrase(tprev,w.xmax,text))

        self.append(sphrs)
        self.append(phrs)        

    def extractTones(self):
        """ Associate accents with landmarks and words. """
        count=0
        bad=[]
        o=0
        lm = self.get_tier('observed')
        wd = self.get_tier('words')
        

        tones = self.get_tier('tones').filter('*')
        # Mark landmarks
        t1 = tones[0]
                                            
        for p in lm:
            t1 = tones.findBefore(p.time, t1.index)
            t2 = tones.findAfter(p.time, t1.index)
            p.links[tones.name]=(t1,t2)
                                            

        # Mark words
        t = tones[0]
        for w in wd:
            w.links[tones.name]= tones.findBetween(w.xmin, w.xmax, t.index)
            t = w.links[tones.name][-1]
                                            
                                            
            
        # Mark phonemes
##        for t in tones:
##            if '*' in t.mark:
##                count+=1
##                # Find the nearest observed landmarks 
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
##                    if LMref.phoneme_class(p.text)=='v':
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

    def extractContext(self):
        """ Main function to associate landmarks with contex tiers; overwrite previous runs """
        p = self.get_tier("Predicted")
        d = self.get_tier("Deleted")
        i = self.get_tier("Inserted")
        m = self.get_tier("Mutated")
        summary = p.merge(d).merge(i).merge(m)
        
        # TODO: phrase-subphrase-word-phoneme hierarchy relative positions
       
        
        # TODO: prosody markings associated with different tiers
        self.extractBreaks()
        self.extractTones()        
       

            


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
                    mark = ss.strip()
                    if LMref.is_std(mark):
                        out.append(LMPoint(t, mark))     
                        t += subdelta
                    else:
                        print(mark, 'is not a recognized standard landmark')
            else:
                mark = s.strip()
                if LMref.is_std(mark):
                    out.append(LMPoint(t, mark))
                    t+= delta
                else:
                    print(mark, 'is not a recognized standard landmark')
        return out

    def context(self):
        """ Return all context information in a flat dictionary. Keys are parameter names. """
        c = {}
        c['name']=re.match(LMref.STD_LM, self.mark).group()

        phones = c.links['phones']
        if phones: 
            [c.extend(phn.context().items()) for phn in self.links['phones']]
        else:
            # TODO: guess context for un-aligned landmark
            pass
        return c
            
        


    
class LMTier(PointTier):
    """ Class Invariant - All items must be LMPoint instances """
    def __init__(self, name, xmin, xmax):
        PointTier.__init__(self, name, xmin, xmax)
        counterLMTier = None
        
    def lmTier(ptier):
        """ Converts a regular point tier into LMTier """
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

    def checkFormat(self):
        for p in self.items:
            if not LMref.is_std(p.mark):
                raise Exception("Cannot recognize label", p)
    
    def insert(self, lmpoint):
        if not isinstance(lmpoint, LMPoint):
            raise Exception("Not a LMPoint instance: ", lmpoint)
        PointTier.insert(self, lmpoint)

    def linkToIntervalTier(self, iTier):
        """ Link LM points to closest intervals in iTier (phones, words, etc.)  """
        if 'predicted'==self.name:
            delta = 2000*EPSILON
        else:
            delta = 100*EPSILON
        offset = 0      # moving start of search
        for p in self.items:
            prev = iTier.find(p.time-delta, offset)    # for concurrent points
            offset = succ.index
            succ = iTier.find(p.time+delta, offset)
            p.links[iTier.name] = (prev, succ)

    def linkToPointTier(self, pTier):
        """ Link LM points to the closest point in pTier. """
        # Search boundary
        offset = 0
        delta = 0.1*pTier.minDist() # anything smaller than half of the min distance in pTier
        for p in self.items:
            link = pTier.findLastAsIndex(p.time+delta, offset-1)
            if link+1<len(pTier.items) and abs(pTier[link+1].time - p.time) < abs(pTier[link].time - p.time):
                link = link+1
            offset = link
            p.links[pTier.name] = link
            
            
        
    def links(self, tname):
        """ Return a tier representation of landmarks' links to another tier."""
        link_tier=PointTier(self.name+'->'+tname, self.xmin, self.xmax)
        links = []
        for m in self.items:
            links.append(Point(m.time, str(m.links[tname])))
        links.sort()
        link_tier.items = links
        return link_tier

    def reset(self):
        """ Clear alignment by setting counterLM to   None for all LMPoints."""
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


        self.links = {}
        

    def context(self):
        c = {}
        c['manner class']=self.manner
        c['type']= self.type
        c['stress']=self.stress
        c['number']=self.number
        c['subnumber']=self.subnumber

        # TODO: association with breaks and tones
        
        return c

    
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

        self.links = {}

    def context(self):
        c = {}
        c['text']=c.text
        c['ip']=self.ip
        c['IP']=self.IP

        return c
        
  
    
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
