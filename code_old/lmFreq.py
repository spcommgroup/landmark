from ExtendedTextGrid import *

tg=ExtendedTextGrid.readObject('conv07_121031.pkl')
out = open('silences.txt','w')
s=0

for w in tg[0]:
    if not is_word(w.text):
        if w.xmax - w.xmin < 0.5:
            print("SHORT:", w)
        else:
            s1, e1 = tg[6].findAsIndexRange(w.xmin, w.xmax, s)
            s2, e2 = tg[1].findAsIndexRange(w.xmin, w.xmax, s)
##            if s1!=e1:
##                print('act. LM:',w, tg[6][s1], tg[6][e1-1])
            if s2!=e2:
                print('Landmarks:',w, tg[1][s2], tg[1][e2-1])

n=sum([len(lm.mark.split('/')) for lm in tg[1]])
t=sum([(w.xmax-w.xmin)*(is_word(w.text)) for w in tg[0]])

print('Labeled landmarks:', n)
print('Total time:', tg.xmax-tg.xmin)
print( 'Effective time:', t)
print( 'LM frequency:', n/t)

                



        
        
        
        
