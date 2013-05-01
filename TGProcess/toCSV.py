#!/usr/bin/env python3

from TGProcess import * #TGProcess.py must be in the same directory as this file, \
                        # or in the Python modules directory, for this import to succeed.
import os #File path manipulation
import sys #Command line arguments
from operator import itemgetter

if len(sys.argv) < 2:
    exit("Usage: python toCSV.py /Path/To/File.TextGrid")
filepath = os.path.abspath(sys.argv[1])
destpath = filepath + ".csv"

t = TextGrid(filepath=filepath)

t.listTiers()
print("Choose a tier number to transcribe as a CSV file.")
source = input("> ")

t[int(source)-1].writeTierToPathAsCSV(destpath)


