"""
convProcess.py
Combines the functionality of generatePhonesTier.py, saveTierAsLM.py, and LexiconExtract.py, used for batch processing 16 textgrids at once.
1. Generates a Phones tier
2. Saves words tier as .lm
3. Saves phones tier as .lm
4. Saves lexicon as _lexicon.txt
"""
import sys, logging
# Require Python 3.x
if sys.version_info[0] < 3:
    print("Error: The TextGrid processor requires Python 3.0 or above. Exiting.\n")
    sys.exit(1)

#This will crash on python 2.x so it has to go below the version test
from ExtendedTextGrid import *

for i in range(1, 17):
    filename = "conv{num:02d}g".format(num=i)
    filepath = "../landmarks/matcher-data/"+filename+".TextGrid"
    tg = ExtendedTextGrid(f=filepath)
    tg.oprint = False

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

    #### save words tier as lm ####
    newtg = TextGrid(oprint=False)
    newtg.append(wtier)
    newtg.saveAsLM(filepath[:-9]+"_words")

    #### generate Phones Tier ####
    tg.putPhns(wtier.name, "gen_phones")

    #### save phones tier as lm ####
    newtg = TextGrid(oprint=False)
    newtg.append(tg.get_tier("gen_phones"))
    newtg.saveAsLM(filepath[:-9]+"_phones")

    #### lexicon extract ####
    # Dictionary Path
    cmupath = "cmudict.0.7a"
    DICT = open(cmupath)
    lexicon = {}
    vocab = []

    words = {}
    count = 0

    for interval in wtier:
        word = interval.text.strip(" ?.\t\"").lower()
        if word in words:
            words[word] += 1
        else:
            words[word] = 1

    vocab += words.keys()

    vocab = list(set(vocab))
    anomalies = vocab           # irregular pronounciation
    non_phn = []
    for entry in DICT:
        if not entry.startswith(";;;"):
            word = entry.split()[0].lower()
            if word in vocab:
                lexicon[word] = entry.strip('\n').lower()
                anomalies.remove(word)

    DICT.close()

    print("The following words were not found in the dictionary:")
    for word in anomalies:
        if not word.startswith("<") and not word.endswith(">"):
            print("\t"+word)
    fix = input("Fix anomalies now (yes/no)? ")
    if fix.lower()!="no":
        for word in anomalies:
            if not word.startswith("<") and not word.endswith(">"):
                pron = input(word+": ")
                if pron:
                    lexicon[word]=word + "  " + pron.strip()

    lexpath = filepath[:-9]+ "_lexicon.txt"
    out = open(lexpath, "w")
    out.write(";;; This lexicon is a subset of CMUdict containing words from "+filepath+"\n")
    out.write(";;; It was generated from the CMU dictionary file "+cmupath+"\n")
    for word in lexicon:
        out.write(lexicon[word]+"\n")
    out.close()