import pickle
from Context import *

def writeAlignment(plm_tier, lm_tier, fname):
    """ Return the string representation of the aligned predicted and observed landmark sequences."""
    
    out = open(fname, 'w')
    out.write('MUTATION_TYPE\tEXPECTED_LM\tOBSERVED_LM\tEXPECTED_LM_TIME\tOBSERVED_LM_TIME\tFROM_PHONEME'+
              '\t~pos\t~accent?\tTO_PHONEME\t~pos\t~accent?\tFROM_WORD\t~pos\t~dialogFrequency\tTO_WORD\t~pos\t~dialogFrequency'+
              '\tFROM_SUBPHRASE\t~pos\tTO_SUBPHRASE\t~pos'+
              '\n'
              )
    print('Checking', len(plm_tier), 'predicted landmarks against', len(lm_tier), 'observed landmarks.')
    insertion = 0
    mutation = 0
    deletion = 0
    preserved = 0
    for lm in plm_tier:
##        try:
        if lm.counterLM==None:
            out.write('DELETION\t'+lm.mark+'\t\t'+str(lm.time)+'\t\t')
            deletion+=1
        else:
            if lm.counterLM.counterLM!=lm:
                print('WARNING: alignment breaks at', lm)

            if lm.mark!=lm.counterLM.mark:
                out.write('MUTATION\t'+lm.mark+'\t'+lm.counterLM.mark+'\t'+str(lm.time)+'\t'+str(lm.counterLM.time)+'\t')
                mutation+=1
            else:
                out.write('PRESERVED\t'+lm.mark+'\t'+lm.counterLM.mark+'\t'+str(lm.time)+'\t'+str(lm.counterLM.time)+'\t')
                preserved+=1
                
        out.write(lm.writeContext()+'\n')
            
##        except:
##            print('ERROR at', lm)
    print('Done writing',mutation, 'mutations and', deletion, 'deletions.')
    for lm in lm_tier:        
        try:
            if lm.counterLM==None:
                out.write('INSERTION\t\t'+lm.mark+'\t\t'+str(lm.time)+'\t')
                insertion+=1
        except:
            print('ERROR at', lm)
    print('Done writing', insertion, 'insertions.', preserved, 'landmarks are preserved.' )

            
                

def writeAlignmentContext(expected, actual, fname):
    """ Given two aligned landmark sequences, write the comparison result to file specified by fname.
    All the following contextual are listed out for each mutation:
    
    MUTATION_TYPE EXPECTED_LM  EXPECTED_LM_TIME   OBSERVED_LM   OBSERVED_LM_TIME  ACCENT    FROM_PHONEME  -pos   TO_PHONEME  -pos   FROM_WORD   -pos
    TO_WORD -pos FROM_SUBPHRASE   -pos    TO_SUBPHRASE    -pos    FROM_PHRASE     -pos    TO_PHRASE   -pos      DIADLOGUE_WORD_FREQ
    
    """
    if len(expected)!= len(actual):
        raise Exception("Given landmark sequences do not have the same length!")

    out = open(fname, 'w')
    out.write('MUTATION_TYPE\tEXPECTED_LM\tOBSERVED_LM\tEXPECTED_LM_TIME\tOBSERVED_LM_TIME\tFROM_PHONEME'+
              '\t~pos\t~rev pos\t~accent?\tTO_PHONEME\t~pos\t~rev pos\t~accent?\tFROM_WORD\t~pos\t~dialogFrequency\tTO_WORD\t~pos\t~dialogFrequency'+
              '\tFROM_SUBPHRASE\t~pos\tTO_SUBPHRASE\t~pos'+
              '\tFROM_PHRASE\t~pos\tTO_PHRASE\t~pos\n'
              )

    for i in range(len(expected)):
        if lm.counterLM==None:   #insertion
            out.write('INSERTION\t\t'+actual[i].mark+'\t\t'+str(actual[i].time)+'\t')
            print("INSERTION!", actual[i])
##            out.write('INSERTION!'+str(actual[i]))
        elif actual[i]==None:
            out.write('DELETION\t'+expected[i].mark+'\t'+str(expected[i].time)+'\t\t')
            out.write(expected[i].writeContext())
        elif expected[i].mark!=lm.counterLM.mark:
            out.write('MUTATION\t'+expected[i].mark+'\t'+actual[i].mark+'\t'+str(expected[i].time)+'\t'+str(actual[i].time)+'\t')
            out.write(expected[i].writeContext())
        else:
            out.write('PRESERVED\t'+expected[i].mark+'\t'+actual[i].mark+'\t'+str(expected[i].time)+'\t'+str(actual[i].time)+'\t')
        out.write('\n')


source = "conv07_pb1a"
tg = pickle.load(open(source+'.pkl','rb'))
writeAlignment(tg.get_tier('splitted lm'), tg.get_tier('alt lm'), source+'_summary.txt')
