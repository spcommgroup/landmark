from ExtendedTextGrid import *
##from matplotlib import *


g=ExtendedTextGrid.readObject('conv07b.pkl')

# min & max lm space
def distance_range(g):
    prev=0
    min_lm_space=min([tg[1][i].time-tg[1][i-1].time for i in range(1, len(tg[1]))])
    print(min_lm_space)

    # min distance to word boundary
    min_lm_word_dist=100000
    i=0
    for w in tg[0]:
        i,j = tg[1].findAsIndexRange(w.xmin, w.xmax, i)
        min_lm_word_dist=min(abs(tg[1][i].time-w.xmin), abs(w.xmax - tg[1][j-1].time))
        if min_lm_word_dist<0.000001:
            print(w)
    print(min_lm_word_dist)


# min distance to phoneme boundary



def alignLM(g):
    '''
    Modified implementation of Needleman-Wunsch algorithm, seen at http://en.wikipedia.org/wiki/Needleman-Wunsch_algorithm.
    Minimizes cost of deletions, insertions of mutations, where all three are weighted equally undesirably.
    Requires the existence of the predicted and actual landmark tier.
    '''

    # Cost values
    words = g.get_tier('words')
    plms = g.get_tier('pred. LM')
    alms = g.get_tier('act. LM')
    phns = g.get_tier('phones')
    psections = g.split('pred. LM', 'phones')
    asections = g.split('act. LM', 'phones')

    for i in range(len(psections)):
        s1, e1 = psections[i]
        s2, e2 = asections[i]
        print("Aligning section", i, ', from', plms[s1].time, 'to', plms[e1-1].time)
        align(plms, s1,e1, alms, s2, e2)
    plms.counterLMTier = alms
    alms.counterLMTier = plms

    
def compare_general(predLM, actlLM, poffset=0, aoffset=0):
    """ Compares two points"""    
    if predLM==None:                  
        return I

    if actlLM==None:
        return D
    if predLM.mark == actlLM.mark:
        return MATCH   
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
            insertion = (F[j][i-1][0] + compare_general(None, l2[s2+j-1]), (j,i-1))
            deletion = (F[j-1][i][0] + compare_general(l1[s1+i-1], None), (j-1, i))                    
            mutation = (F[j-1][i-1][0] + compare_general(l1[s1+i-1],l2[s2+j-1]), (j-1,i-1))
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
        print("Total number of alterations: ", total)
        print("   " + str(insertionCount) + " insertions,")
        print("   " + str(deletionCount) + " deletions, ")
        print("   " + str(mutationCount) + " mutations,")
        print("   " + str(noChangeCount) + " preserved.")

def aligned(p,a, mode = 'm'):
    """ Return a LMTier with time adjustment on each point to
    line up with its counter landmark, if present; insert 
    mark ("m-+") where a counter lm is not found; deletion ("m-x") is implied
    by a missing point."""

    tier = LMTier('modifications', p.xmin, p.xmax)
    if mode == 'a':
        tier = LMTier('aligned', g.xmin, g.xmax)
        
    for lm in p:
        if lm.counterLM == None:
            tier.insert(LMPoint( lm.time, 'D: '+lm.mark))
        else:
            if lm.mark!=lm.counterLM.mark:     # show changes only
                tier.insert(LMPoint(lm.counterLM.time, 'M: '+lm.mark+'-->'+lm.counterLM.mark))
            elif mode=='a':
                tier.insert(LMPoint(lm.counterLM.time, lm.mark))
                                
            
    for lm in a:
        if lm.counterLM==None:
            tier.insert(LMPoint(lm.time, 'I: '+lm.mark))
            if '-' in lm.mark and '+' not in lm.mark:
                print('WARNING: insertion of comment', lm)
     
    return tier


##def plot_distance(t):
##    ds = [t[i]-t[i-1] for i in range(1,len(t))]
##    plot(ds)
    
    
def check_alignment(a):
    v_ins = []
    del_ins = []
    
    for lm in a:
        if lm.mark[0]== 'I':
            if 'v' in lm.mark.lower():
                v_ins.append(lm)
    
    for lm in a:
        if lm.mark[0]== 'I':
            if 'x' in lm.mark.lower():
                v_ins.append(lm)

    return v_ins, del_ins




INFTY = 1000000
D = -1   # deletion
I = -1   # insertion
MATCH = 0   # match 
MISS = -1   # mutation

##a1=g[-3]
##a2=g[-1]
##align(a1,0, 180, a2, 0, 178)
##a = aligned(a1, a2)


LMs = [
'V',	#vowel LM			energy peak
'G',	#glide LM				energy dip
'Nc',	#nasal closure LM			abrupt onset of nasal
'Nr',	#nasal release LM			abrupt offset of nasal
'Fc',	#fricative closure LM		abrupt onset of frication
'Fr',	#fricative release LM		abrupt offset of frication
'Sc',	#stop closure LM			cessation of vocal tract activity due to oral closure
'Sr',	#stop release LM			abrupt release of burst energy due to oral release
'Tn',	#stridency onset LM		onset of stridency
'Tf',	#stridency offset LM		offset of stridency

    #(other possible types not dealt with here include abrupt onset and offset of liquids)

'Lc',	#liquid closure LM			abrupt onset of liquid
'Lr',	#liquid release LM			abrupt offset of liquid
]


def catagorize(t):
    E = {}
    for lm in LMs:
        E[lm]=[]
        for m in t:
            if m.mark[0]=='D':
                m
            if lm in m.mark:
                E[lm].append(m)
                if m.counterLM==None:
                    m
    return E

def pLMcontext(plm, phones):
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

def extract_lm(g, lmtype):
    plms = g.get_tier('pred. LM')
    alms = g.get_tier('act. LM')

    pnew = LMTier('pred. '+lmtype, g.xmin, g.xmax)
    anew = LMTier('act. '+lmtype, g.xmin, g.xmax)

    for m in plms:
        if lmtype in m.mark:
            pnew.append(m)
    
    for m in alms:
        if lmtype in m.mark:
            anew.append(m)

    return pnew, anew
        
        
    
def saveTab(g, lmtype, plms, alms):
    """ Save as .tab file named 'fname' """
    f = open(g.fname+'_'+lmtype+'.tab', 'w')
    phones = g.get_tier('phones')
    words = g.get_tier('Words')
    x1s = ['_cls','_acnt', '_type','_num', '_snum']
    h1='\t'.join(['\t'.join([y+ x for x in x1s]) for y in ['phn1', 'phn2']])
    h0 = 'lm'
    h2 = alms[0].links.keys()
    n=1+2*len(x1s)+len(h2)      # number of attributes
    header = '\t'.join([h0, h1, '\t'.join(h2), 'outcome'])+'\n'+ \
    '\t'.join(['discrete' for i in range(n+1)])+'\n'+\
    '\t'*n+'class\n'
    f.write(header)
    f.write('\n'.join([pLMcontext(m, phones) for m in plms]))
    f.close()

    
    
