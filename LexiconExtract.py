import pickle, sys
from TGProcess import *

# Require Python 3.x
if sys.version_info < (3, 0):
    print("Error: The TextGrid processor requires Python 3.0 or above. Exiting.\n")
    sys.exit(1)

# Dictionary Path
cmupath = "cmudict.0.7a"
DICT=open(cmupath)

# File Path(s)
# --using user prompt instead--
# wordfiles = ["conv01_landmarks_ssh-edits_3-11-09_no-auto-labels.textgrid",
#              "conv02g_ym_fixed_lma_ssh_2-25-08-to-nmv.textgrid",
#              "conv03g-or-5__ssh_9-11-08.textgrid",
#              "conv04g_fixed_lma_7-24-07_ssh-3-28-08.textgrid",
#              "conv05g_merged_1-complete.textgrid",
#              "conv06g_ch_fixed.textgrid",
#              "conv08gdmw.textgrid",
#              "yinmon07g_lm.textgrid"
#              ]

f = False
while not f:
    path = input(".textgrid file path: ")
    if path.lower().endswith(".textgrid"):
        try:
            f = open(path, "r")
        except IOError:
            print ("The file does not exist")
    else:
        print ("Must be a .textgrid file")

lexicon = {}
vocab = []

# wordfile=open(fname)
words = {}
count=0
text = ""

# Find word tier
tg = TextGrid(oprint=False)
tg.readGridFromPath(path)
for tier in tg:
    if 'word' in tier.name.lower() or 'conv' in tier.name.lower():     # Word tier is named differently in different textgrid files
        text = tier
        break
#OR, assuming that text tier always comes first:
if not text:
    text = tg.tiers[0]    
print ("found text tier ", text.name)
use = input("Use this tier (yes/no)? ")
if not (use.lower()=="yes" or use.lower()=="y"):
    for tier, i in zip(tg, range(len(tg.tiers))):
        print (i + " " + tier.name)
    use = input("Use tier: ")
    text = tg.tiers[int(use)]

print ("\nprocessing file", path, " ...")

for interval in text:
    word = interval.text.strip(" ?.\t\"").lower()
    if word in words:
        words[word]+=1
    else:
        words[word]=1

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

#print (lexicon)
# Output File
# out=open("lexicon", 'wb')
# pickle.dump(lexicon, out)

out.close()
DICT.close()

print("Warning! The following words were not found in the dictionary:")
for word in anomalies:
    if not word.startswith("<") and not word.endswith(">"):
        print("\t"+word)
fix = input("Fix anomalies now (yes/no)? ")
if fix.lower()=="yes":
    for word in anomalies:
        if not word.startswith("<") and not word.endswith(">"):
            pron = input(word+": ")
            if pron:
                lexicon[word]=word + "  " + pron.strip()

# jessk added 6/17/13: Save as CMU-formatted Dictionary
if path.lower().endswith(".textgrid"):
    outpath = path[:-9]
else:
    outpath = path
outpath += "_lexicon.txt"

out = open(outpath, "w")
out.write(";;; This lexicon is a subset of CMUdict containing words from "+path+"\n")
out.write(";;; It was generated from the CMU dictionary file "+cmupath+"\n")
for word in lexicon:
    out.write(lexicon[word]+"\n")

print("Saved to "+outpath+".")
out.close()