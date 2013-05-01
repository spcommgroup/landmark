### Landmark Predictor 1.0.3.1 ###
### Author: Minshu Zhan ###
### May 2012 ###
### - Modified for the removal of SyllableConstituent class ###


from TGProcess import *
from Context import *
import pickle


DELTA = 0.00001
SUBDELTA = 0.000001

# Input Files (.textgrid)
wordfiles = [
##            "conv01_landmarks_ssh-edits_3-11-09_no-auto-labels",
##             "conv02g_ym_fixed_lma_ssh_2-25-08-to-nmv",
##             "conv03g-or-5__ssh_9-11-08",
##             "conv04g_fixed_lma_7-24-07_ssh-3-28-08",
##             "conv05g_merged_1-complete",
##             "conv06g_ch_fixed",
##             "conv08gdmw",
             "conv07_temp"
             ]
    
## TO-DO: ADD USER PROMPT INTERFACE

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
Dictionary that maps phoneme class pairs to landmarks
"""
phn_trans_to_lm = pickle.load(open('LM_dic','rb'))

"""
Find the manner class for a given phoneme.
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
    

def is_voiced(phn):
    return not(phn in ['#', 'h', 'f', 'th', 's', 'sh', 'p', 't', 'k'])

def is_nasal(phn):
    return( phn in nasal)

def is_word(word):
    return not ('<' in word or '>' in word or word=='')


for source_file in wordfiles:
    print( "Processing file \"", source_file)

    # Main textgrid 
    tg = TextGrid(filepath=source_file+".textgrid")
    print(tg)
    text = tg.get_tier('words')


    # Initiate new textgrid tiers for predicted landmarks, phonemes, voicing, and nosal info
    lm_tier = LMTier(name="predicted LM", xmin = tg.xmin , xmax=text.xmax)
    phn_tier = IntervalTier(name="phoneme", xmin = tg.xmin, xmax=tg.xmax)
    g_tier = PointTier(name="glottal voicing", xmin = tg.xmin, xmax=tg.xmax)
    n_tier = PointTier(name="velopharyngeal", xmin = tg.xmin, xmax=tg.xmax)
    extword_tier = IntervalTier(name='word-context', xmin= tg.xmin, xmax=tg.xmax)


    # Main loop

    prev_phn = Phoneme(0, 0, None)

    for interval in text:
        word = interval.text.lower().strip("\t \" +?.'[],")
##        print(word)
        if not is_word(word):  # treat non-word as silence
            wd = Word(interval.xmin, interval.xmax, '')  
            cur_phn = Phoneme(interval.xmin, interval.xmax, wd)    # silent Phoneme interval    
            phn_tier.items.append(cur_phn)      # update "phoneme" tier
            
            if prev_phn.text!='#':   # generate LM point only when previous phoneme class is not silence
                pclass = phoneme_class(prev_phn.text)
                lm=phn_trans_to_lm[pclass]['#']
                lm_tier.insert(LMPoint(interval.xmin, lm, prev_phn, cur_phn)) # update "predicted LM" tier
                if is_voiced(prev_phn.text):
                    g_tier.insert(Point(interval.xmin, '-g'))
                if is_nasal(prev_phn.text):
                    n_tier.insert(Point(interval.xmin, '-n'))       
            prev_phn = cur_phn
            
        else:   # regular word
            try:
                phonemes=lexicon[word].split()[1:]      # keeps the phonemes only (DictEntry := WORD PHONEME+)
                duration = (interval.xmax-interval.xmin)/len(phonemes)    # duration of each phoneme
                # Construct Word instance
                wd = Word(interval.xmin, interval.xmax, word)


                # states of syllable constituent parser
                n = 0
                sn = 0
                prevType = ''
                
                for i in range(len(phonemes)):
                    phn = phonemes[i]
    ##                    print(phn)
                    if phn[-1] in '012': # vowel -> nucleus
                        t = 'n'
                    else:               # consonant 
                        if n==0:
                            t = 'o'
                        else:
                            t = 'a'
                    if prevType != t:
                        sn=0
                        if t=='n':
                            n+=1    
                    sn+=1                   
                    prevType = t

                    
                    # Construct new Phoneme instance
                    tphn= interval.xmin+i*duration   # start time of current phoneme
                    cur_phn = Phoneme(tphn, tphn+duration, wd, phn, phoneme_class(phn), t, n, sn)
                    phn_tier.items.append(cur_phn)  # update "phoneme" tier
                    
                    
                    if is_voiced(prev_phn.text) and not is_voiced(phn):
                        g_tier.insert(Point(tphn, mark='-g'))
                    elif is_voiced(phn) and not is_voiced(prev_phn.text):
                        g_tier.insert(Point(tphn, mark='+g'))
                    if is_nasal(prev_phn.text) and not is_nasal(phn):
                        n_tier.insert(Point(tphn, mark='-n'))
                    elif is_nasal(phn) and not is_nasal(prev_phn.text):
                        n_tier.insert(Point(tphn, mark='+n'))
                        
                    lm=phn_trans_to_lm[phoneme_class(prev_phn.text)][phoneme_class(phn)]
                    
                    if lm!='':
                        lm_tier.insert(LMPoint(tphn, lm, prev_phn, cur_phn))  # update "predicted LM" tier
                    prev_phn=cur_phn

                # Word's syllable count is # nucleus
                wd.syllableCount = n
                    
                # After parsing the word, determine 'c' (coda) by iterating through the word reversely
                i=-1
                end_phn = phn_tier[i]
                while end_phn.type == 'a':
                    end_phn.type = 'c'
                    i-=1
                    end_phn = phn_tier[i]                  
                            
            except:       # temporarily treat non-recognizable words as silences
                print('Cannot parse word interval:', interval)
                wd = Word(interval.xmin, interval.xmax, '')  
                cur_phn = Phoneme(interval.xmin, interval.xmax, wd)    # silence
                phn_tier.items.append(cur_phn)      # update "phoneme" tier
                prev_phn = cur_phn
        extword_tier.append(wd)


    tg.append(extword_tier)
    tg.append(lm_tier.splitLMs())
    tg.append(phn_tier)
    tg.append(g_tier)
    tg.append(n_tier)

# Output TextGrid File
    tg.writeGrid(open("conv07_p.textgrid",'w'))
    print("Saved ", tg)
# Output Context-rich Python TextGrid object file
    context = open("conv07_p.pkl", 'wb')
    pickle.dump(tg, context)
    context.close()

 
