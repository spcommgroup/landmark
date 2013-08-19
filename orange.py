print("Loading orange ..... "),
import Orange
print "DONE"
data = Orange.data.Table("data/source/Conv07_choi_20130228_final.tab")

# print "Attributes:", ", ".join(x.name for x in data.domain.features)
print "Class:", data.domain.class_var.name
# print "Data instances", len(data)

tree = Orange.classification.tree.TreeLearner(data)
print tree.to_string()