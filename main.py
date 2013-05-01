from ExtendedTextGrid import *

# [Data Preparation]
# Define file path here
sourcetg = "C:\\Users\mz\Documents\\landmark\data\source\Conv07_choi_20130228_final.TextGrid"
sourcepd = "C:\\Users\mz\Documents\\landmark\data\source\conv07g_RS.TextGrid"
fname = "C:\\Users\mz\Documents\\landmark\data\Conv07_choi_20130228_final.TextGrid"

# Load file
tg = ExtendedTextGrid(f=sourcetg)
tg.saveAs(fname)
# Apply lexicon, predict landmarks, and unify landmark label format
tg.putPhns()
tg.predictLM()
tg.convertLM()
# Convert words tier to context-rich objects
tg.extendWords()
# Match landmarks with corresponding phones
tg.linkLMtoWords("pred. LM")
tg.linkLMtoWords("act. LM")
tg.linkLMtoPhones()
# Align predicted and observed landmarks
tg.alignLM()
# Adjust position of each predicted landmark to the aligned observed landmark 
lm_tier = tg.get_tier("pred. lm")
# Create a new tier to display landmark modifications
tg.append(lm_tier.aligned())

# Convert textgrid into table
tg.saveTab()

# DT Analysis

# 




