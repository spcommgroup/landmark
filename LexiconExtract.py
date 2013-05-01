import pickle
from TGProcess import *

# Dictionary Path
d = "C:\\Users\mzhan\Documents\urop_speech\data\\"

DICT=open("cmudict.0.7a")

# File Path(s)
wordfiles = ["conv01_landmarks_ssh-edits_3-11-09_no-auto-labels.textgrid",
             "conv02g_ym_fixed_lma_ssh_2-25-08-to-nmv.textgrid",
             "conv03g-or-5__ssh_9-11-08.textgrid",
             "conv04g_fixed_lma_7-24-07_ssh-3-28-08.textgrid",
             "conv05g_merged_1-complete.textgrid",
             "conv06g_ch_fixed.textgrid",
             "conv08gdmw.textgrid",
             "yinmon07g_lm.textgrid"
             ]
## TO-TO: ADD PROMPT INTERFACE

lexicon = {}
vocab = []

for fname in wordfiles:
    print ("\nprocessing file", fname, " ...")
    wordfile=open(d+fname)
    words = {}
    count=0
    
    # Find word tier
    tg = TextGrid()
    tg.readGridFromPath(fname)
    for tier in tg:
        if 'word' in tier.name.lower() or 'conv' in tier.name.lower():     # Word tier is named differently in different textgrid files
            text = tier
            break
    # OR, assuming that text tier always comes first:
##    text = tg.tiers[0]    
    print ("found text tier ", text)
    
    for interval in text:
        word = interval.text.strip(" ?.\t\"").lower()
        if word in words:
            words[word]+=1
        else:
            words[word]=1

    vocab += words.keys()
    wordfile.close()

vocab = list(set(vocab))
anomalies = vocab           # irregular pronounciation
non_phn = []
for entry in DICT:
    if not entry.startswith(";;;"):
        word = entry.split()[0].lower()
        if word in vocab:
            lexicon[word] = entry.strip('\n').lower()
            anomalies.remove(word)


# Output File
out=open("lexicon", 'wb')
pickle.dump(lexicon, out)

out.close()
DICT.close()

