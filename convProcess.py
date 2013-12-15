"""
convProcess.py
Combines the functionality of generatePhonesTier.py, saveTierAsLM.py, and LexiconExtract.py, used for batch processing 16 textgrids at once.
1. Generates a Phones tier
2. Saves words tier as .lm
3. Saves phones tier as .lm
4. Saves lexicon as _lexicon.txt
"""
import sys, logging, pickle
from lexiconToLMTypes import *
# Require Python 3.x
if sys.version_info[0] < 3:
    print("Error: The TextGrid processor requires Python 3.0 or above. Exiting.\n")
    sys.exit(1)

#This will crash on python 2.x so it has to go below the version test
from ExtendedTextGrid import *
 

def findWordsTier(tg, filename):
    wtier = None
    tier_names = [tier.name for tier in tg]
    for pn in ["word", "words", "Word", "Words", filename, filename[:-1]]:
        if pn in tier_names:
            wtier = tg.get_tier(pn)

    if wtier == None:
        print(filename)
        for i, tier in zip(range(len(tg)), tg):
            print(str(i) + " " + tier.name)
        wt = int(input("Words tier: "))
        wtier = tg[wt]
    return wtier

def saveTierAsLM(tier,name,filepath):
    newtg = TextGrid(oprint=False)
    newtg.append(tier)
    newtg.saveAsLM(filepath[:-9]+"_"+name)

def lexiconFromTier(wtier,filepath):
    # Dictionary Path
    cmupath = "cmudict.0.7a"
    DICT = open(cmupath)
    vocab = []
    my_lexicon = {}
    words = {}
    count = 0

    for interval in wtier:
        word = interval.text.strip(" ?.\t\"+'[],").lower()
        for wordpart in word.split():
            if wordpart in words:
                words[wordpart.strip(" ?.\t\"+'[],")] += 1
            else:
                words[wordpart.strip(" ?.\t\"+'[],")] = 1

    vocab += words.keys()

    vocab = list(set(vocab))
    anomalies = vocab           # irregular pronounciation
    non_phn = []
    for entry in DICT:
        if not entry.startswith(";;;"):
            word = entry.split()[0].lower()
            if word in vocab:
                if not word in LMref.lexicon:
                    LMref.lexicon[word.lower().strip("\t \" +?.'[],")] = entry.strip('\n').lower()
                anomalies.remove(word)
                my_lexicon[word.lower().strip("\t \" +?.'[],")] = entry.strip('\n').lower()

    DICT.close()

    print("The following words were not found in the dictionary:")
    for word in anomalies:
        if not word.startswith("<") and not word.endswith(">") and not word in LMref.lexicon:
            print("\t"+word)
    if len(anomalies) > 0:
        fix = input("Fix anomalies now (yes/no)? ")
    else:
        fix = "no"
    if fix.lower()!="no":
        for word in anomalies:
            if not word.startswith("<") and not word.endswith(">") and not word in LMref.lexicon:
                while True:
                    pron = input(word+": ")
                    if pron.startswith("!"): 
                        if pron[1:] in LMref.lexicon:
                            LMref.lexicon[word.lower().strip("\t \" +?.'[],")]=word + "  " + " ".join(LMref.lexicon[pron[1:]].split()[1:])
                            break
                        else:
                            print(pron[1:] + "not found in lexicon")  
                    elif pron:
                        LMref.lexicon[word.lower().strip("\t \" +?.'[],")]=word + "  " + pron.strip()
                        break

    lexpath = filepath[:-9]+ "_lexicon.txt"
    out = open(lexpath, "w")
    out.write(";;; This lexicon is a subset of CMUdict containing words from "+filepath+"\n")
    out.write(";;; It was generated from the CMU dictionary file "+cmupath+"\n")
    for word in my_lexicon:
        out.write(LMref.lexicon[word]+"\n")
    out.close()

def generateLandmarkTier(phonetier):
    import phones_to_landmarks_dict
    d = phones_to_landmarks_dict.c
    
    lmtier = PointTier(name="LM", xmin = 0, xmax=phonetier.xmax)
    
    for interval in phonetier:
        try:    
            # non-words
            phone = interval.text.lower().strip("\t \" +?.'[],012")     # ignore uncertainty marks
            if not ('<' in phone or '>' in phone or phone=='' or phone=="#"):    
                lms=d[phone]
                duration = (interval.xmax-interval.xmin)/len(lms)    # duration of each phoneme

                # Find phoneme positions
                n = 0
                sn = 0
                prevType = None
                
                for i in range(len(lms)):
                    lm = lms[i]
                    if len(lms)==1: #Single LM (V or glide)
                        i = .5 #Put LM in middle of phone
                    time_of_lm= interval.xmin+i*duration   # start time of current phoneme                                    
                    lm_point = Point(time_of_lm, lm)
                    lmtier.append(lm_point)    
        except KeyError:       # ignore (but print) unrecognized phones
            print('Cannot parse word interval:', interval.text)
    return lmtier
def extendLexicon(filename):
    pass

def processFromPath(filename, filepath):
    tg = ExtendedTextGrid(f=filepath)
    tg.oprint = False

    wtier = findWordsTier(tg, filename)

    saveTierAsLM(wtier,"words", filepath)

    lexiconFromTier(wtier, filepath)

    tg.predictPhns(wtier.name, "gen_phones")

    saveTierAsLM(generateLandmarkTier(tg.get_tier("gen_phones")), "landmarks", filepath)

    saveTierAsLM(tg.get_tier("gen_phones"), "phones", filepath)

if __name__ == "__main__":
    # for i in range(1, 17):
    #     filename = "conv{num:02d}g".format(num=i)
    #     filepath = "../landmarks/matcher-data/"+filename+".TextGrid"
    #     print("Processing "+filename)
    #     skip = input("Skip (y/n)? ")
    #     if skip=="n":
    #         processFromPath(filename, filepath)
    #     pickle.dump(lexicon, open("lexicon", 'wb'))

    filename = "conv09g_jessk"
    filepath = "../TIMIT labeling/AEMT/"+filename+".TextGrid"
    processFromPath(filename,filepath)