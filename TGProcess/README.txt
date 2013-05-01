TGProcess – Praat TextGrid File Reading, Writing and ProcessingVersion 1.0.0For Use With Python Version 3.2.1 (See Issues/Improvements)INTRODUCTION==================================================================The phonetics software Praat saves data in .TextGrid files, using a custom TextGrid file format.  The TGProcess module provides a parser for the TextGrid file format and some tools for manipulating, analyzing and exporting TextGrid data.EXAMPLES OF POSSIBLE USES=====================================================	The TGProcess module is intended to be a versatile tool for TextGrid data handling and analysis.  Some examples of programs that could be built on top of TGProcess are:	Tier-specific or context-specific find-and-replace programs.	Data profilers that determine the frequency with which sequences or types of landmarks occur.	Programs that predict landmarks sequences based on the words tier (using an external algorithm), then compare those predictions to the landmarks in a certain tier.	Programs that analyze a sound file (using an external algorithm), automatically generate a tier of landmarks, and optionally compare those landmarks to the landmarks in a certain tier.
	It should be noted that, while some of the above examples are very difficult, they are made easier by the functionality provided by TGProcess.

EXAMPLE CODE==================================================================
The best way to become familiar with the TGProcess module is to examine the liberally commented source code of TGProcess.py and the example scripts.
To run the example scripts, make sure they are located in the same directory as TGProcess.py, then execute "python [scriptname.py] /Path/To/File.TextGrid", replacing [scriptname.py] with the name of the script.  For example: "python duration.py /Users/J/Desktop/Conv01.TextGrid".  Be sure you have Python 3.2.1 or later installed (see Issues/Improvements).

Module Source Code:
TGProcess.py
	*Module source code.

Example Scripts:
duration.py
	*Tabulates the time between all "t-cl" occurrences and their subsequent "t" occurrences.
	*Demonstrates accessing Points by taking slices of the Tier instance, rather than by taking slices of the Tier.items instance variable.
	*Demonstrates use of Point.landmarkList()

countLM.py
	*Counts the number of occurrences of each landmark (or other text) in each TextTier of a TextGrid.
	*Demonstrates simple looping techniques.
	*Demonstrates accessing Points by taking slices of the Tier instance, rather than by taking slices of the Tier.items instance variable.
	*Demonstrates use of Point.landmarkList()

moveLM.py
	*Moves select landmarks from select TextTiers to a destination tier.
	*Demonstrates modification of Points.
	*Demonstrates addition and deletion of Points to Tiers.
	*Demonstrates addition of Tiers to TextGrids.

toCSV.py
	*Writes the contents of a Tier to a .csv (Excel) file.

One useful technique that was not demonstrated in the above examples is expansion/modification of the classes.  For example, if one wishes to perform some analysis of the general "manner of articulation" category of landmarks, one could simply write a script to loop through all points in a tier, and for each point p, look up the manner of p.mark and set p.manner = manner(p.mark).  For more advanced alterations, one could subclass TextGrid, Tier, Interval or Point.

SUMMARY OF TGPROCESS==========================================================
	This section is intended to provide a quick summary of the TGProcess module.  Readers are advised to consult the liberally commented source code of TGProcess.py and the example scripts to gain additional familiarity with the module.

	The TGProcess module defines the following classes for storing TextGrid data.  Listed under each class are relevant comments and several noteworthy methods.
	
-TextGrid
	*Top-Level class.  Stores instance variables for TextGrid metadata, and an array full of Tier() instances.
	*TextGrid.readGrid(self,f) reads all the data and metadata from the TextGrid file represented by f and stores it internally.
	*TextGrid.writeGrid(self,f) writes to f the TextGrid that was stored internally, as a valid .TextGrid file.
	*TextGrid.listTiers(self) prints a multi-line listing of the tiers contained in self.
	*The instance variable TextGrid.tiers is a list of Tier() instances.  In many situations, "tg.tiers" can be accessed as "tg", that is, "tg[i]" is equivalent to "tg.tiers[i]", etc, where tg is an instance of TextGrid.

-Tier
	*Stores instance variables for Tier metadata, and an array full of Interval() or Point() instances.		
	*Tier.writeTier(self,f) helps TextGrid.writeGrid(self,f) perform its job.  It is not meant to be called in other contexts.
	*Tier has other methods for adding and removing intervals and points from Tier instances.  See source for details.
	*Tier.writeTierToPathAsCSV(self,filepath) writes the contents of the Tier to a CSV file (which can be opened in Microsoft Excel).
	*Similarly to the TextGrid object, "tr.items[i]" is equivalent to "tr[i]", etc, where tr is an instance of TextGrid.

-Interval:
	*Stores data for an individual interval.
	*No interesting methods.
	*Generally manipulated by accessing Interval.xmin, Interval.xmax, and interval.text.

-Point:
	*Stores data for an individual point
	*Defines Point.__lt__(self,other) so a list of Points (i.e. a TextTier) can be sorted by time.
	*Point.landmarkList(self) takes the mark variable of a point instance and produces a list of all slash-separated landmarks inside: e.g. "f/t-cl" gives ["f","t-c"]
	*Point.setMarkFromList(self,list) takes a list of landmarks, such as those generated by Point.landmarkList(self), turns them into a slash-separated string, and sets that string as that point's mark.

ISSUES/IMPROVEMENTS===========================================================
	*TGProcess has only been tested on Python 3.2.1.  I believe it should work on all Python 3.x.x, but the CSV (Excel) exporter may be 3.2.1 specific, for now.  For functions that don't pertain to CSV: Praat files are encoded with varying Unicode encodings, which only Python 3 handles natively.  I'm looking into modules that will allow us to handle them on Python 2.  Until this is implemented, Python 3 is required.
	*The algorithms for adding Points and Intervals to Tiers currently run in O(n) time, but they can easily be reduced to O(log n).
	*I'm not sure that the naming conventions in TGProcess.py are the best.  If anyone has suggestions for changes of class of function names, please let me know!