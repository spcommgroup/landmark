import pickle
import LMdicParser
 

"""
0. LMdicParser.LMdic maps phoneme transitions to landmarks
"""
predict_table = LMdicParser.LMdic

""" 1. Pronouncing Dictionary """
# Input Dictionary (pickled python dictionary, produced by LMdicParser.py)
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


# conversation 8
lexicon['st-'] = 'st- s t'
lexicon['ha-']='ha- ae1'
lexicon['crat-']='crat- k r ae1 t'
lexicon['ug-']='ug- ah1 g'
lexicon['ng-']='ng- ng'

### TO-DO: Complete dictionary entries for the remaining irregularly pronounced words


"""
3. Map phonemes to manner class
phn: string, a phoneme symbol as specified in cmudict.0.7a.symbols in CMU's pronouncing
dictionary files. Note that all vowels end with a number 0,1,or 2 indicating its stress.
Return a string representing the phoneme manner class of the phoneme
"""
# 9 total classes including '#' (silence)
vowel = ['aw','oy','ay','iy', 'ih', 'ey', 'eh', 'ae', 'aa', 'ao', 'ow', 'ah', 'uw', 'uh', 'rr', 'er', 'ex']
glide = ['r', 'l', 'w', 'y', 'hh']           #'w', 'y' =  semivowel? 'r', 'l' = liquid? 'hh' = aspirate?
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

lm_table_rev = {
    'Nc':['m-cl', 'n-cl', 'ng-cl'],
    'Nr':['m', 'n', 'ng'],
    'Fc':['f-cl', 'th-cl', 's-cl', 'sh-cl', 'v-cl', 'dh-cl', 'z-cl', 'zh-cl', 'ch1', 'jh1/dj1', 'j1', 'dh1'],
    'Fr':['f', 'th', 's', 'sh', 'v', 'dh', 'z', 'zh', 'ch2', 'jh2','dj2','j2'],
#    'Tn' : ['s-cl', 'sh-cl', 'z-cl', 'zh-cl'],
#    'Tf': ['s', 'sh', 'z', 'zh'],
    'Sc' : ['p-cl', 't-cl', 'k-cl', 'b-cl', 'd-cl', 'g-cl', 'ch-cl', 'jh/dj-cl', 'j-cl'],
    'Sr' : ['p', 't', 'k', 'b', 'd', 'g', 'ch1', 'jh1','dj1','j1', 'j'],
    'Gc' : ['w-cl', 'y-cl', 'r-cl', 'l-cl', 'h-cl'],
    'G' : ['w', 'y', 'r', 'l', 'h'],
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
##        else:
        lm_table[value]=key


"""
6. Alignment cost matrix (coming soon...)
"""

