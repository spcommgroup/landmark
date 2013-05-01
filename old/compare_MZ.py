from TGProcess import *
from Context import *
import os
import sys
import time

import pickle 


##if len(sys.argv) < 3:
##    exit("Usage: python compare.py /Path/To/File.TextGrid1 /Path/ToFile.TextGrid2")
##filepath1 = os.path.abspath(sys.argv[1])
##filepath2 = os.path.abspath(sys.argv[2])


INFTY = 1000000
D = 0   #Cost of a deletion
I = 3   #Cost of insertion
MATCH = 1   
MISS = -1   

source = "conv07_pb2"

f = pickle.load(open(source+'.pkl','rb'))       # Use the context-rich textgrid instead!


#TODO: Decide values
#Temporal Mutations Thresholds
diffThresholds = {} #Custom thresholds.  Eg = {'t': 0.010, 'k-cl': 0.00}
defaultDiff = 0.000 #Default threshold for landmarks not listed in diffThresholds

def match(predLM, obsvLM):
    """ Computes the similarity of two landmark labels. A match occurs if two labels are identical or
    if one is representing the deletion or uncertainty of the other. """
    word1 = predLM.phns[0].word
    word2 = predLM.phns[1].word
    t = obsvLM.time

    # Important: any observed landmark is bounded by the word(s) which produced the predicted landmark that it is aligning to    
    if t<word1.xmin or t> word2.xmax:
        return -INFTY
    
    if predLM.mark.strip('-x?')==obsvLM.mark.strip('-x?'):  
        return MATCH
    elif '-x' in obsvLM.mark:      # BAD: LM deletion label M-x not matching corresponding LM label M
        return -INFTY   
    return MISS
    
##
##def parenEqual(a,b):
##    """
##    Compares two strings and treat characters enclosed by parentheses in the second
##    string as flexbile
##    Note that parentheses are escaped only in the second input string, not the first.
##    """
##    #This may return an incorrect result in the case of a/(b)/b/c, because of the semi-parenthesised pair.
##    #However, that will not occur in our data.
##    if a == b:
##        return True #To save time.
##    
##    la = a.split("/")
##    lb = b.split("/")
##    while la:
##        if not lb:
##            return False #Not enough entries
##        if "(" in lb[0] or ")" in lb[0]:
##            if lb[0].strip("()") == la[0]:
##                #Paren'd entry should have been there.
##                la = la[1:]
##            #else paren'd entry shouldn't have been there, but we let it slide.
##            lb = lb[1:]
##        else:
##            if lb[0] == la[0]:
##                #Non paren'd entry matches.
##                la = la[1:]
##                lb = lb[1:]
##            else:
##                #Non paren'd entry doesn't match.  Say they're not equal!
##                return False
##    for itemLeft in lb:
##        if "(" not in itemLeft:
##            #Non paren'd entry, but no template entries left to match it with.  They're unequal!
##            return False
##    return True
                
                
                
def align(l1,l2):
    '''
    Modified implementation of Needleman-Wunsch algorithm, seen at http://en.wikipedia.org/wiki/Needleman-Wunsch_algorithm.
    Minimizes cost of deletions, insertions of mutations, where all three are weighted equally undesirably.
    NOTE: Only works with TGProcess.Point objects, as it relies on the Point.mark attribute.
    l1, l2 are lists of LMPoints.
    Return a tuple (expected, actual, alterTypes) 
    '''
        
    #TO-DO: insertion should be more expensive?
    start = time.time()
##    print("Comparing "+l1.name+" and "+l2.name)

##    M = -2 #Cost of a mutation  --> specified by match() function
##    PI = 0.5 #Cost of inserting a parenthesized item
    #TODO: Would it ever be useful to assign a (+ or -) cost C to a correct match?  I'll need to think about this.
    
    #Strange reverse ordering of n and m, but I'm keeping it this way to stay consistent with Wikipedia. :)
    n = len(l1)
    m = len(l2)

    #F[j][i] is the minimum cost of aligning the first i points in l1 with the first j points in l2.
    #(This includes the numerous deletions or insertions that arise if i != j.)
    F = [[(-I*j, (j-1, 0))] for j in range(0,m+1)] #Generate basis column
    F[0] = [(-D*i,(0, i-1)) for i in range(0,n+1)] #Generate basis row
    F[0][0]= (0, None)

    lastProgressLevel = 0
    for j in range(1,m+1):
        #Extremely ugly progress printouts. :)
##        progress = round(100.0*j/m)
##        if progress != lastProgressLevel:
##            lastProgressLevel = progress
##            print("Progress: " + str(progress) + "%")
##            
        for i in range(1,n+1):
            deletion = (F[j][i-1][0] - D, (j,i-1))
            insertion = (F[j-1][i][0] - I, (j-1, i))
                
            mutation = (F[j-1][i-1][0] + match(l1[i-1],l2[j-1]), (j-1,i-1))
                
                
            
            #firstTen1[i-1] is the mark that correstponds to the CURRENT column
            #This strangeness is a result of the basis offsets.
            # opt is a (similarity, index_pair) tuple where index_pair (j, i) keeps track of the  optimal alignment cost from which the current optimum is derived.
            opt = max([deletion, insertion, mutation])
            F[j].append(opt)
            

    #Fun stats:
    insertionCount = 0
    deletionCount = 0
    mutationCount = 0
    noChangeCount = 0

    #Aligned lists, with None values inserted to align the lists.
    expected = []
    actual = []

    '''Keep track of what modifications happen, where.  Elements will be:
    "ins":     insertion
    "del":     deletion
    "time":    temporal mutation
    "mut":     landmark mutation, NOT accompanied by temporal mutatation
    "timemut": landmark mutation AND temporal mutation
    "---":     exact match, both between point landmarks and point times.'''
##    alterTypes = []

    #Time diffs:
    #Not including a time diffs tier.  Adds no extra info, as the diff can be caluculated \
    #from subtracting the times of a Point from expected and a Point from actual.

    

    (j,i) = (m,n) #"Bottom-right"
    while i>0 or j>0:
##        print(F[j][i])
##        print('\nBEFORE:',id(l1[i-1]), id(l2[j-1]))
##        print(F[j][i])
        if F[j][i][1]==(j-1,i):
            #Insertion of element in l2 that doesn't exist in l1.
            insertionCount+= 1
            expected = [None] + expected
            actual = [l2[j-1]] + actual
            l2[j-1].counterLM=None
##            print('l2', id(l2[j-1]))
##            print('l2',  j-1, l2[j-1])
##            print('(',j,',',i,')->(', j-1,',', i,')')
            (j,i) = (j-1,i)
##            print('l2:', j-1)
            
        elif F[j][i][1] == (j, i-1):
            #Deleted elements exists in l1 but not l2.
            deletionCount += 1
            expected = [l1[i-1]] + expected
            actual = [None] + actual
            l1[i-1].counterLM=None
##            print('l1', id(l1[i-1]))
                  
##            print('l1',i-1, l1[i-1])
##            print('(',j,',',i,')->(', j,',', i-1, ')')
            (j,i) = (j,i-1)
##            print('l1:', i-1)
            
        elif F[j][i][1] == (j-1, i-1):
            if l1[i-1].mark==l2[j-1].mark:                    
                noChangeCount += 1
                expected = [l1[i-1]] + expected
                actual = [l2[j-1]] + actual
            else:
                mutationCount += 1
                expected = [l1[i-1]] + expected
                actual = [l2[j-1]] + actual
##            print('l1:', i-1, l1[i-1])
##            print('l2:', j-1,l2[j-1] )
##            print('(',j,',',i,')->(', j-1,',', i-1, ')')
            l1[i-1].counterLM = l2[j-1]
            l2[j-1].counterLM = l1[i-1]
##            print('l1', id(l1[i-1]), 'l2', id(l2[j-1]))
            (j,i) = (j-1,i-1)
            
            
        else:
            raise Exception("Error aligning landmarks!") 
                            

    total = insertionCount+deletionCount+mutationCount

##    print(expected, actual)
##    print(l1.items, l2.items)

    
    i=0
##    for e in expected:
##        if e!=None:
##            print(id(e), e, id(l1[i]),l1[i])
####            print(l1[i+1].counterLM)
##            i+=1
##            
    print("Compared", len(l1), "landmarks")
    print("The smallest possible number of alterations is ", total, ":")
    print("   " + str(insertionCount) + " insertions,")
    print("   " + str(deletionCount) + " deletions, ")
    print("   " + str(mutationCount) + " mutations,")
    print("   " + str(noChangeCount) + " preserved.")
    if total+noChangeCount!=len(expected):
        print("WARNING: sum does not match!")
    print("Alignment took " + str(time.time()-start) + " seconds. \n")

    return (expected,actual)








#Main code for aligning the landmark tiers from the two TextGrids
##
print("Processing", source)
psections = f.split("Splitted lm", "phoneme")
sections = f.split("alt lm", "phoneme")

print(len(psections), 'sections')
# Aligned output
predicted = []
observed = []

##i = 1

for i in range(len(sections)):
##for i in range(4):
    print(psections[i])
    print("Aligning section", i, ', from', psections[i].xmin, 'to', psections[i].xmax)
    aln1, aln2 = align(psections[i],sections[i])
    predicted += aln1
    observed += aln2

##pickle.dump((predicted, observed), open('alignment(b)0723.pkl','wb'))
pickle.dump(f, open(source+'a.pkl', 'wb'))


##(expected, actual, alterTypes) = align(f.get_tier('predicted lm'),f.get_tier('alt lm'))
##writeResult(expected, actual, alterTypes, 'summary_all.txt')

##
##out1 = open("expected.pkl",'wb')
##out2 = open("actual.pkl",'wb')
##out3 = open("alterTypes.pkl",'wb')
##
##pickle.dump(expected,out1)
##pickle.dump(actual,out2)
##pickle.dump(alterTypes,out3)
