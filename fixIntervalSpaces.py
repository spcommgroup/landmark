"""
fixIntervalSpaces.py
Runs the method fixIntervalSpaces on every interval tier on a given textgrid.
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
if len(sys.argv) == 2:
    try: 
        path = sys.argv[1]
        f = open(path)
        f.close()
    except IOError:
        path = pathFromInput()
else:
    path = pathFromInput()

tg = ExtendedTextGrid(path)
for tier in tg:
    if type(tier) == IntervalTier:
        print("running on tier "+tier.name)
        tier.fixIntervalSpaces()

tg.save()

print("Saved as "+tg.fname+".TextGrid.")