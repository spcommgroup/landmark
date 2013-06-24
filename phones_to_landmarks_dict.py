
#Translates from ARPAbet (CMU-style) phones to choi-style landmark predictions
d = {
	"b":  ["b-cl",  "b"],
	"ch": ["ch-cl", "ch1", "ch2"],
	"d":  ["d-cl",  "d"],
	"dh": ["dh-cl", "dh"],
	"er": ["r",],
	"f":  ["f-cl",  "f"],
	"g":  ["g-cl",  "g"],
	"hh": ["h",],
	"jh": ["jh-cl", "jh1", "jh2"],
	"k":  ["k-cl",  "k"],
	"l":  ["l",],
	"m":  ["m-cl",  "m"],
	"n":  ["n-cl",  "n"],
	"ng": ["ng-cl", "ng"],
	"p":  ["p-cl",  "p"],
	"r":  ["r"],
	"s":  ["s-cl",  "s"],
	"sh": ["sh-cl", "sh"],
	"t":  ["t-cl",  "t"],
	"th": ["th-cl", "th"],
	"v":  ["v-cl",  "v"],
	"w":  ["w",],
	"y":  ["y",],
	"z":  ["z-cl",  "z"],
	"zh": ["zh-cl", "zh"]
}
d.update({v: ["V",] for v in "aa ae ah ao aw ay eh ey ih iy ow oy uh uw".split(" ")})