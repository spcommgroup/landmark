"""
generatePhonesTier.py
Reads a .textgrid file, looks for a tier named "words", and adds a tier named "Phones" with the predicted phones.
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

tg.save()

print("Saved as "+tg.fname+".TextGrid.")