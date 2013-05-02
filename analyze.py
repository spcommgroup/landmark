from ExtendedTextGrid import *
from matplotlib import *


g=ExtendedTextGrid.readObject('conv07b.pkl')

# min & max lm space
def distance_range(g):
    prev=0
    min_lm_space=min([tg[1][i].time-tg[1][i-1].time for i in range(1, len(tg[1]))])
    print(min_lm_space)

    # min distance to word boundary
    min_lm_word_dist=100000
    i=0
    for w in tg[0]:
        i,j = tg[1].findAsIndexRange(w.xmin, w.xmax, i)
        min_lm_word_dist=min(abs(tg[1][i].time-w.xmin), abs(w.xmax - tg[1][j-1].time))
        if min_lm_word_dist<0.000001:
            print(w)
    print(min_lm_word_dist)


# min distance to phoneme boundary

t= g.get_tier('act. lm')
def plot_distance(t):
    ds = [t[i]-t[i-1] for i in range(1,len(t))]
    
    




    
