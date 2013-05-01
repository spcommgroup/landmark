import pickle
import re


""" 0. Pronouncing Dictionary """
# Input Dictionary (pickled python dictionary, produced by LexiconExtract.py)
lexicon_file = "lexicon"
lexicon = pickle.load(open(lexicon_file,'rb'))

## Adaptations of the lexicon for unusual pronounciations and absent entries in cmudict
# conversation 1
lexicon['do+you+have']='do+you+have d uw1 y uw1 hh ae1 v'
lexicon['leh-']= 'leh- l eh1'
lexicon['b---']='b--- b'
lexicon['b-']='b- b'
lexicon['-ottom']='-ottom aa1 t ah0 m'
lexicon["monument's"]=lexicon['monument']+' s'
lexicon["i'zh---"]='i\'zh--- ay1 zh'

# conversation 2
lexicon['waterhole']='waterhole w ao1 t er0 hh ow1 l'
lexicon['anywhere-']=lexicon['anywhere']
# (to be continued...)

# conversation 3
lexicon['i bet']='i_bet ay1 b eh1 t'
lexicon['kind of']='kind_of k ay1 n d ah1 v'
lexicon['r-']='r- r'
lexicon['left-']=lexicon['left']
lexicon['carved-']=lexicon['carved']
lexicon['to-']=lexicon['to']
lexicon['o']='o aa1'
lexicon['in the']='in_the ih1 n dh ah0'
lexicon['should i']='should_i sh uh1 d ay1'
lexicon['cur-']='cur-k ah1 r'
lexicon['and you']='and_you ae1 n d y uw1'
lexicon['mmm']='mmm m'

# conversation 4
lexicon['ha[ve']=lexicon['have']
lexicon['a-']='a- ah0'
lexicon['youv']='youv y uw1 v'
lexicon['okayv']='okayv ow2 k ey1 v'
lexicon['w-']='w- w'

# conversation 5
lexicon['(o)kay']='(o)kay ow0 k ey1'
lexicon['ap-']='ap ae1 p'
lexicon['hea-']='hea hh eh1'
lexicon['mm-']='mm m'

# conversation 7
lexicon['th-']='th- dh'
lexicon['canad-']=lexicon['canadian'][:-10]
lexicon['ri-']='ri- r ih1'
lexicon['mm']='mm m'
lexicon['g-']= 'g- g'
lexicon['markerr']=lexicon['marker']
lexicon['di-']='di- d ih0'
lexicon['it\'s-']=lexicon['it\'s']
lexicon['mhum']='mhum m h m'


# conversation 8
lexicon['st-'] = 'st- s t'
lexicon['ha-']='ha- ae1'
lexicon['crat-']='crat- k r ae1 t'
lexicon['ug-']='ug- ah1 g'
lexicon['ng-']='ng- ng'

### TO-DO: Complete dictionary entries for the remaining irregularly pronounced words


"""
1. Generate a python dictionary that maps phenome class pairs to predicted landmarks.
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


classes = ['#','v','g','n','fu','fn','fs','s','a']
predict_table = {}
for c in classes:
    predict_table[c] = {}
    
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
##            predict_table[f][t]=lm

##source = "phn_trans_to_lm.txt"
source = "lm_prediction.txt"
table = open(source,'rb')

phn_pattern = '('+'|'.join(classes)+')'
##lm_pattern = '|'.join(LMs+[',','\s','/'])
lm_pattern='.*'
re_phn = '([#a-zA-Z]+)'
re_lm = '([a-zA-Z/,\s\+\-]*)'     # temp: ignore spaces
pattern='\d*\.\s?'+phn_pattern+'\s?-\s?'+phn_pattern+'\s*\[('+lm_pattern+')\)\[('+lm_pattern+')\)'

while 1:
##for l in table.readlines():
    line = table.readline()
##    line = str(l)
    if line!='\n':
        print(line)
        m=re.match(pattern, line)
        prev_phn=m.group(1)
        succ_phn=m.group(2)
        if not prev_phn in classes:
            print("Unknown phoneme class ", prev_phn)
        if not succ_phn in classes:
            print("Unknown phoneme class ", succ_phn)
        prev_lms=m.group(3)
        succ_lms=m.group(4)
        predict_table[prev_phn][succ_phn]=[prev_lms, succ_lms]
        print(predict_table[prev_phn][succ_phn])
        
    


"""
3. Map phonemes to manner class
phn: string, a phoneme symbol as specified in cmudict.0.7a.symbols in CMU's pronouncing
dictionary files. Note that all vowels end with a number 0,1,or 2 indicating its stress.
Return a string representing the phoneme manner class of the phoneme
"""
# 9 total classes including '#' (silence)
vowel = ['aw','oy','ay','iy', 'ih', 'ey', 'eh', 'ae', 'aa', 'ao', 'ow', 'ah', 'uw', 'uh', 'rr', 'er', 'ex']
glide = ['r', 'l', 'w', 'y', 'h', 'hh']           #'w', 'y' =  semivowel? 'r', 'l' = liquid? 'hh' = aspirate?
nasal = ['n', 'm', 'ng']
##    fric = ['f' ,'v' ,'th', 'dh' ,'s' ,'z' ,'sh' ,'zh']   # splitted into fric_unmk, fric_nstr, and fric_str
fric_unmk= ['f' ,'v']
fric_nstr = ['dh','th']
fric_str= ['s' ,'z' ,'sh' ,'zh']
stop = ['p','t','k','b','d','g']
affr= ['ch', 'dj','jh']

def phoneme_class(phn):
    
##    SUBTYPES:
##    nasal_vowel = []
##    aspr_vowel = []
##    semi_vowel = ['y','w']
##    asp = ['h']  
##    liq = ['l','r']
##    syl_nasal = []

    if phn=='#': return '#'
    if phn[:-1] in vowel: return 'v'
    if phn in glide: return 'g'
    if phn in nasal: return 'n'
##    if phn in fric: return 'f'
    if phn in fric_unmk: return 'fu'
    if phn in fric_nstr: return 'fn'
    if phn in fric_str: return 'fs'    
    if phn in stop: return 's'
    if phn in affr: return 'a'
    print( "Cannot recognize the manner class of ", phn)
    

"""
4. Map phoneme to distinctive features
"""
def is_voiced(phn):
    return not(phn in ['#', 'h', 'f', 'th', 's', 'sh', 'p', 't', 'k'])

def is_nasal(phn):
    return( phn in nasal)

def is_word(word):
    return not ('<' in word or '>' in word or word=='')

"""
5. Map hand-label format landmarks to machine generated format
"""

##lm_table_rev = {
##    'Nc':['m-cl', 'n-cl', 'ng-cl'],
##    'Nr':['m', 'n', 'ng'],
##    'Fc':['f-cl', 'th-cl', 's-cl', 'sh-cl', 'v-cl', 'dh-cl', 'z-cl', 'zh-cl'],
##    'Fr':['f', 'th', 's', 'sh', 'v', 'dh', 'z', 'zh', 'ch2', 'jh2/dj2','j2','jh2'],
###    'Tn' : ['s-cl', 'sh-cl', 'z-cl', 'zh-cl'],
###    'Tf': ['s', 'sh', 'z', 'zh'],
##    'Sc' : ['p-cl', 't-cl', 'k-cl', 'b-cl', 'd-cl', 'g-cl', 'ch-cl', 'jh/dj-cl', 'j-cl', 'jh-cl'],
##    'Sr' : ['p', 't', 'k', 'b', 'd', 'g'],
##    'Sr/Fc':['ch1', 'jh1/dj1','j1', 'j','dh1','jh1'],
##    'Gc' : ['w-cl', 'y-cl', 'r-cl', 'l-cl', 'h-cl'],
##    'Gr' : ['w', 'y', 'r', 'l', 'h', 'l-rl', 'w-rl','y-rl', 'r-rl','h-rl'],
##    'V':['V'],
##    '+g':['+g'],
##    '-g':['-g'],
##    '+n':['+n'],
##    '-n':['-n'],
##    
##    }


lm_table_rev = {
    'Nc':['m-cl', 'n-cl', 'ng-cl'],
    'Nr':['m', 'n', 'ng'],
    'Fc':['f-cl', 'th-cl', 's-cl', 'sh-cl', 'v-cl', 'dh-cl', 'z-cl', 'zh-cl'],
    'Fr':['f', 'th', 's', 'sh', 'v', 'dh', 'z', 'zh', 'ch2', 'jh2/dj2','j2','jh2'],
#    'Tn' : ['s-cl', 'sh-cl', 'z-cl', 'zh-cl'],
#    'Tf': ['s', 'sh', 'z', 'zh'],
    'Sc' : ['p-cl', 't-cl', 'k-cl', 'b-cl', 'd-cl', 'g-cl', 'ch-cl', 'jh/dj-cl', 'j-cl', 'jh-cl'],
    'Sr' : ['p', 't', 'k', 'b', 'd', 'g'],
    'Sr/Fc':['ch1', 'jh1/dj1','j1', 'j','dh1','jh1'],
    'Gc' : ['w-cl', 'y-cl', 'r-cl', 'l-cl', 'h-cl'],
    'Gr' :[ 'l-rl', 'w-rl','y-rl', 'r-rl','h-rl'],
    'G':  ['w', 'y', 'r', 'l', 'h'],
    'V':['V'],
    '+g':['+g'],
    '-g':['-g'],
    '+n':['+n'],
    '-n':['-n'],
    
    }

lm_table={}
for key in lm_table_rev:
    for value in lm_table_rev[key]:
##        if value in lm_table:
##            lm_table[value].append(key)
##            print(lm_table[value])
##        else:
        lm_table[value]=key


"""
6. Alignment cost matrix 
"""
row = {}
for lm in [None]+LMs:
    row[lm]={}
cost=row.copy()
for lm in cost:
    cost[lm]=row

