#!/usr/bin/env python3

from TGProcess import * #TGProcess.py must be in the same directory as this file, \
                        # or in the Python modules directory, for this import to succeed.
import os #File path manipulation
import sys #Command line arguments
from operator import itemgetter
from math import sqrt

if len(sys.argv) < 2:
    exit("Usage: python duration.py /Path/To/File.TextGrid")
filepath = os.path.abspath(sys.argv[1])
t = TextGrid(filepath=filepath)

diffs = []
for tier in t:
    if tier.tierClass != "TextTier":
        continue #Only deal with TextTiers, not IntervalTiers
    for i in range(0,len(tier)-1): #-1 so we can look ahead without risking an IndexError
        if "t-cl" in tier[i].landmarkList() and "t" in tier[i+1].landmarkList():
                diffs.append(float(tier[i+1].time) - float(tier[i].time))

for diff in sorted(diffs):
    print(diff)

mean = sum(diffs)/len(diffs)
sd = sqrt(sum((x-mean)**2 for x in diffs)/len(diffs))
print("Mean: " + str(mean))
print("Std Dev: " + str(sd))
