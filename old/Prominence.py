import TGProcess
import pickle

source = "conv07_pb2a"


tg = pickle.load(open(source+".pkl", 'rb'))
tones = tg.get_tier("tones")
lms = tg.get_tier("alt lm")
plms = tg.get_tier("splitted lm")




def putAccent(lm):
    p1, p2 = lm.phns
    if p1.manner=='v':
        p1.accent = True
    if p2.manner=='v':
        p2.accent = True
    if p1.accent and p2.accent:
        raise Exception('ERROR: put accent on consecutive vowels', lm.phns, 'at', lm)
    if not (p1.accent or p2.accent):
        raise Exception('ERROR: cannot find a vowel to put accent on among', lm.phns, 'at', lm)


def addAccent(tones_tier, lm_tier):
    count=0
    global bad
    bad = []
    for t in tones_tier:
        if '*' in t.mark:
            count+=1
            # Find the nearest observed landmarks 
            ind = lm_tier.findLastAsIndex(t.time)
            prevLM = lm_tier[ind]
            succLM = lm_tier[ind+1]
            # Find the corresponding predicted landmarks
            prevPLM = prevLM.counterLM
            succPLM = succLM.counterLM

            if prevPLM == None and succPLM==None:
                print('ERROR: cannot locate vowel accented by', t)
                bad.append(t)
            elif prevPLM == None:
                try:
                    putAccent(succPLM)
                except:
                    bad.append(t)
            elif succPLM == None:
                try:
                    putAccent(prevPLM)
                except:
                    bad.append(t)
            elif prevPLM.phns == succPLM.phns:    # If two lms resulted from the transition of same pair of phonemes, processing one
                try:
                    putAccent(prevPLM)
                except:
                    bad.append(t)                
            elif prevPLM.phns[1]==succPLM.phns[0]:
                if prevPLM.phns[1].manner=='v':
                    prevPLM.phns[1].accent=True
                else:
                    print('ERROR: at',t, prevPLM.phns, succPLM.phns)
                    bad.append(t)
            else:
                bad.append(t)
                print('ERROR: at',t,prevPLM.phns, succPLM.phns)
    print('Done processing', count, 'accent marks. The following marks require attention:')
    print(bad)
            

def addProminence(lms_actual, lms_expected, tones_tier, lm_tier):
    for t in tones:
        if '*' in t.mark:
            count+=1
            # Find the nearest observed landmarks 
            ind = lm_tier.findLastAsIndex(t.time)
            prevLM = lm_tier[ind]
            succLM = lm_tier[ind+1]
            # Find the corresponding predicted landmarks
            prevPLM = lms_expected[lms_actual.index(prevLM)]
            succPLM = lms_expected[lms_actual.index(succLM)]
            trans1 = None
            trans2 = None
            if prevPLM!=None:
                trans1 = prevPLM.phns
            if succPLM!=None:
                trans2 = succPLM.phns

            if trans1==trans2:
                try:
                    p1,p2 = trans1
                except:
                    print('ERROR: cannot find accented vowel at', t)
                if p1.manner=='v':
                    p1.prominence=True
                    
                                

            if trans1==None:
                trans = trans2
            if trans2==None:
                trans = trans1

                
                
            if trans1!=None and trans2!=None:
                if trans1[0]!=trans2[0] and trans1[1]!=trans2[0]: # if the phoneme transitions that resulted in the two adjacent lms are neither idential nor adjecent
                    print(t)
                    print(prevLM)
                    print(lms_expected[lms_actual.index(prevLM)])
                    print(trans1)
                    print(trans1[0].word, trans1[1].word)
                    print(succLM)
                    print(lms_expected[lms_actual.index(succLM)])
                    print(trans2)
                    print(trans2[0].word, trans2[1].word)
                    print('\n')
addAccent(tones, lms)


pickle.dump(tg, open(source+'.pkl', 'wb'))
