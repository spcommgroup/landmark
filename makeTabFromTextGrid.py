"""
Takes in a .TextGrid file, does all the preparations (which may require editing
the textgrid to fix bad landmarks), then returns the path of the output .tab file.
"""

"""
BEFORE YOU RUN, PLEASE READ:

 * FIRST, move your textgrid files to data/source folder. Work out of that folder.

REQUIRED TIER NAMES:
 * "words": interval tier with full words
 * either "landmarks" or "LM": point tier with t-cl style landmarks
 * either "LMmod" or "LMmods" or "comments": point tier with t-cl-x style landmarks 

NOTE: If a tier named "phones" exists, it will be renamed to "phones_prev" and a 
	  new, generated "phones" tier will be used.
"""

TEXTGRID_FILE = "conv12g_chelsea.TextGrid"

from ExtendedTextGrid import *
src = "data/source/" + TEXTGRID_FILE
print("Creating .tab from "+src+"...")
tg = ExtendedTextGrid(src)
tg.prepare()
tg.extractContext()
tg.saveTab()
print("Saved as "+tg.fname+".tab")

