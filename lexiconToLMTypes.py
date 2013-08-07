"""
lexiconToLMTypes.py
Takes a CMU-formatted lexicon and returns a lexicon using LM types instead of phones.
Example: Input: FOG  F AO G
Output: FOG  Fc Fr V Sc Sr
"""
import sys
# Require Python 3.x
if sys.version_info[0] < 3:
    print("Error: The TextGrid processor requires Python 3.0 or above. Exiting.\n")
    sys.exit(1)

def readLexicon(f):
	return {line.split()[0]: " ".join(line.strip("\n").split()[1:]) for line in f if not line.startswith(";;;")}

def convertToLM(dic):
	conversionTable = {}
	conversionTable.update({p: ["V"] for p in "aa ae ah ao aw ay eh ey ih iy ow oy uh uw".split()})
	conversionTable.update({p: "Sc Sr".split() for p in "b p t d k g".split()})
	conversionTable.update({p: "Fc Fr".split() for p in "f v th dh s z sh zh ".split()})
	conversionTable.update({p: ["G"] for p in "l er r w y hh".split()})
	conversionTable.update({p: "Sc Sr Fc Fr".split() for p in "jh ch".split()})
	conversionTable.update({p: "Nc Nr".split() for p in "m n ng".split()})
	for word in dic:
		translation = []
		for letter in dic[word].split():
			letter = letter.strip("012").lower()
			if letter in conversionTable:
				for transLetter in conversionTable[letter]:
					translation.append(transLetter)
			else:
				print("Letter not found in conversion table: "+letter)
		dic[word] = " ".join(translation)
	return dic

def saveDic(dic, fpath):
	outpath = ".".join(fpath.split(".")[:-1])+".landmark."+fpath.split(".")[-1]
	with open(outpath, "w") as f:
		for entry in dic:
			f.write(entry + "  " + dic[entry] + "\n")
	return "The file was saved to "+ outpath

if __name__ == "__main__":
	if len(sys.argv) == 2:
		fpath = sys.argv[1]
	f = None
	while not f:
		try:
			f = open(fpath, "r")
		except:
			fpath = input("Enter the path of the lexicon file: ")
	dic = readLexicon(f)
	dic = convertToLM(dic)
	print(saveDic(dic, fpath))