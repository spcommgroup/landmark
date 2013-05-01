from TGProcess import *
import pickle

source = 'conv07_pb'
tg = pickle.load(open(source+".pkl", 'rb'))
##tg = TextGrid(filepath= 'conv07_temp_predicted.textgrid')

lms = tg.get_tier("landmarks")
comments = tg.get_tier("comments")

lms2 = PointTier("alt LM", 0, tg[0].xmax)

DELTA = 0.000001



##for lm in lms:
##    marks = lm.splitLM(10*DELTA, DELTA)
##    for m in marks:
##        new = m.convertLM()
##        lms2.insert(new)  
##
##
##for lm in comments: 
####    if 'ch1' in lm.mark or 'ch2' in lm.mark:
####        print('FRIC', lm.mark)
##    marks = lm.splitLM(10*DELTA, DELTA)
##    for m in marks:
##        new = m.convertLM()
##        lms2.insert(new)
##  




for lm in comments: 
##    if 'ch1' in lm.mark or 'ch2' in lm.mark:
##        print('FRIC', lm.mark)
    marks = lm.splitLM(10*DELTA, DELTA)
    for m in marks:
        new = m.convertLM()
        lms2.insert(new)
        
for lm in lms:
    marks = lm.splitLM(10*DELTA, DELTA)
    for m in marks:
        new = m.convertLM()
        lms2.insert(new)  

        

print("Converting glides...")
prev = Point(0, 'Gr')
for lm in lms2:
##    print("NEW", lm)
    if lm.mark == 'Gc':
        if prev.mark == 'Gr':
##            print("START ")
            prev = lm
##        else:   # TO-DO
##            print(" Consecutive glide closures found.")
##            raise Exception(" Consecutive glide closures found.")
    if lm.mark == 'Gr':
        if prev.mark == 'Gc':
            t = (lm.time+prev.time)/2
            lms2.insert(Point(t, 'G'))
##            print("ADD G to", t)
            lms2.remove(lm)
            lms2.remove(prev)
            prev = lm
##        else:
##            print(" Consecutive glide releases found.")
##            raise Exception(" Consecutive glide releases found.")

print("Extracting +/-g +/-n labels")
lms3 = PointTier("g/n", '0', tg.xmax)
for lm in lms2:
    if lm.mark in ['+g', '-g','+n','-n']:
##        print(lm)
        lms2.remove(lm)
        lms3.append(lm)

tg.append(lms2)
tg.append(lms3)
tg.writeGridToPath(source+"2.textgrid")
pickle.dump(tg, open(source+"2.pkl",'wb'))
