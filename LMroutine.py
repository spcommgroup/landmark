from ExtendedTextGrid import *

data = 'conv07_113'
##data='conv07_121031'

g = ExtendedTextGrid.readObject(data+'.pkl')

##g.putPhones()
##g.convertLM()
##g.predictLM()
##g.linkLMtoWords('act. lm')
##g.linkLMtoWords('pred. lm')

##
##
### Cost values
##INFTY = 1000000
##D = -1   # deletion
##I = -1   # insertion
##MATCH = 1   # match 
##MISS = -1   # mutation
##words = g.get_tier('words')
##plms = g.get_tier('pred. LM')
##alms = g.get_tier('act. LM')
##phns = g.get_tier('phones')
##psections = g.split('pred. LM', 'phones')
##asections = g.split('act. LM', 'phones')
##
##'''
##def compare(predLM, actlLM, poffset=0, aoffset=0):
##    """ Computes the similarity of two landmark labels. A match occurs if two labels are identical or
##    if one is representing the deletion or uncertainty of the other. """
##    if predLM==None:
##        if actlLM.mark[-1] in 'x?':
##            return -INFTY
##        return I
##    pword1,pword2 = predLM.links['words']
##
##    if actlLM==None:
##        if predLM.mark[-1] in '-x+?':
##            print('shouldnt happen...')
##            return -INFTY
##        return D
##
##    aword1,aword2 = actlLM.links['words']
##        
##    # Crossover cannot exceed two words
##    if abs(pword1-aword1)>1 and abs(pword2-aword2)>1:
##        return -INFTY
##    # 
##    if predLM.mark.strip('')==actlLM.mark.strip(' -x?'):  
##        return MATCH
##    elif actlLM.mark.strip()[-1] in 'x?':      # BAD: comment not matching corresponding LM
##        return -INFTY   
##    return MISS
##'''
##
##def compare(predLM, actlLM, poffset=0, aoffset=0):
##    """ Computes the similarity of two landmark labels. A match occurs if two labels are identical or
##    if one is representing the deletion or uncertainty of the other. """
##    if predLM==None:
##        if actlLM.mark[-1] in 'x?':
##            return -INFTY
##        elif actlLM.mark[-1] =='+':
##            return MATCH                    
##        return I
##    pword1,pword2 = predLM.links['words']
##
##    if actlLM==None:
##        return D
##    aword1,aword2 = actlLM.links['words']                
##
##    # Crossover cannot exceed two words
##    if abs(pword1-aword1)>1 and abs(pword2-aword2)>1:
##        return -INFTY
##    if  actlLM.mark[-1]=='+':
##        return -INFTY
##    
##    p= predLM.mark
##    a= actlLM.mark.strip(' -x?')
##    if p in a:
##        return MATCH    # G v.s. Gc, Gr            
##    elif actlLM.mark[-1] in 'x?':      # BAD: comment not matching corresponding LM
##        return -INFTY   
##    return MISS
##
##
##def align(l1,s1,e1, l2,s2,e2):
##    """
##    Align two sequences given by l1[s1:e1], l2[s2:e2]
##    Note that e1, e2 are exclusive bounds.
##    l1: predicted sequence. 
##    l2: actual sequence. 
##    """
##    # lengths of sequences
##    n = e1-s1
##    m = e2-s2
##
##    # F[j][i] is a tuple (C, prev) where C is the minimum cost of aligning the first i points in l1 with the
##    # first j points in l2, and prev is the index of the optimal alignment among F[j-1][i], F[j][i-1], F[j-1][F-1]
##    # represented as a tuple (j,i)
##    F = [[(I*j, (j-1, 0))] for j in range(m+1)] #Generate basis column
##    F[0] = [(D*i,(0, i-1)) for i in range(n+1)] #Generate basis row
##    F[0][0]= (0, None)          
##
##    for j in range(1,m+1):         
##        for i in range(1,n+1):                    
##            insertion = (F[j][i-1][0] + compare(None, l2[s2+j-1]), (j,i-1))
##            deletion = (F[j-1][i][0] + compare(l1[s1+i-1], None), (j-1, i))                    
##            mutation = (F[j-1][i-1][0] + compare(l1[s1+i-1],l2[s2+j-1]), (j-1,i-1))
####            print([deletion, insertion, mutation])
##            opt = max([deletion, insertion, mutation])      # max compares the first item in the (C, prev) tuples
##            F[j].append(opt)
##            
##    #Fun stats:
##    insertionCount = 0
##    deletionCount = 0
##    mutationCount = 0
##    noChangeCount = 0  
##
##    # Find the aligned sequence which yielded the minimal cost
##    (j,i) = (m,n)    #"Bottom-right"
##    while i>0 or j>0:
##        print(j, i, F[j][i])
##        if F[j][i][1]==(j-1,i):
##            #Insertion of element in l2 that doesn't exist in l1.
##            insertionCount+= 1
##            l2[s2+j-1].counterLM=None
##            (j,i) = (j-1,i)
##            
##        elif F[j][i][1] == (j, i-1):
##            #Deleted elements exists in l1 but not l2.
##            deletionCount += 1
##            l1[s1+i-1].counterLM=None
##            (j,i) = (j,i-1)
##            
##        elif F[j][i][1] == (j-1, i-1):
##            if l1[s1+i-1].mark.strip()==l2[s2+j-1].mark.strip():                    
##                noChangeCount += 1
##            else:
##                mutationCount += 1
##            l1[s1+i-1].counterLM = l2[s2+j-1]
##            l2[s2+j-1].counterLM = l1[s1+i-1]
##            (j,i) = (j-1,i-1)
##
##        else:
##            raise Exception("Error aligning landmarks",l1[i+s1],l2[j+s2]) 
##                            
##    total = insertionCount+deletionCount+mutationCount
##
##    print("Compared", n, "predicted landmarks against", m, "actual landmarks")
##    print("Total number of alterations is ", total, ":")
##    print("   " + str(insertionCount) + " insertions,")
##    print("   " + str(deletionCount) + " deletions, ")
##    print("   " + str(mutationCount) + " mutations,")
##    print("   " + str(noChangeCount) + " preserved.")
##    return F   
##
####for i in range(len(psections)):
##i=16
##s1, e1 = psections[i]
##s2, e2 = asections[i]
##print("Aligning section", i, ', from', plms[s1].time, 'to', plms[e1-1].time)
##F=align(plms, s1,e1, alms, s2, e2)
##plms.counterLMTier = alms
##alms.counterLMTier = plms
##f = F[:]
##for j in range(e2-s2+1):
##    for i in range(e1-s1+1):
##        #print(F[j][i])
##        s, p = f[j][i]
##        if p!=None:
##            p = (alms[p[0]+s2], plms[p[1]+s1])
##            f[j][i]=s, p
            
