"""
convProcess.py
Combines the functionality of generatePhonesTier.py, saveTierAsLM.py, and LexiconExtract.py, used for batch processing 16 textgrids at once.
1. Generates a Phones tier
2. Saves words tier as .lm
3. Saves phones tier as .lm
4. Saves lexicon as _lexicon.txt
"""
import sys, logging, pickle
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
                if not word in lexicon:
                    lexicon[word.lower().strip("\t \" +?.'[],")] = entry.strip('\n').lower()
                anomalies.remove(word)
                my_lexicon[word.lower().strip("\t \" +?.'[],")] = entry.strip('\n').lower()

    DICT.close()

    print("The following words were not found in the dictionary:")
    for word in anomalies:
        if not word.startswith("<") and not word.endswith(">") and not word in lexicon:
            print("\t"+word)
    if len(anomalies) > 0:
        fix = input("Fix anomalies now (yes/no)? ")
    else:
        fix = "no"
    if fix.lower()!="no":
        for word in anomalies:
            if not word.startswith("<") and not word.endswith(">") and not word in lexicon:
                while True:
                    pron = input(word+": ")
                    if pron.startswith("!"): 
                        if pron[1:] in lexicon:
                            lexicon[word.lower().strip("\t \" +?.'[],")]=word + "  " + " ".join(lexicon[pron[1:]].split()[1:])
                            break
                        else:
                            print(pron[1:] + "not found in lexicon")  
                    elif pron:
                        lexicon[word.lower().strip("\t \" +?.'[],")]=word + "  " + pron.strip()
                        break

    lexpath = filepath[:-9]+ "_lexicon.txt"
    out = open(lexpath, "w")
    out.write(";;; This lexicon is a subset of CMUdict containing words from "+filepath+"\n")
    out.write(";;; It was generated from the CMU dictionary file "+cmupath+"\n")
    for word in my_lexicon:
        out.write(lexicon[word]+"\n")
    out.close()

def processFromPath(filename, filepath):
    tg = ExtendedTextGrid(f=filepath)
    tg.oprint = False

    wtier = findWordsTier(tg, filename)

    saveTierAsLM(wtier,"words", filepath)

    lexiconFromTier(wtier, filepath)

    tg.putPhns(wtier.name, "gen_phones")

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

    filename = "conv01g"
    filepath = "../landmarks/matcher-data/"+filename+".TextGrid"
    processFromPath(filename,filepath)