"""
Takes in a .TextGrid file, does all the preparations (which may require editing
the textgrid to fix bad landmarks), then returns the path of the output .tab file.
"""

from ExtendedTextGrid import *

tg = ExtendedTextGrid("data/source/SLI3122_CNREP_choi.TextGrid")
tg.prepare()
tg.extractContext()
tg.saveTab()

