"""
Parses additional textgrid tiers which contains contextual information
And add the information into the main textgrid file source
""" 

import pickle
from TGProcess import *
from Context import *

source= 'conv07_p'
prosody = "conv07g_RS"

# Main textgrid 
##tg_main = TextGrid(filepath = source+'.TextGrid')
tg_main = pickle.load(open(source+'.pkl', 'rb'))

# Prosodic info textgrid
tg_prosody = TextGrid(filepath=prosody+".textgrid")

# Merge into main textgrid
tg_main.append(tg_prosody.get_tier('tones'))
tg_main.append(tg_prosody.get_tier('breaks'))

words = tg_main.get_tier("word-context")
plms = tg_main.get_tier("splitted lm")
phns = tg_main.get_tier("phoneme")
breaks = tg_main.get_tier("breaks")
tones = tg_main.get_tier("tones")

      
        
phrasing = []

phrs = IntervalTier("phrases", tg_main.xmin, tg_main.xmax)
sphrs = IntervalTier("subphrases", tg_main.xmin, tg_main.xmax)


for b in breaks:
    if '3' in b.mark or '4' in b.mark:     # TO-DO
        phrasing.append(b)


P = []
IP = 1 
p = []
fP = 0
fp = 0
prev = -1
sphrase = Subphrase('0','', 1,[],None)
phrase = Phrase('0','',1,[],None)
phrs.items.append(phrase)
sphrs.items.append(sphrase)


def is_word(w):
    return not ('<' in w or '>' in w or w=='')


for b in phrasing:
##    print("BREAK", b)
    
    cur = words.findAsIndex(b.time)
    if words[cur].xmax-b.time>b.time-words[cur].xmin:   # for inaccurate labels
       cur-=1 
    if cur == prev:   # skip the break if it locates within the same word as the previous break
        continue
##    print('WORDS', prev, cur, words[prev+1:cur+1])
    for word in words[prev+1:cur+1]:
        if is_word(word.text):
##            print(word)
            p+= [word.text]
##            print('p', p)
            word.number=len(p)      # all phonemes linking to the word are updated
            word.subphrase = sphrase
    sphrase.xmax = word.xmax
    sphrase.text = p                # all words linking to the subphrase are updated 
    sphrase.dialogFreq = fp         # TO-DO find frequency
    sphrase.phrase = phrase

    P+=p

    # Complete the data of current phrase and start new phrase
    if '4' in b.mark:
##        print(b)
##        print("PHRASE ", P)
        phrase.xmax = word.xmax
        phrase.text = P
        phrase.dialogFreq = fP
        IP+=1
        P = []
        phrs.items.append(phrase)
        phrase = Phrase(word.xmax, '', IP, [], None)
        ip = 0
   
    # Start new subphrase
    ip+=1
    sphrs.items.append(sphrase)    
    sphrase = Subphrase(word.xmin, '', ip, [], None)
    p=[]
    prev = cur
tg_main.fill_tier(words)
##tg_main.append(phrs)
##tg_main.append(sphrs)

tg_main.writeGridToPath(source+'b.textgrid')
pickle.dump(tg_main, open(source+'b.pkl','wb'))

