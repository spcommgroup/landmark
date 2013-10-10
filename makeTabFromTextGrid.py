"""
Takes in a .TextGrid file, does all the preparations (which may require editing
the textgrid to fix bad landmarks), then returns the path of the output .tab file.
"""

from ExtendedTextGrid import *
src = "data/source/conv09g_jessk.TextGrid"
print("Creating .tab from "+src+"...")
tg = ExtendedTextGrid(src)
tg.prepare()
tg.extractContext()
tg.saveTab()
print("Saved as "+tg.fname+".tab")

