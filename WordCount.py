import TGProcess
import pickle

source = "conv07_pb2a"


f = open(source+'.pkl','rb')
tg = pickle.load(f)
words = tg.get_tier('words')
wordContext = tg.get_tier('word-context')




def is_word(word):
    return not ('<' in word or '>' in word or word=='')

def findDialogFreq(words_tier):
    wordCount = {}
    total=0    
    for word in words_tier:
        text = word.text.lower().strip("\t \" +?.'[],")
        if is_word(text):
            if text in wordCount:
                wordCount[text]+=1.0
            else:
                wordCount[text]=1.0
            total+=1.0
    return dict([(wd, ct/total) for (wd, ct) in wordCount.items()])

def addDialogFreq(dialogFreq, wordContext_tier):
    for w in wordContext_tier:
        text = w.text.lower().strip("\t \" +?.'[],")
        if is_word(text):
            try:
                w.dialogFreq=dialogFreq[text]
            except:
                print('ERROR: ', w, '(index=',wordContext_tier.items.index(w),') not found in dialog frequency table.')


F = findDialogFreq(words)
addDialogFreq(F, wordContext)

pickle.dump(tg, open(source+'.pkl','wb'))
                


