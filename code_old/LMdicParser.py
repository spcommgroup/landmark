import pickle 
"""
Generate a python dictionary that maps phenome class pairs
to predicted landmarks.

The input file follows the format:


# - g       (+g)
# - n       +g/+n/Nc
...


where the phenome pair and the prediction in each entry is seperated by tab(s).
Extra spaces and '\n' are allowed.
"""
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

import re

#source = "phn_trans_to_lm.txt"
source = "lm_prediction.txt"
table = open(source,'r')
classes = ['#','v','g','n','fu','fn','fs','s','a']
LMdic = {}
for c in classes:
    LMdic[c] = {}
    
##for line in table:
##    line = line.strip('\n')
##    if line!='':
##        entry = re.split('\s*//\s*', line)[0].split('\t')
##        print(entry)
##        f,a,t = entry[0].split()
##        if len(entry)>1:
##            lm = entry[1]
##        else:
##            lm = ''
##        if f not in classes or t not in classes:
##            print("Unknown phoneme class ", f)
##        else:
##            LMdic[f][t]=lm



# Parse time-augmented landmark prediction table
re_phn = '([#a-zA-Z]+)'
re_lm = '([a-zA-Z/,\s\+\-]*)'
pattern='\d*\.\s*'+re_phn+'\s*[-–]\s*'+re_phn+'\s*\['+re_lm+'\)\['+re_lm+'\)\s*'

for line in table:
    if line!='\n':
        m=re.match(pattern, line)
        prev_phn=m.group(1)
        succ_phn=m.group(2)
        if not prev_phn in classes:
            print("Unknown phoneme class ", prev_phn)
        if not succ_phn in classes:
            print("Unknown phoneme class ", succ_phn)
        prev_lms=m.group(3)
        succ_lms=m.group(4)
        LMdic[prev_phn][succ_phn]=[prev_lms, succ_lms]
##        print(LMdic[prev_phn][succ_phn])
        
    
    


