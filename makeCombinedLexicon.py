"""
makeCombinedLexicon.py
creates a combined lexicon out of all the _lexicon.txt files in matcher-data
"""

with open("../landmarks/matcher-data/conv_all_lexicon.txt", "a") as out:
    for i in range(1, 17):
        with open("../landmarks/matcher-data/conv{num:02d}g_lexicon.txt".format(num=i), "r") as inp:
            for line in inp:
                if not line.startswith(";;;"):
                    out.write(line)
