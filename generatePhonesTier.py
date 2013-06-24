"""
generatePhonesTier.py
Reads a .textgrid file, looks for a tier named "words", and adds a tier named "Phones" with the predicted phones.
Update 6/24/13: Also optionally generates a landmark tier
"""
import sys
# Require Python 3.x
if sys.version_info[0] < 3:
    print("Error: The TextGrid processor requires Python 3.0 or above. Exiting.\n")
    sys.exit(1)

#This will crash on python 2.x so unfortunately it has to go below the version test
from ExtendedTextGrid import *

def pathFromInput():
    """returns the path of a .TextGrid file from user input"""
    f = False
    while not f:
        path = input("Enter TextGrid file path: ")
        if not path.lower().endswith(".textgrid"):
            print("File must end with .textgrid")
            continue
        try: 
            f = open(path)
            f.close()
        except IOError:
            print("File does not exist")
            continue
    return path

while 1: #Loop until putPhns() runs sucessfully, then break & save
    tg = ExtendedTextGrid(pathFromInput())
    try:
        tg.putPhns()
        break
    except Exception:
        print("There must be a tier named \"words\".")

lm = input("Do you want to generate a landmark tier (yes/no)? ").lower()
if lm=="yes" or lm=="y":
    import phones_to_landmarks_dict
    d = phones_to_landmarks_dict.d
    phonetier = tg.get_tier("phones")
    # Initiate new textgrid tiers for predicted landmarks, phonemes, voicing, and nosal info
    lmtier = PointTier(name="LM", xmin = 0, xmax=phonetier.xmax)
    
    for interval in phonetier:
        try:    
            # non-words
            phone = interval.text.lower().strip("\t \" +?.'[],012")     # ignore uncertainty marks
            if not ('<' in phone or '>' in phone or phone=='' or phone=="#"):    
                lms=d[phone]
                duration = (interval.xmax-interval.xmin)/len(lms)    # duration of each phoneme

                # Find phoneme positions
                n = 0
                sn = 0
                prevType = None
                
                for i in range(len(lms)):
                    lm = lms[i]
                    if len(lms)==1: #Single LM (V or glide)
                        i = .5 #Put LM in middle of phone
                    time_of_lm= interval.xmin+i*duration   # start time of current phoneme                                    
                    lm_point = Point(time_of_lm, lm)
                    lmtier.append(lm_point)    
        except KeyError:       # ignore (but print) unrecognized phones
            print('Cannot parse word interval:', interval.text)
    tg.append(lmtier)

tg.save()

print("Saved as "+tg.fname+".TextGrid.")