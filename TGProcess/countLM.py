#!/usr/bin/env python3

from TGProcess import * #TGProcess.py must be in the same directory as this file, \
                        # or in the Python modules directory, for this import to succeed.
import os #File path manipulation
import sys #Command line arguments
from operator import itemgetter

if len(sys.argv) < 2:
    exit("Usage: python countLM.py /Path/To/File.TextGrid")
filepath = os.path.abspath(sys.argv[1])
pathsplit = os.path.splitext(filepath)
destpath = pathsplit[0] + ".processed" + pathsplit[1]

t = TextGrid(filepath=filepath)

table = {} #table of landmarks and their occurence counts

for tier in t: #Note, this was easier than "for tier in t.tiers:"
    if tier.tierClass != "TextTier":
        continue #Only deal with TextTiers, not Intervaltiers
    for point in tier:
        for landmark in point.landmarkList():
            table[landmark] = table.get(landmark,0)+1

for mark, count in sorted(table.items(),key=itemgetter(1),reverse=True):
    print(str(count) + " -> " + mark)
