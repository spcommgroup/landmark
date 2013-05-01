### Landmark Predictor 1.0 ###
### Author: Minshu Zhan ###
### May 2012 ###


from TGProcess import *
import pickle



# Input Files (.textgrid)
wordfiles = [
            "conv01_landmarks_ssh-edits_3-11-09_no-auto-labels",
             "conv02g_ym_fixed_lma_ssh_2-25-08-to-nmv",
             "conv03g-or-5__ssh_9-11-08",
             "conv04g_fixed_lma_7-24-07_ssh-3-28-08",
             "conv05g_merged_1-complete",
             "conv06g_ch_fixed",
             "conv08gdmw",
             "yinmon07g_lm"
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



for source_file in wordfiles:
    print( "Processing file \"", source_file)

    """ Initiate TextGrid object"""
    tg = TextGrid()

    tg.readGridFromPath(source_file+".textgrid")
    for tier in tg:
        if 'word' in tier.name.lower() or 'conv' in tier.name.lower():
            text = tier
            break

    # Produce landmark textgrid tier
    prev_phn = '#'
    tier = Tier(name="predicted LM", xmax=text.xmax)
    phn_tier = Tier(tierClass="IntervalTier",name="phoneme", xmax=text.xmax)
    g_tier = Tier(name="glottal voicing", xmax=text.xmax)
    n_tier = Tier(name="velopharyngeal", xmax=text.xmax)

    for interval in text:
        word = interval.text.lower().strip("\t \" +?.'[],")
        if '<' in word or '>' in word or word=='':  # non-word = silence
            phn_tier.items.append(Interval(interval.xmin,interval.xmax,''))
##            print (interval.text)
            if prev_phn!='#':
                lm=phn_trans_to_lm[phoneme_class(prev_phn)]['#']
                tier.addPoint(Point(time= interval.xmin, mark=lm))
                if is_voiced(prev_phn):
                    g_tier.addPoint(Point(time= interval.xmin, mark='-g'))
                if is_nasal(prev_phn):
                    n_tier.addPoint(Point(time= interval.xmin, mark='-n'))       
            prev_phn='#'
            
        else:
            if word in lexicon:
                phonemes=lexicon[word].split()[1:] 
                duration = (float(interval.xmax)-float(interval.xmin))/len(phonemes)
                for i in range(len(phonemes)):
                    phn = phonemes[i]
                    phn_tier.items.append(Interval(str(float(interval.xmin)+i*duration),str(float(interval.xmin)+(i+1)*duration),phn))
                    if is_voiced(prev_phn) and not is_voiced(phn):
                        g_tier.addPoint(Point(time= str(float(interval.xmin)+i*duration), mark='-g'))
                    elif is_voiced(phn) and not is_voiced(prev_phn):
                        g_tier.addPoint(Point(time= str(float(interval.xmin)+i*duration), mark='+g'))
                    if is_nasal(prev_phn) and not is_nasal(phn):
                        n_tier.addPoint(Point(time= str(float(interval.xmin)+i*duration), mark='-n'))
                    elif is_nasal(phn) and not is_nasal(prev_phn):
                        n_tier.addPoint(Point(time= str(float(interval.xmin)+i*duration), mark='+n')) 
                    lm=phn_trans_to_lm[phoneme_class(prev_phn)][phoneme_class(phn)]
                    if lm!='':
                        tier.addPoint(Point(time= str(float(interval.xmin)+i*duration), mark=lm))
                    prev_phn=phn
            else:
                prev_phn = '#'          # temporarily treat non-recognizable words as silences

    tg.append(tier)
    tg.append(phn_tier)
    tg.append(g_tier)
    tg.append(n_tier)

# Output File (ended with "_predicted" suffix)
    tg.writeGrid(open(source_file+"_predicted.textgrid",'w'))

 
